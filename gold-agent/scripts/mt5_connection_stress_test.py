#!/usr/bin/env python
"""
MT5 Connection Reliability Stress Test
======================================

Tests real Exness MT5 connection reliability via 1000 cycles:
- Connect → Query real symbol data → Disconnect → Log results
- Or: Connect once → Run 1000 sequential data queries

Usage:
    python mt5_connection_stress_test.py --cycles 1000 --mode query

Modes:
    - "connect": 1000 separate connect/disconnect cycles (stricter test)
    - "query": 1 connection, 1000 sequential queries (faster test)

Environment Variables (create .env in project root):
    MT5_LOGIN=12345678          # Your Exness demo account number
    MT5_PASSWORD=YourPassword   # Your Exness demo password
    MT5_SERVER=ExnessMT5-Demo   # Server name (e.g., ExnessMT5-Demo, ExnessMT5Demo)

Results:
    - Saves detailed CSV log to: logs/mt5_stress_test_TIMESTAMP.csv
    - Prints summary statistics (success rate, latency, errors)
    - Identifies failure patterns (time-based clustering, query-type clustering)
"""

import sys
import os
import time
import csv
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables only")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


@dataclass
class ConnectionTestResult:
    """Single connection/query test result."""
    cycle_number: int
    timestamp: str
    mode: str  # "connect" or "query"
    symbol: str
    success: bool
    response_time_ms: float
    error_message: Optional[str]
    data_valid: bool
    data_fields: Optional[Dict]  # {"price": 2050.5, "swap_long": 0.0, ...}
    retry_attempts: int
    retry_reason: Optional[str]


