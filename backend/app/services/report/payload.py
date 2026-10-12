from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas import PortfolioInput


class Loose(BaseModel):
    model_config = ConfigDict(extra="ignore")


class FanChart(Loose):
    p5: list[float]
    p95: list[float]


class RiskPortfolio(Loose):
    var: float
    cvar: float
    volatility: float
    fan_chart: FanChart


class RiskMeta(Loose):
    days: int
    horizon: int
    n_sim: int
    confidence: float


class GarchInfo(Loose):
    converged: bool


class DailyVol(Loose):
    current: float


class RiskAsset(Loose):
    ticker: str
    weight: float
    annualized_vol: float
    volatility: DailyVol
    garch: GarchInfo


class Correlation(Loose):
    tickers: list[str]
    matrix: list[list[float]]


class RiskResult(Loose):
    meta: RiskMeta
    portfolio: RiskPortfolio
    assets: list[RiskAsset]
    correlation: Correlation


class AnomalySummary(Loose):
    anomalies: int
    scored_days: int
    latest_date: str
    latest_is_anomaly: bool


class AnomalyDay(Loose):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date: str
    daily_return: float = Field(alias="return")


class AnomalySeries(Loose):
    name: str
    summary: AnomalySummary
    anomalies: list[AnomalyDay]


class AnomalyMeta(Loose):
    days: int


class AnomalyResult(Loose):
    meta: AnomalyMeta
    portfolio: AnomalySeries
    assets: list[AnomalySeries]


class SentimentShare(Loose):
    positive: float
    negative: float


class SentimentAsset(Loose):
    ticker: str
    status: str
    headlines: int
    score: float | None = None
    label: str | None = None
    share: SentimentShare | None = None


class SentimentMeta(Loose):
    window_days: int
    min_headlines: int


class SentimentResult(Loose):
    meta: SentimentMeta
    assets: list[SentimentAsset]


class ReportRequest(PortfolioInput):
    risk: RiskResult
    anomalies: AnomalyResult | None = None
    sentiment: SentimentResult | None = None
