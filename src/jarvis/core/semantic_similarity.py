
import math
from collections.abc import Sequence


def _validate_vector(vector: Sequence[float], name: str) -> None:
    """Validate that a vector contains finite numeric values."""
    if isinstance(vector, (str, bytes)) or not isinstance(
        vector, Sequence
    ):
        raise TypeError(f"{name} must be a sequence of numbers.")

    if not vector:
        raise ValueError(f"{name} cannot be empty.")

    for value in vector:
        if isinstance(value, bool) or not isinstance(
            value, (int, float)
        ):
            raise TypeError(
                f"Every value in {name} must be numeric."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"Every value in {name} must be finite."
            )


def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    _validate_vector(vector_a, "vector_a")
    _validate_vector(vector_b, "vector_b")

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding vectors must have the same dimensions."
        )

    dot_product = math.fsum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        math.fsum(value * value for value in vector_a)
    )
    magnitude_b = math.sqrt(
        math.fsum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError(
            "Embedding vectors cannot have zero magnitude."
        )

    similarity = dot_product / (magnitude_a * magnitude_b)

    # Avoid tiny floating-point rounding errors beyond [-1, 1].
    return max(-1.0, min(1.0, similarity))
