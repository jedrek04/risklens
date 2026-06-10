from pydantic import BaseModel, Field, model_validator
from typing import List


class PortfolioAsset(BaseModel):
    ticker: str
    weight: float = Field(gt=0, le=1)


class PortfolioRequest(BaseModel):
    portfolio: List[PortfolioAsset]
    days: int = 365
    horizon: int = 10

    @model_validator(mode="after")
    def validate_weights(self):
        total = sum(a.weight for a in self.portfolio)

        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"Portfolio weights must sum to 1.0, got {total}")

        return self