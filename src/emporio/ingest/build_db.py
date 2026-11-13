import json
import sqlite3

import pandas as pd

from emporio.config import settings

PIX_DISCOUNT = 0.05  # policy manual

SCHEMA = """
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);
CREATE TABLE products (
    product_id     INTEGER PRIMARY KEY,
    name           TEXT NOT NULL,
    category_id    INTEGER NOT NULL REFERENCES categories(category_id),
    description    TEXT,
    price_brl      REAL NOT NULL CHECK (price_brl > 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    status         TEXT NOT NULL CHECK (status IN ('active', 'discontinued', 'coming_soon')),
    specs          TEXT,  -- JSON
    created_at     TEXT
);
CREATE TABLE promotions (
    promotion_id     INTEGER PRIMARY KEY,
    product_id       INTEGER NOT NULL REFERENCES products(product_id),
    discount_percent REAL NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
    description      TEXT,
    is_active        INTEGER NOT NULL CHECK (is_active IN (0, 1))
);
CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    phone        TEXT,
    phone_digits TEXT,  -- normalized, for identity checks
    email        TEXT,  -- lowercased
    city         TEXT
);
CREATE TABLE orders (
    order_id           INTEGER PRIMARY KEY,
    customer_id        INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date         TEXT NOT NULL,
    status             TEXT NOT NULL,
    total_brl          REAL NOT NULL,
    payment_method     TEXT,
    tracking_code      TEXT,
    estimated_delivery TEXT,
    notes              TEXT
);
CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);
"""

CATALOG_VIEW = f"""
CREATE VIEW product_catalog AS
WITH best_promo AS (
    SELECT product_id, discount_percent, description,
           ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY discount_percent DESC) AS rn
    FROM promotions
    WHERE is_active = 1
)
SELECT
    p.product_id,
    p.name,
    c.name AS category,
    p.description,
    p.specs,
    p.status,
    p.stock_quantity,
    (p.status = 'active' AND p.stock_quantity > 0) AS is_available,
    p.price_brl AS list_price_brl,
    bp.discount_percent,
    bp.description AS promotion_name,
    ROUND(p.price_brl * (1 - COALESCE(bp.discount_percent, 0) / 100.0), 2) AS final_price_brl,
    -- PIX discount does not stack with a promotion (section 6.2)
    CASE WHEN bp.product_id IS NULL
         THEN ROUND(p.price_brl * (1 - {PIX_DISCOUNT}), 2) END AS pix_price_brl
FROM products p
JOIN categories c ON c.category_id = p.category_id
LEFT JOIN best_promo bp ON bp.product_id = p.product_id AND bp.rn = 1;
"""


def read_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(settings.data_dir / f"{name}.csv")
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    df[text_cols] = df[text_cols].apply(lambda col: col.str.strip())
    return df


def load_tables() -> dict[str, pd.DataFrame]:
    products = read_csv("products")
    products["specs"].map(json.loads)  # fail loudly on malformed JSON

    customers = read_csv("customers")
    customers["email"] = customers["email"].str.lower()
    customers["phone_digits"] = customers["phone"].str.replace(r"\D", "", regex=True)

    return {
        "categories": read_csv("categories"),
        "products": products,
        "promotions": read_csv("promotions"),
        "customers": customers,
        "orders": read_csv("orders"),
        "order_items": read_csv("order_items"),
    }


def build() -> None:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.unlink(missing_ok=True)

    tables = load_tables()
    with sqlite3.connect(settings.sqlite_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="append", index=False)
        conn.executescript(CATALOG_VIEW)

        for name in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            print(f"{name:<12} {count:>4} rows")
    conn.close()


if __name__ == "__main__":
    build()
    print(f"Database written to {settings.sqlite_path}")
