from functools import lru_cache
from emporio.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get the embeddings model."""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        encode_kwargs={"normalize_embeddings": True, "prompt" : "passage: "},
        query_encode_kwargs={"normalize_embeddings": True, "prompt" : "query: "},
    )


@lru_cache
def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=settings.chroma_collection,
        persist_directory=str(settings.chroma_dir),
        embedding_function=get_embeddings(),
    )
