from abc import ABC, abstractmethod

from apps.products.enums import ProductStatusEnum


class ProductStateInterface(ABC):
    def __init__(self, product: "Product") -> None:
        self.product = product

    @abstractmethod
    def can_be_purchased(self) -> bool:
        pass

    @abstractmethod
    def next_state(self) -> ProductStatusEnum:
        pass
