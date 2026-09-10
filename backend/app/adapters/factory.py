from app.adapters.learning_adapter import LearningAdapter
from app.adapters.mock_learning_adapter import MockLearningAdapter


def get_learning_adapter(source: str = "mock") -> LearningAdapter:
    """
    Return the learning-resource adapter for the requested source.

    Supported sources:
    - mock
    """

    if source == "mock":
        return MockLearningAdapter()

    raise ValueError(
        f"Unsupported learning provider: {source}"
    )