from abc import ABC, abstractmethod
from typing import BinaryIO, List

from counter.domain.models import ObjectCount, Prediction


class ObjectDetector(ABC):
    @abstractmethod
    def predict(self, image: BinaryIO) -> List[Prediction]:
        """Object detection model predictions.

        Parameters
        ----------
        image : BinaryIO
            Image for object detection.

        Returns
        -------
        List[Prediction]
            Detected objects.
        """
        raise NotImplementedError


class ObjectCountRepo(ABC):
    @abstractmethod
    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Get objects count of given classes.

        Get all the objects count if no object_classes are given.

        Parameters
        ----------
        object_classes : List[str], optional
            Object classes, by default None

        Returns
        -------
        List[ObjectCount]
            Objects and their count.
        """
        raise NotImplementedError

    @abstractmethod
    def update_values(self, new_values: List[ObjectCount]):
        """Update objects count.

        Parameters
        ----------
        new_values : List[ObjectCount]
            Objects and their count.
        """
        raise NotImplementedError
