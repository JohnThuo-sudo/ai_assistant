
import unittest

from jarvis.core.semantic_similarity import cosine_similarity


class TestCosineSimilarity(unittest.TestCase):
    def test_identical_direction_returns_one(self):
        result = cosine_similarity([1, 2, 3], [1, 2, 3])
        self.assertAlmostEqual(result, 1.0)

    def test_same_direction_different_magnitude_returns_one(self):
        result = cosine_similarity([1, 2], [2, 4])
        self.assertAlmostEqual(result, 1.0)

    def test_perpendicular_vectors_return_zero(self):
        result = cosine_similarity([1, 0], [0, 1])
        self.assertAlmostEqual(result, 0.0)

    def test_opposite_direction_returns_negative_one(self):
        result = cosine_similarity([1, 0], [-1, 0])
        self.assertAlmostEqual(result, -1.0)

    def test_different_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            cosine_similarity([1, 2], [1, 2, 3])

    def test_empty_vector_is_rejected(self):
        with self.assertRaises(ValueError):
            cosine_similarity([], [])

    def test_zero_magnitude_vector_is_rejected(self):
        with self.assertRaises(ValueError):
            cosine_similarity([0, 0], [1, 2])

    def test_non_numeric_values_are_rejected(self):
        with self.assertRaises(TypeError):
            cosine_similarity([1, "two"], [1, 2])

    def test_boolean_values_are_rejected(self):
        with self.assertRaises(TypeError):
            cosine_similarity([True, 1], [1, 1])

    def test_infinite_values_are_rejected(self):
        with self.assertRaises(ValueError):
            cosine_similarity([float("inf"), 1], [1, 1])


if __name__ == "__main__":
    unittest.main()
