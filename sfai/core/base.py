from abc import ABC, abstractmethod
from typing import Dict, Any
from sfai.core.response_models import BaseResponse


class BaseApp(ABC):
    """
    Abstract base class for all provider implementations.
    Ensures a consistent interface for deployment operations.
    """

    @abstractmethod
    def init(self, **kwargs) -> BaseResponse:
        pass


class BasePlatform(ABC):
    @abstractmethod
    def init(self, **kwargs) -> BaseResponse:
        pass

    @abstractmethod
    def deploy(self, context: Dict[str, Any], **kwargs) -> BaseResponse:
        pass

    @abstractmethod
    def delete(self, context: Dict[str, Any]) -> BaseResponse:
        pass

    @abstractmethod
    def open(self, context: Dict[str, Any], **kwargs) -> BaseResponse:
        pass

    @abstractmethod
    def status(self, context: Dict[str, Any]) -> BaseResponse:
        pass

    @abstractmethod
    def logs(self, context: Dict[str, Any]) -> BaseResponse:
        pass


class BaseIntegration(ABC):
    @abstractmethod
    def publish(self, **kwargs) -> BaseResponse:
        pass
