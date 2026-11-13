import re
import shutil

import pymupdf4llm
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

from emporio.config import settings

HEADERS = [("#", "title"), ("##", "section"), ("###", "subsection")]

NOISE = re.compile(
    r"^(Página \d+|\*\*Empório da Música\*\* Manual de Políticas e Procedimentos)\s*$",
    re.MULTILINE,
)
BOLD_HEADER = re.compile(r"^(#+) \*\*(.+?)\*\*\s*$", re.MULTILINE)

def get_embeddings() -> HuggingFaceEmbeddings:
    """Get the embeddings model."""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        encode_kwargs={"normalize_embeddings": True, "prompt" : "passage: "},
        query_encode_kwargs={"normalize_embeddings": True, "prompt" : "query: "},
    )


def pdf_to_markdown() -> str:
    """Convert the PDF to Markdown."""
    md = pymupdf4llm.to_markdown(str(settings.policies_path))
    md = NOISE.sub("", md)
    md = BOLD_HEADER.sub(r"\1 \2", md)
    return re.sub(r"\n{3,}", "\n\n", md)


def split_sections(md: str) -> list[Document]:
    splitter = MarkdownHeaderTextSplitter(HEADERS, strip_headers=True)
    docs = []
    for i, chunk in enumerate(splitter.split_text(md)):
        path = [chunk.metadata[key] for _, key in HEADERS[1:] if key in chunk.metadata]
        breadcrumb = " > ".join(path) or "Capa e contato"
        docs.append(
            Document(
                id=f"policy-{i:02d}",
                # The breadcrumb gives a short section its context when embedded.
                page_content=f"{breadcrumb}\n\n{chunk.page_content.strip()}",
                metadata={"source": settings.policies_filename, "breadcrumb": breadcrumb},
            )
        )
    return docs


def build() -> None:
    docs = split_sections(pdf_to_markdown())

    shutil.rmtree(settings.chroma_dir, ignore_errors=True)
    Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=settings.chroma_collection,
        persist_directory=str(settings.chroma_dir),
    )

    for doc in docs:
        print(f"{doc.id}  {len(doc.page_content):>5} chars  {doc.metadata['breadcrumb']}")


if __name__ == "__main__":
    build()
    print(f"Index written to {settings.chroma_dir}")
