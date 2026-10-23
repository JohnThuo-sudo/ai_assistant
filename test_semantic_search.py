
from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.config.settings import load_settings
from jarvis.core.semantic_similarity import cosine_similarity


def main() -> None:
    settings = load_settings()
    provider = OllamaEmbeddingProvider(settings)

    memories = [
        "I enjoy developing software with Python.",
        "My favourite activity is playing football.",
        "I am building a personal AI assistant called Jarvis.",
        "I study database design and PostgreSQL.",
    ]

    query = "Which programming language do I enjoy using?"

    print("Generating query embedding...")
    query_vector = provider.embed(query)

    print("\nComparing query with saved-memory examples...\n")

    results = []

    for memory in memories:
        memory_vector = provider.embed(memory)

        score = cosine_similarity(
            query_vector,
            memory_vector,
        )

        results.append((score, memory))

    results.sort(key=lambda item: item[0], reverse=True)

    print(f"Query: {query}\n")

    for rank, (score, memory) in enumerate(results, start=1):
        print(f"{rank}. Similarity: {score:.4f}")
        print(f"   Memory: {memory}\n")


if __name__ == "__main__":
    main()
