from apps.products.enums import ProductStatusEnum
from apps.products.state_mashine.state_interface import ProductStateInterface


class OutOfStockState(ProductStateInterface):
    def can_be_purchased(self) -> bool:
        return False

    def next_state(self) -> ProductStatusEnum:
        if self.product.stock > 0:
            return ProductStatusEnum.LOW_STOCK
        return ProductStatusEnum.OUT_OF_STOCK
