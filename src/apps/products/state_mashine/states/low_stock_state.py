from apps.products.enums import ProductStatusEnum
from apps.products.state_mashine.state_interface import ProductStateInterface


class LowStockState(ProductStateInterface):
    def can_be_purchased(self) -> bool:
        return self.product.stock > 0

    def next_state(self) -> ProductStatusEnum:
        if self.product.stock == 0:
            return ProductStatusEnum.OUT_OF_STOCK
        if self.product.stock > 5:
            return ProductStatusEnum.AVAILABLE
        return ProductStatusEnum.LOW_STOCK
