"""Notification Module (§4 MASTER_PLAN) — Telegram + console fallback."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from gold_agent.core.models import Decision, StateType


class Notifier(ABC):
    """Abstract notifier interface."""

    @abstractmethod
    async def notify_decision(self, decision: Decision) -> bool:
        """Send decision notification."""
        pass

    @abstractmethod
    async def notify_blocked(self, decision: Decision, gate: str) -> bool:
        """Send gate-blocked notification."""
        pass

    @abstractmethod
    async def notify_wait(self, decision: Decision) -> bool:
        """Send WAIT notification."""
        pass

    @abstractmethod
    async def notify_state_change(self, new_state: str, reason: str) -> bool:
        """Send state machine change notification."""
        pass

    @abstractmethod
    async def notify_emergency(self, reason: str) -> bool:
        """Send emergency alert."""
        pass


class ConsoleNotifier(Notifier):
    """Console-based notifier (development/fallback)."""

    def __init__(self, language: str = "en"):
        self.language = language

    async def notify_decision(self, decision: Decision) -> bool:
        """Print decision to console."""
        msg = self._format_decision(decision)
        print(msg)
        return True

    async def notify_blocked(self, decision: Decision, gate: str) -> bool:
        """Print gate block to console."""
        msg = f"🚫 {gate} BLOCKED: {decision.action.value} | Confidence: {decision.confidence:.0f}%"
        print(msg)
        return True

    async def notify_wait(self, decision: Decision) -> bool:
        """Print WAIT to console."""
        msg = f"⏳ WAIT: Confidence {decision.confidence:.0f}% below threshold"
        print(msg)
        return True

    async def notify_state_change(self, new_state: str, reason: str) -> bool:
        """Print state change to console."""
        msg = f"🔄 State: {new_state.upper()} | {reason}"
        print(msg)
        return True

    async def notify_emergency(self, reason: str) -> bool:
        """Print emergency alert to console."""
        msg = f"🚨 EMERGENCY: {reason}"
        print(msg)
        return True

    def _format_decision(self, decision: Decision) -> str:
        """Format decision for console output."""
        arrow = "📈" if decision.action.value == "BUY" else "📉" if decision.action.value == "SELL" else "⏳"

        msg = (
            f"{arrow} {decision.action.value} | "
            f"Confidence: {decision.confidence:.0f}% | "
            f"Reason: {decision.reason}"
        )
        return msg


class TelegramNotifier(Notifier):
    """Telegram bot notifier (production)."""

    def __init__(self, bot_token: str, chat_id: str, config):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.config = config
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Telegram bot client."""
        try:
            from telegram import Bot
            self.client = Bot(token=self.bot_token)
        except ImportError:
            print("python-telegram-bot not installed. Telegram notifications disabled.")
            self.client = None
        except Exception as e:
            print(f"Failed to initialize Telegram: {e}")
            self.client = None

    async def notify_decision(self, decision: Decision) -> bool:
        """Send decision via Telegram."""
        if not self.client:
            return False

        try:
            msg = self._format_decision(decision)
            await self.client.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False

    async def notify_blocked(self, decision: Decision, gate: str) -> bool:
        """Send gate block via Telegram."""
        if not self.client:
            return False

        try:
            msg = f"*🚫 {gate} BLOCKED*\n\nAction: {decision.action.value}\nConfidence: {decision.confidence:.0f}%\n\nReason: {decision.reason}"
            await self.client.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False

    async def notify_wait(self, decision: Decision) -> bool:
        """Send WAIT via Telegram."""
        if not self.client:
            return False

        try:
            msg = f"*⏳ WAIT*\n\nConfidence {decision.confidence:.0f}% below threshold ({self.config.scoring.confidence_threshold_wait}%)"
            await self.client.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False

    async def notify_state_change(self, new_state: str, reason: str) -> bool:
        """Send state change via Telegram."""
        if not self.client:
            return False

        try:
            state_emoji = {
                "autonomous": "✅",
                "safe_mode": "⚠️",
                "emergency": "🚨",
                "manual_recovery": "🔧"
            }
            emoji = state_emoji.get(new_state, "")
            msg = f"*{emoji} State Change*\n\nNew State: {new_state.upper()}\n\nReason: {reason}"
            await self.client.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False

    async def notify_emergency(self, reason: str) -> bool:
        """Send emergency alert via Telegram."""
        if not self.client:
            return False

        try:
            msg = f"*🚨 EMERGENCY ALERT*\n\n{reason}\n\nTimestamp: {datetime.utcnow().isoformat()}"
            await self.client.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False

    def _format_decision(self, decision: Decision) -> str:
        """Format decision for Telegram."""
        emoji = "📈" if decision.action.value == "BUY" else "📉" if decision.action.value == "SELL" else "⏳"
        msg = (
            f"{emoji} *{decision.action.value}* Decision\n\n"
            f"Confidence: {decision.confidence:.0f}%\n"
            f"Reason: {decision.reason}\n"
            f"Time: {decision.timestamp.strftime('%H:%M:%S UTC')}"
        )
        return msg

    def _format_decision_arabic(self, decision: Decision) -> str:
        """Format decision in Arabic for Telegram."""
        action_ar = {
            "BUY": "شراء",
            "SELL": "بيع",
            "WAIT": "انتظار"
        }

        msg = (
            f"*قرار التداول* 🎯\n\n"
            f"الإجراء: {action_ar.get(decision.action.value, decision.action.value)}\n"
            f"الثقة: {decision.confidence:.0f}%\n"
            f"السبب: {decision.reason}\n"
            f"الوقت: {decision.timestamp.strftime('%H:%M:%S UTC')}"
        )
        return msg


