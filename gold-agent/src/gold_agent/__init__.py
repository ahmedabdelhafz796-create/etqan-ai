"""Gold Trading Analysis Agent — Semi-automated trading decision system."""

__version__ = "0.1.0"
__author__ = "Gold Trading Analysis Agent Team"

from src.gold_agent.config import Config
from src.gold_agent.core.models import Decision, MarketData, NewsItem
from src.gold_agent.state_machine import StateMachine

__all__ = [
    "Config",
    "Decision",
    "MarketData",
    "NewsItem",
    "StateMachine",
]
