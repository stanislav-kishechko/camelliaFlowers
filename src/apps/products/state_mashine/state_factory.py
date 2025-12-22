from apps.products.enums import ProductStatusEnum
from apps.products.state_mashine.states.available_state import AvailableState
from apps.products.state_mashine.states.low_stock_state import LowStockState
from apps.products.state_mashine.states.out_of_stock_state import OutOfStockState

STATE_MAP = {
    ProductStatusEnum.AVAILABLE: AvailableState,
    ProductStatusEnum.LOW_STOCK: LowStockState,
    ProductStatusEnum.OUT_OF_STOCK: OutOfStockState,
}


def get_product_state(product):
    try:
        state_cls = STATE_MAP[product.status]
    except KeyError:
        raise ValueError(
            f"Unsupported product status: {product.status}. "
            f"Add it to STATE_MAP."
        )

    return state_cls(product)
