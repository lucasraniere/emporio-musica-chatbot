"""Terminal chat with the Empório da Música agent."""

import argparse
import sqlite3
import uuid

from langgraph.checkpoint.sqlite import SqliteSaver
from rich.console import Console
from rich.markup import escape

from emporio.agent.graph import build_graph
from emporio.config import settings

console = Console()
ASSISTANT_NAME = "Clave"
EXIT_WORDS = {"sair", "exit", "quit"}


def answer(graph, thread_id: str, text: str) -> None:
    """Run one turn, printing each tool call as it happens and then the reply."""
    config = {"configurable": {"thread_id": thread_id}}
    for update in graph.stream({"messages": [("user", text)]}, config, stream_mode="updates"):
        for message in update.get("agent", {}).get("messages", []):
            for call in message.tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items())
                console.print(f"  [dim]↳ consultando {call['name']}({escape(args)})[/dim]")
            if message.text:
                console.print(
                    f"[bold magenta]{ASSISTANT_NAME}:[/bold magenta] {escape(message.text)}\n"
                )


def chat(graph, thread_id: str) -> None:
    console.print(
        f"[dim]Conversa {thread_id} | modelo {settings.llm_model}. "
        "Digite 'sair' para encerrar.[/dim]\n"
    )
    while True:
        try:
            text = console.input("[bold cyan]Você:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if text.lower() in EXIT_WORDS:
            break
        if not text:
            continue
        try:
            answer(graph, thread_id, text)
        # Deliberately broad: an API or rate-limit error must not end the chat.
        except Exception as error:  # noqa: BLE001
            console.print(
                f"[red]Não consegui responder agora ({type(error).__name__}). "
                "Tente de novo em instantes.[/red]\n"
            )
    console.print(f"[dim]Até mais! Para continuar depois: --thread {thread_id}[/dim]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat com a assistente da Empório da Música")
    parser.add_argument(
        "--thread", help="ID de uma conversa anterior, para continuar de onde parou"
    )
    args = parser.parse_args()

    if not settings.sqlite_path.exists() or not settings.chroma_dir.exists():
        console.print(
            "[red]Base de dados não encontrada. Rode antes:[/red]\n"
            "  uv run python -m emporio.ingest.build_db\n"
            "  uv run python -m emporio.ingest.build_index"
        )
        raise SystemExit(1)

    conn = sqlite3.connect(settings.checkpoint_path, check_same_thread=False)
    try:
        graph = build_graph(checkpointer=SqliteSaver(conn))
        chat(graph, args.thread or uuid.uuid4().hex[:8])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
