"""Configuration management for Gold Trading Analysis Agent."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class DataConfig(BaseModel):
    market_provider: str = "mock"
    news_provider: str = "mock"
    symbols: Dict[str, str] = Field(default_factory=dict)
    update_interval_minutes: int = 60


class IndicatorConfig(BaseModel):
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    ma_short: int = 50
    ma_long: int = 200


class ScoringConfig(BaseModel):
    rsi_weight: float = 0.30
    macd_weight: float = 0.35
    ma_weight: float = 0.35
    news_weight: float = 0.20
    macro_weight: float = 0.15
    confidence_threshold_act: float = 65.0
    confidence_threshold_wait: float = 50.0
    confidence_threshold_conflict: float = 40.0


class BrainConfig(BaseModel):
    provider: str = "mock"
    model: str = "claude-sonnet-5"
    temperature: float = 0.7
    max_tokens: int = 200
    timeout_seconds: int = 30
    fallback_to_rule_engine: bool = True


class FallbackEngineConfig(BaseModel):
    enabled: bool = True
    conservative_confidence_reduction: float = 0.10
    min_indicator_agreement: int = 3


class RiskGateConfig(BaseModel):
    enabled: bool = True
    max_drawdown_percent: float = 5.0
    max_position_size_percent: float = 2.0
    daily_loss_limit_percent: float = 3.0
    max_consecutive_losses: int = 5
    data_quality_threshold: float = 0.95
    market_volatility_limit_vix: float = 40.0


class ShartiaConfig(BaseModel):
    enabled: bool = True
    school: str = "hanafi"
    audit_log_enabled: bool = True
    rules_file: str = "config/sharia_rules.yaml"


class NotificationConfig(BaseModel):
    primary_channel: str = "console"
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_enabled: bool = True
    console_enabled: bool = True
    console_language: str = "ar"


class ExecutionConfig(BaseModel):
    enabled: bool = False
    kill_switch_required: bool = True
    kill_switch_armed: bool = True
    broker: str = "mock"


class StateMachineConfig(BaseModel):
    initial_state: str = "autonomous"
    safe_mode_data_quality_threshold: float = 0.95
    emergency_drawdown_threshold: float = 0.15
    emergency_connection_timeout_seconds: int = 300


class AuditConfig(BaseModel):
    database_type: str = "sqlite"
    sqlite_path: str = "data/gold_agent.db"
    sharia_audit_log_enabled: bool = True
    decision_log_enabled: bool = True
    retention_days: int = 730


class BacktestConfig(BaseModel):
    enabled: bool = True
    initial_capital: float = 100000.0
    slippage_percent: float = 0.10
    commission_percent: float = 0.05
    start_date: str = "2023-01-01"
    end_date: str = "2024-12-31"


class Config(BaseModel):
    """Main configuration object."""

    data: DataConfig = Field(default_factory=DataConfig)
    indicators: IndicatorConfig = Field(default_factory=IndicatorConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    brain: BrainConfig = Field(default_factory=BrainConfig)
    fallback_engine: FallbackEngineConfig = Field(default_factory=FallbackEngineConfig)
    risk_gate: RiskGateConfig = Field(default_factory=RiskGateConfig)
    sharia: ShartiaConfig = Field(default_factory=ShartiaConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    state_machine: StateMachineConfig = Field(default_factory=StateMachineConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)

    class Config:
        arbitrary_types_allowed = True

    @validator("scoring")
    def validate_weights(cls, v):
        """Ensure scoring weights are reasonable."""
        if not (0 <= v.rsi_weight <= 1):
            raise ValueError("RSI weight must be 0-1")
        if not (0 <= v.confidence_threshold_act <= 100):
            raise ValueError("Confidence threshold must be 0-100")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
        return cls.from_yaml(config_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.dict()


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML or environment."""
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")

    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    return Config.from_yaml(config_path)


def load_sharia_rules(rules_path: str = "config/sharia_rules.yaml") -> Dict[str, Any]:
    """Load Sharia compliance rules from YAML."""
    if not Path(rules_path).exists():
        raise FileNotFoundError(f"Sharia rules file not found: {rules_path}")

    with open(rules_path, "r") as f:
        rules = yaml.safe_load(f)
    return rules