class MT5ConnectionStressTester:
    """Stress test MT5 connection reliability."""

    def __init__(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
    ):
        """Initialize with Exness credentials."""
        self.login = login or int(os.getenv("MT5_LOGIN", "0"))
        self.password = password or os.getenv("MT5_PASSWORD", "")
        self.server = server or os.getenv("MT5_SERVER", "ExnessMT5-Demo")

        self.connected = False
        self.mt5 = None
        self.results: List[ConnectionTestResult] = []
        self.retry_config = {
            "max_retries": 3,
            "backoff_initial": 0.1,  # 100ms
            "backoff_max": 5.0,  # 5 seconds
        }

        # Symbols to test (mix of asset classes)
        self.test_symbols = [
            "XAUUSD",  # Gold (commodity)
            "EURUSD",  # Forex
            "GBPUSD",  # Forex
            "MSFT",    # Stock (if available)
            "AAPL",    # Stock (if available)
        ]

    def _import_mt5(self) -> bool:
        """Attempt to import MetaTrader5 library."""
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            logger.info("✓ MetaTrader5 library imported successfully")
            return True
        except ImportError:
            logger.error("✗ MetaTrader5 library not installed: pip install MetaTrader5")
            return False

    def _connect_with_retry(self) -> bool:
        """Connect to MT5 with exponential backoff retry."""
        if not self.mt5:
            logger.error("MT5 not imported, cannot connect")
            return False

        retry_count = 0
        backoff_time = self.retry_config["backoff_initial"]

        while retry_count <= self.retry_config["max_retries"]:
            try:
                logger.info(
                    f"Connecting to MT5 (attempt {retry_count + 1}/{self.retry_config['max_retries'] + 1}): "
                    f"login={self.login}, server={self.server}"
                )

                if self.mt5.initialize(
                    login=self.login,
                    password=self.password,
                    server=self.server,
                ):
                    logger.info("✓ Connected to MT5 successfully")
                    self.connected = True
                    return True
                else:
                    error = self.mt5.last_error()
                    logger.warning(
                        f"✗ Connection failed (attempt {retry_count + 1}): {error}"
                    )
                    retry_count += 1
                    if retry_count <= self.retry_config["max_retries"]:
                        logger.info(f"  Retrying in {backoff_time:.2f}s...")
                        time.sleep(backoff_time)
                        backoff_time = min(
                            backoff_time * 2,
                            self.retry_config["backoff_max"]
                        )

            except Exception as e:
                logger.error(f"✗ Connection exception (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count <= self.retry_config["max_retries"]:
                    logger.info(f"  Retrying in {backoff_time:.2f}s...")
                    time.sleep(backoff_time)
                    backoff_time = min(
                        backoff_time * 2,
                        self.retry_config["backoff_max"]
                    )

        logger.error(
            f"✗ Failed to connect after {self.retry_config['max_retries'] + 1} attempts"
        )
        return False

    def _disconnect(self) -> None:
        """Disconnect from MT5."""
        if self.mt5 and self.connected:
            try:
                self.mt5.shutdown()
                self.connected = False
                logger.debug("✓ Disconnected from MT5")
            except Exception as e:
                logger.error(f"✗ Disconnect error: {e}")

    def _query_symbol_data(self, symbol: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Query real symbol data from MT5.

        Returns:
            (success, data_dict, error_message)
        """
        if not self.connected or not self.mt5:
            return False, None, "Not connected to MT5"

        try:
            # Query symbol info
            symbol_info = self.mt5.symbol_info(symbol)
            if symbol_info is None:
                return False, None, f"Symbol {symbol} not found"

            # Extract key fields
            data = {
                "symbol": symbol,
                "ask": symbol_info.ask,
                "bid": symbol_info.bid,
                "spread": symbol_info.ask - symbol_info.bid,
                "swap_long": symbol_info.swap_long,
                "swap_short": symbol_info.swap_short,
                "contract_type": "SPOT" if not symbol_info.is_derivative else "DERIVATIVE",
            }

            # Validate data completeness
            required_fields = ["ask", "bid", "swap_long", "swap_short"]
            data_valid = all(
                key in data and data[key] is not None
                for key in required_fields
            )

            if not data_valid:
                return False, data, "Incomplete data returned"

            return True, data, None

        except Exception as e:
            return False, None, str(e)

    def stress_test_connect_mode(self, cycles: int = 1000) -> None:
        """
        Stress test: 1000 separate connect/disconnect cycles.
        Stricter test — measures connection establishment overhead.
        """
        logger.info(f"Starting stress test: {cycles} connect/disconnect cycles")
        logger.info(f"Testing symbols: {self.test_symbols}")

        for cycle in range(1, cycles + 1):
            # Select symbol (rotate through test symbols)
            symbol = self.test_symbols[(cycle - 1) % len(self.test_symbols)]

            # Connect
            start_time = time.time()
            connect_success = self._connect_with_retry()
            connect_time = (time.time() - start_time) * 1000  # ms

            if not connect_success:
                result = ConnectionTestResult(
                    cycle_number=cycle,
                    timestamp=datetime.utcnow().isoformat(),
                    mode="connect",
                    symbol=symbol,
                    success=False,
                    response_time_ms=connect_time,
                    error_message="Connection failed",
                    data_valid=False,
                    data_fields=None,
                    retry_attempts=self.retry_config["max_retries"] + 1,
                    retry_reason="Connection exhausted retries",
                )
                self.results.append(result)
                logger.warning(f"[Cycle {cycle}] Connection failed after retries")
                continue

            # Query data
            query_start = time.time()
            data_success, data_dict, error_msg = self._query_symbol_data(symbol)
            query_time = (time.time() - query_start) * 1000  # ms

            # Disconnect
            self._disconnect()

            total_time = (time.time() - start_time) * 1000  # ms

            # Log result
            result = ConnectionTestResult(
                cycle_number=cycle,
                timestamp=datetime.utcnow().isoformat(),
                mode="connect",
                symbol=symbol,
                success=data_success,
                response_time_ms=total_time,
                error_message=error_msg if not data_success else None,
                data_valid=data_success,
                data_fields=data_dict,
                retry_attempts=1,
                retry_reason=None,
            )
            self.results.append(result)

            # Progress logging
            if cycle % 100 == 0:
                success_count = sum(1 for r in self.results if r.success)
                success_rate = (success_count / len(self.results)) * 100
                avg_time = sum(r.response_time_ms for r in self.results) / len(self.results)
                logger.info(
                    f"Progress: {cycle}/{cycles} | "
                    f"Success: {success_rate:.1f}% | "
                    f"Avg Time: {avg_time:.1f}ms"
                )

    def stress_test_query_mode(self, cycles: int = 1000) -> None:
        """
        Stress test: 1 connection, 1000 sequential queries.
        Faster test — measures query reliability once connected.
        """
        logger.info(f"Starting stress test: 1 connection, {cycles} sequential queries")
        logger.info(f"Testing symbols: {self.test_symbols}")

        # Single connection
        if not self._connect_with_retry():
            logger.error("Cannot connect to MT5, aborting stress test")
            return

        try:
            for cycle in range(1, cycles + 1):
                # Select symbol (rotate through test symbols)
                symbol = self.test_symbols[(cycle - 1) % len(self.test_symbols)]

                # Query data
                start_time = time.time()
                data_success, data_dict, error_msg = self._query_symbol_data(symbol)
                response_time = (time.time() - start_time) * 1000  # ms

                # Log result
                result = ConnectionTestResult(
                    cycle_number=cycle,
                    timestamp=datetime.utcnow().isoformat(),
                    mode="query",
                    symbol=symbol,
                    success=data_success,
                    response_time_ms=response_time,
                    error_message=error_msg if not data_success else None,
                    data_valid=data_success,
                    data_fields=data_dict,
                    retry_attempts=0,
                    retry_reason=None,
                )
                self.results.append(result)

                # Progress logging
                if cycle % 100 == 0:
                    success_count = sum(1 for r in self.results if r.success)
                    success_rate = (success_count / len(self.results)) * 100
                    avg_time = sum(r.response_time_ms for r in self.results) / len(self.results)
                    logger.info(
                        f"Progress: {cycle}/{cycles} | "
                        f"Success: {success_rate:.1f}% | "
                        f"Avg Time: {avg_time:.2f}ms"
                    )

        finally:
            self._disconnect()

    def analyze_results(self) -> None:
        """Analyze results and identify patterns."""
        if not self.results:
            logger.error("No results to analyze")
            return

        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total_tests - successful
        success_rate = (successful / total_tests) * 100

        logger.info("=" * 70)
        logger.info("STRESS TEST RESULTS")
        logger.info("=" * 70)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {success_rate:.2f}%")
        logger.info("")

        # Response time analysis
        successful_times = [r.response_time_ms for r in self.results if r.success]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            min_time = min(successful_times)
            max_time = max(successful_times)
            logger.info(f"Response Time (successful only):")
            logger.info(f"  Average: {avg_time:.2f}ms")
            logger.info(f"  Min: {min_time:.2f}ms")
            logger.info(f"  Max: {max_time:.2f}ms")
            logger.info("")

        # Error analysis
        if failed > 0:
            logger.info(f"Failed Tests Analysis:")
            error_counts = defaultdict(int)
            for r in self.results:
                if not r.success and r.error_message:
                    error_counts[r.error_message] += 1

            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {error}: {count} occurrences")
            logger.info("")

        # Failure clustering analysis
        failure_cycles = [r.cycle_number for r in self.results if not r.success]
        if failure_cycles:
            logger.info(f"Failure Clustering Analysis:")

            # By symbol
            symbol_failures = defaultdict(int)
            for r in self.results:
                if not r.success:
                    symbol_failures[r.symbol] += 1
            logger.info(f"  By Symbol:")
            for symbol, count in sorted(symbol_failures.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"    {symbol}: {count} failures")

            # By cycle position (first/middle/last 100)
            first_100 = sum(1 for c in failure_cycles if c <= 100)
            last_100 = sum(1 for c in failure_cycles if c > total_tests - 100)
            middle = len(failure_cycles) - first_100 - last_100
            logger.info(f"  By Position:")
            logger.info(f"    First 100 cycles: {first_100} failures")
            logger.info(f"    Middle cycles: {middle} failures")
            logger.info(f"    Last 100 cycles: {last_100} failures")
            logger.info("")

        # Retry analysis (connect mode only)
        connect_results = [r for r in self.results if r.mode == "connect"]
        if connect_results:
            retried = sum(1 for r in connect_results if r.retry_attempts > 1)
            logger.info(f"Retry Analysis (connect mode):")
            logger.info(f"  Tests requiring retries: {retried}/{len(connect_results)}")
            if retried > 0:
                logger.info(f"  Retry success rate: {(successful - (len(connect_results) - retried)) / retried * 100:.1f}%")
            logger.info("")

        # Verdict
        logger.info("RELIABILITY VERDICT:")
        if success_rate >= 99.5:
            logger.info(f"  ✅ EXCELLENT: {success_rate:.2f}% success rate")
            logger.info("  Acceptable for live trading (very high reliability)")
        elif success_rate >= 99.0:
            logger.info(f"  ✅ GOOD: {success_rate:.2f}% success rate")
            logger.info("  Generally acceptable for live trading")
        elif success_rate >= 95.0:
            logger.info(f"  ⚠️  ACCEPTABLE: {success_rate:.2f}% success rate")
            logger.info("  Acceptable but monitor closely for failure patterns")
        else:
            logger.info(f"  ❌ POOR: {success_rate:.2f}% success rate")
            logger.info("  NOT acceptable for live trading — investigate root causes")

        logger.info("=" * 70)

    def save_results_csv(self) -> Path:
        """Save detailed results to CSV."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        csv_path = log_dir / f"mt5_stress_test_{timestamp}.csv"

        try:
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                writer.writeheader()
                for result in self.results:
                    result_dict = asdict(result)
                    # Convert data_fields to JSON string
                    result_dict["data_fields"] = json.dumps(result.data_fields) if result.data_fields else ""
                    writer.writerow(result_dict)

            logger.info(f"✓ Results saved to: {csv_path}")
            return csv_path

        except Exception as e:
            logger.error(f"✗ Failed to save CSV: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="MT5 Connection Reliability Stress Test"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1000,
        help="Number of test cycles (default: 1000)",
    )
    parser.add_argument(
        "--mode",
        choices=["connect", "query"],
        default="query",
        help="Test mode: connect (separate cycles) or query (single connection)",
    )
    parser.add_argument(
        "--login",
        type=int,
        help="MT5 login (or use MT5_LOGIN env var)",
    )
    parser.add_argument(
        "--password",
        help="MT5 password (or use MT5_PASSWORD env var)",
    )
    parser.add_argument(
        "--server",
        help="MT5 server (or use MT5_SERVER env var)",
    )

    args = parser.parse_args()

    # Check if credentials are available
    login = args.login or int(os.getenv("MT5_LOGIN", "0") or "0")
    password = args.password or os.getenv("MT5_PASSWORD", "")
    server = args.server or os.getenv("MT5_SERVER", "ExnessMT5-Demo")

    if not login or not password:
        logger.error(
            "\n❌ MT5 credentials not provided!\n"
            "Set environment variables or pass command-line arguments:\n"
            "  MT5_LOGIN=12345678 MT5_PASSWORD=YourPassword python mt5_connection_stress_test.py\n"
            "OR:\n"
            "  python mt5_connection_stress_test.py --login 12345678 --password YourPassword\n"
        )
        return 1

    # Run stress test
    tester = MT5ConnectionStressTester(login=login, password=password, server=server)

    if not tester._import_mt5():
        logger.error("Cannot proceed without MetaTrader5 library")
        return 1

    try:
        if args.mode == "connect":
            tester.stress_test_connect_mode(cycles=args.cycles)
        else:
            tester.stress_test_query_mode(cycles=args.cycles)

        # Analyze and report
        tester.analyze_results()
        csv_path = tester.save_results_csv()

        logger.info(f"\n✓ Stress test complete. CSV log: {csv_path}\n")
        return 0

    except KeyboardInterrupt:
        logger.info("\n⏸ Stress test interrupted by user")
        tester.analyze_results()
        csv_path = tester.save_results_csv()
        logger.info(f"Partial results saved to: {csv_path}")
        return 1
    except Exception as e:
        logger.error(f"✗ Stress test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
