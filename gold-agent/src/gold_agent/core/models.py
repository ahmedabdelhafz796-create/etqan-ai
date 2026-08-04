"""Core data models for Gold Trading Analysis Agent."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """Trading actions."""
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


class StateType(str, Enum):
    """State machine states (§5.1 MASTER_PLAN)."""
    AUTONOMOUS = "autonomous"
    SAFE_MODE = "safe_mode"
    EMERGENCY = "emergency"
    MANUAL_RECOVERY = "manual_recovery"


class GateVerdictType(str, Enum):
    """Gate verdict types."""
    PASSED = "passed"
    BLOCKED = "blocked"


@dataclass
class MarketData:
    """Market data point (§6 MASTER_PLAN)."""
    timestamp: datetime
    xau_usd: float  # Gold price in USD
    dxy: float  # US Dollar Index
    bond_yield_10y: Optional[float] = None  # 10-year bond yield
    vix: Optional[float] = None  # Volatility Index
    data_quality: float = 1.0  # 0-1; confidence in data


@dataclass
class NewsItem:
    """News article."""
    timestamp: datetime
    title: str
    description: Optional[str]
    source: str
    url: Optional[str]
    sentiment: Optional[float] = None  # -1.0 to 1.0


@dataclass
class IndicatorValues:
    """Calculated technical indicators."""
    timestamp: datetime
    rsi: float  # 0-100
    macd: float  # MACD line value
    macd_signal: float  # Signal line
    macd_histogram: float  # MACD - Signal
    ma_short: float  # Short-term MA (50)
    ma_long: float  # Long-term MA (200)


@dataclass
class Score:
    """Weighted scoring result."""
    timestamp: datetime
    rsi_score: float  # 0-100
    macd_score: float  # 0-100
    ma_score: float  # 0-100
    news_score: Optional[float] = None  # 0-100
    macro_score: Optional[float] = None  # 0-100
    combined_score: float = 0.0  # Final 0-100
    signals_aligned: int = 0  # Number of aligned signals


@dataclass
class GateVerdict:
    """Result of a gate check."""
    verdict: GateVerdictType
    passed: bool
    reason: str
    details: Optional[dict] = None


@dataclass
class Decision:
    """Final decision with explanation (§7 MASTER_PLAN)."""
    timestamp: datetime
    action: ActionType
    confidence: float  # 0-100%
    reason: str
    indicators: IndicatorValues
    score: Score
    risk_gate_verdict: Optional[GateVerdict] = None
    sharia_gate_verdict: Optional[GateVerdict] = None
    llm_brain_used: bool = False
    state: StateType = StateType.AUTONOMOUS

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "indicators": {
                "rsi": self.indicators.rsi,
                "macd": self.indicators.macd,
                "ma_short": self.indicators.ma_short,
                "ma_long": self.indicators.ma_long,
            },
            "score": {
                "rsi_score": self.score.rsi_score,
                "macd_score": self.score.macd_score,
                "ma_score": self.score.ma_score,
                "combined_score": self.score.combined_score,
            },
            "risk_gate_passed": self.risk_gate_verdict.passed if self.risk_gate_verdict else None,
            "sharia_gate_passed": self.sharia_gate_verdict.passed if self.sharia_gate_verdict else None,
            "llm_brain_used": self.llm_brain_used,
            "state": self.state.value,
        }


@dataclass
class HealthStatus:
    """System health check result."""
    timestamp: datetime
    data_quality: float  # 0-1
    connection_status: str  # "healthy", "degraded", "down"
    last_data_age_minutes: float
    agent_errors_last_hour: int
    alerts_sent_today: int
    state: StateType
    requires_intervention: bool = False
    reason: Optional[str] = None


# ============================================================================
# TIER 1: EXECUTION ARCHITECTURE MODELS
# ============================================================================

class OrderStatus(str, Enum):
    """Order execution status."""
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    ERROR = "error"


class OrderType(str, Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class PositionSide(str, Enum):
    """Position direction."""
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass
class Order:
    """A single order to be executed."""
    order_id: str  # Unique order ID
    timestamp: datetime  # When order was created
    symbol: str  # Trading symbol (e.g., "XAUUSD")
    side: ActionType  # BUY or SELL
    quantity: float  # Amount to trade
    order_type: OrderType
    price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None  # For stop orders
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: Optional[float] = None
    rejection_reason: Optional[str] = None
    broker_order_id: Optional[str] = None  # Broker's order ID
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Trade:
    """A single opened trade (position)."""
    trade_id: str  # Unique trade ID
    entry_decision_id: int  # Links to decision that triggered entry
    symbol: str
    side: PositionSide
    entry_price: float
    quantity: float
    entry_timestamp: datetime
    entry_order_id: str  # Order that opened the trade

    # Position management
    current_price: Optional[float] = None
    current_p_l: Optional[float] = None  # Current profit/loss
    current_p_l_percent: Optional[float] = None  # Current P&L %

    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # Exit
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None
    exit_reason: Optional[str] = None  # "tp", "sl", "manual", "closed"
    exit_order_id: Optional[str] = None
    final_p_l: Optional[float] = None
    final_p_l_percent: Optional[float] = None

    # Metadata
    state: str = "open"  # "open", "closed", "error"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Position:
    """Current open position summary."""
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    entry_timestamp: datetime
    unrealized_p_l: float
    unrealized_p_l_percent: float
    trade_ids: list  # Trade IDs in this position
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class PortfolioMetrics:
    """Portfolio-level statistics."""
    timestamp: datetime
    total_value: float  # Total account value
    cash_balance: float
    positions_value: float
    unrealized_p_l: float
    realized_p_l_today: float
    max_drawdown_percent: float
    num_open_positions: int
    num_winning_trades_today: int
    num_losing_trades_today: int
    win_rate: float  # 0-1
    average_win: float
    average_loss: float
    risk_reward_ratio: float
    sharpe_ratio: Optional[float] = None
    max_leverage_used: float = 1.0
