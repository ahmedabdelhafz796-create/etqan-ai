"""Gold Trading Analysis Agent — Semi-automated trading decision system."""

__version__ = "0.1.0"
__author__ = "Gold Trading Analysis Agent Team"

from gold_agent.config import Config
from gold_agent.core.models import Decision, MarketData, NewsItem
from gold_agent.state_machine import StateMachine

__all__ = [
    "Config",
    "Decision",
    "MarketData",
    "NewsItem",
    "StateMachine",
]
