from typing import List

from pydantic import BaseModel, Field, model_validator


class PortfolioAsset(BaseModel):
    ticker: str
    weight: float = Field(gt=0, le=1)


class PortfolioInput(BaseModel):
    portfolio: List[PortfolioAsset] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_portfolio(self):
        tickers = [a.ticker for a in self.portfolio]
        if len(set(tickers)) != len(tickers):
            raise ValueError("Duplicate tickers in portfolio")

        total = sum(a.weight for a in self.portfolio)
        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"Portfolio weights must sum to 1.0, got {total}")

        return self


class PortfolioRequest(PortfolioInput):
    days: int = Field(default=730, ge=150, le=4000)
    horizon: int = Field(default=10, ge=1, le=90)
    n_sim: int = Field(default=10000, ge=1000, le=100000)


class AnomalyRequest(PortfolioInput):
    days: int = Field(default=365, ge=30, le=4000)
