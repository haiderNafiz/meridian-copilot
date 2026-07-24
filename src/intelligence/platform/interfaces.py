from typing import Protocol, TypeVar
from .contracts import BaseRequest, BaseResponse

TRequest = TypeVar("TRequest", bound=BaseRequest, contravariant=True)
TResponse = TypeVar("TResponse", bound=BaseResponse, covariant=True)

class ProviderProtocol(Protocol[TRequest, TResponse]):
    def infer(self, request: TRequest) -> TResponse:
        """Executes the provider-specific semantic inference or lookup."""
        ...

class ServiceProtocol(Protocol[TRequest, TResponse]):
    def process(self, request: TRequest) -> TResponse:
        """Coordinates execution through provider strategies."""
        ...
