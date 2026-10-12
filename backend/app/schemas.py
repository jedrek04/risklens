from typing import List

from pydantic import BaseModel, Field, model_validator


class PortfolioAsset(BaseModel):
    ticker: str
    weight: float = Field(gt=0, le=1)


class PortfolioRequest(BaseModel):
    portfolio: List[PortfolioAsset] = Field(min_length=1)
    days: int = Field(default=365, ge=150, le=4000)
    horizon: int = Field(default=10, ge=1, le=90)

    @model_validator(mode="after")
    def validate_weights(self):
        total = sum(a.weight for a in self.portfolio)

        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"Portfolio weights must sum to 1.0, got {total}")

        return self