class HybridNotifier(Notifier):
    """Hybrid notifier: Telegram + console fallback."""

    def __init__(self, config):
        self.config = config
        self.telegram = None
        self.console = ConsoleNotifier(language=config.notification.console_language)

        if config.notification.telegram_enabled and config.notification.telegram_bot_token:
            self.telegram = TelegramNotifier(
                bot_token=config.notification.telegram_bot_token,
                chat_id=config.notification.telegram_chat_id,
                config=config,
            )

    async def notify_decision(self, decision: Decision) -> bool:
        """Send via Telegram or console."""
        result = True

        if self.telegram:
            try:
                result = await self.telegram.notify_decision(decision)
            except Exception as e:
                print(f"Telegram failed: {e}. Falling back to console.")

        if not result or not self.telegram:
            await self.console.notify_decision(decision)

        return True

    async def notify_blocked(self, decision: Decision, gate: str) -> bool:
        """Send gate block."""
        result = True

        if self.telegram:
            try:
                result = await self.telegram.notify_blocked(decision, gate)
            except Exception as e:
                print(f"Telegram failed: {e}. Falling back to console.")

        if not result or not self.telegram:
            await self.console.notify_blocked(decision, gate)

        return True

    async def notify_wait(self, decision: Decision) -> bool:
        """Send WAIT."""
        result = True

        if self.telegram:
            try:
                result = await self.telegram.notify_wait(decision)
            except Exception as e:
                print(f"Telegram failed: {e}. Falling back to console.")

        if not result or not self.telegram:
            await self.console.notify_wait(decision)

        return True

    async def notify_state_change(self, new_state: str, reason: str) -> bool:
        """Send state change."""
        result = True

        if self.telegram:
            try:
                result = await self.telegram.notify_state_change(new_state, reason)
            except Exception as e:
                print(f"Telegram failed: {e}. Falling back to console.")

        if not result or not self.telegram:
            await self.console.notify_state_change(new_state, reason)

        return True

    async def notify_emergency(self, reason: str) -> bool:
        """Send emergency alert."""
        result = True

        if self.telegram:
            try:
                result = await self.telegram.notify_emergency(reason)
            except Exception as e:
                print(f"Telegram failed: {e}. Falling back to console.")

        if not result or not self.telegram:
            await self.console.notify_emergency(reason)

        return True


def get_notifier(config) -> Notifier:
    """Factory function to get notifier."""
    return HybridNotifier(config)
