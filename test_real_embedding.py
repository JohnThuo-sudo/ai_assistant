
from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.config.settings import load_settings


def main() -> None:
    settings = load_settings()
    provider = OllamaEmbeddingProvider(settings)

    text = "I enjoy developing software with Python."

    print("Generating embedding...")
    vector = provider.embed(text)

    print(f"Model: {provider.model}")
    print(f"Input: {text}")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 10 values: {vector[:10]}")
    print(f"All values are finite: {all(map(lambda x: abs(x) < float('inf'), vector))}")


if __name__ == "__main__":
    main()
