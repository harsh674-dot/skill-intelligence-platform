from abc import ABC, abstractmethod


class LearningAdapter(ABC):
    """
    Common interface for learning-resource providers
    such as iGOT, TPAC, or an internal catalogue.
    """

    @abstractmethod
    def get_courses(self) -> list[dict]:
        """
        Return learning resources in a common format.
        """
        raise NotImplementedError