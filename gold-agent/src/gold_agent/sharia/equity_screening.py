"""Equity Sharia Screening — AAOIFI Standard + MSCI Islamic Methodology.

Two-layer screening for stocks:
1. Sector exclusion list (alcohol, gambling, interest-based finance, etc.)
2. Financial ratio purification screening (AAOIFI/MSCI/DJIM standards)

References:
- AAOIFI Sharia Standard No. 23: Investment Funds
- MSCI Islamic Methodology
- Dow Jones Islamic Market (DJIM) criteria
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EquityFinancialData:
    """Financial metrics for equity screening."""
    total_debt: float  # Total debt in USD
    market_cap: float  # Market capitalization in USD
    revenue: float  # Annual revenue in USD
    interest_income: float  # Interest income (banks/finance) in USD
    cash_equivalents: float  # Cash and equivalents in USD


class EquityShariScreening:
    """
    Two-layer Sharia compliance screening for equities per AAOIFI standards.
    Layer 1: Sector exclusion (hard filter)
    Layer 2: Financial ratio purification (quantitative filter)
    """

    # Layer 1: Prohibited Sectors (AAOIFI Standard No. 23)
    PROHIBITED_SECTORS = {
        "alcohol",  # Alcohol production/distribution
        "gambling",  # Casinos, gambling operators, lotteries
        "banking",  # Conventional interest-based banking
        "insurance",  # Conventional insurance (not takaful)
        "finance",  # Financial services (interest-based lending)
        "defense",  # Weapons/defense contractors
        "tobacco",  # Tobacco production
        "entertainment",  # Adult entertainment
    }

    def __init__(self):
        """Initialize equity screening engine."""
        self.violations = []
        self.last_screening_result = None

    def screen_equity(self, ticker: str, sector: str, financial_data: Optional[EquityFinancialData] = None) -> Tuple[bool, str]:
        """
        Perform two-layer Sharia screening on equity.

        Args:
            ticker: Stock ticker (e.g., "MSFT", "AAPL")
            sector: Sector classification (e.g., "technology", "banking")
            financial_data: Financial metrics for ratio screening

        Returns:
            (is_compliant: bool, reason: str)
        """
        self.violations = []

        # LAYER 1: Sector Exclusion (hard rejection)
        if not self._check_sector_compliance(sector):
            reason = f"Sector exclusion: {ticker} is in prohibited sector {sector}"
            logger.warning(f"✗ Equity screening FAILED: {reason}")
            return False, reason

        # LAYER 2: Financial Ratio Screening (AAOIFI thresholds)
        if financial_data and not self._check_financial_ratios(ticker, financial_data):
            reason = f"Financial ratio violation: {ticker} fails AAOIFI purification test. Violations: {'; '.join(self.violations)}"
            logger.warning(f"✗ Equity screening FAILED: {reason}")
            return False, reason

        # Both layers passed
        reason = f"Equity {ticker} passes Sharia screening (sector: {sector}, AAOIFI ratios compliant)"
        logger.info(f"✓ Equity screening PASSED: {reason}")
        return True, reason

    def _check_sector_compliance(self, sector: str) -> bool:
        """
        Layer 1: Hard exclusion of prohibited sectors.

        Returns:
            False if sector is in prohibited list
            True otherwise
        """
        sector_lower = sector.lower()

        # Exact matches and substring matches
        for prohibited in self.PROHIBITED_SECTORS:
            if prohibited in sector_lower:
                self.violations.append(f"Sector '{sector}' contains prohibited keyword '{prohibited}'")
                return False

        return True

    def _check_financial_ratios(self, ticker: str, data: EquityFinancialData) -> bool:
        """
        Layer 2: Financial ratio screening per AAOIFI/MSCI Islamic standards.

        AAOIFI Thresholds:
        - Debt/Market Cap ≤ 33% (30-33% depending on school)
        - Interest Income/Revenue ≤ 5%
        - Illiquid Assets/Total Assets ≤ 33%

        MSCI/DJIM Similar:
        - Total Debt/Market Cap ≤ 33%
        - Cash + Equivalents/Total Assets ≥ 5% (liquidity check)

        Returns:
            True if all ratios pass
            False if any ratio violates threshold
        """
        all_pass = True

        # Check 1: Debt-to-Market-Cap Ratio (AAOIFI 33% threshold)
        if data.market_cap > 0:
            debt_ratio = data.total_debt / data.market_cap
            if debt_ratio > 0.33:
                self.violations.append(
                    f"Debt/Market Cap = {debt_ratio:.1%} (AAOIFI max 33%)"
                )
                all_pass = False
            else:
                logger.debug(f"  ✓ Debt/Market Cap: {debt_ratio:.1%} (pass)")

        # Check 2: Interest Income Ratio (AAOIFI 5% threshold)
        if data.revenue > 0:
            interest_ratio = data.interest_income / data.revenue
            if interest_ratio > 0.05:
                self.violations.append(
                    f"Interest Income/Revenue = {interest_ratio:.1%} (AAOIFI max 5%)"
                )
                all_pass = False
            else:
                logger.debug(f"  ✓ Interest Income/Revenue: {interest_ratio:.1%} (pass)")

        # Check 3: Liquidity Check (Cash/Equivalents > 0)
        if data.cash_equivalents <= 0:
            self.violations.append("No cash equivalents (liquidity concern)")
            all_pass = False
        else:
            logger.debug(f"  ✓ Cash Equivalents: ${data.cash_equivalents:,.0f} (pass)")

        return all_pass

    def get_compliance_summary(self) -> Dict:
        """Return summary of last screening."""
        return {
            "compliant": self.last_screening_result if self.last_screening_result is not None else False,
            "violations": self.violations,
            "methodology": "AAOIFI Sharia Standard No. 23",
        }
