import requests
from config import OLLAMA_HOST, EMBED_MODEL


def embed(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]
