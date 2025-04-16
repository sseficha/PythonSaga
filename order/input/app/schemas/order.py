from pydantic import BaseModel, Field


class OrderIn(BaseModel):
    user_id: int

    class OrderItems(BaseModel):
        item_id: int
        quantity: int = Field(gt=0)
        price_per_unit: float = Field(gt=0)

    items: list[OrderItems]
