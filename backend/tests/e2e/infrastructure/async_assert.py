"""
AsyncAssert — async wait and assertion utilities for CarbonScope E2E tests.

Provides structured waiting patterns that produce descriptive failure messages
when conditions are not met, avoiding flaky ``asyncio.sleep()`` calls.

Example::

    # Wait for a condition
    await AsyncAssert.wait_until(
        lambda: check_status() == "complete",
        "assessment to reach 'complete' status",
        timeout=30.0,
    )

    # Wait for a specific value
    await AsyncAssert.wait_for_value(
        lambda: get_count(),
        expected=5,
        description="thread count to reach 5",
    )
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union

logger = logging.getLogger("e2e.async_assert")

T = TypeVar("T")
Condition = Union[Callable[[], bool], Callable[[], Coroutine[Any, Any, bool]]]


async def _eval(cond: Condition) -> bool:
    """Evaluate a condition that may be sync or async."""
    if asyncio.iscoroutinefunction(cond):
        return await cond()  # type: ignore[call-arg]
    result = cond()
    if asyncio.iscoroutine(result):
        return await result
    return bool(result)


class AsyncAssert:
    """Static utility class for async assertions in E2E tests."""

    # ── Core wait ─────────────────────────────────────────────────────────

    @staticmethod
    async def wait_until(
        condition: Condition,
        description: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> None:
        """
        Poll ``condition`` until it returns True or ``timeout`` seconds elapse.

        Args:
            condition:     A sync or async callable returning bool.
            description:   Human-readable description shown in failure messages.
            timeout:       Maximum seconds to wait (default 30).
            poll_interval: Seconds between polls (default 0.5).

        Raises:
            AssertionError: If the condition is still False after ``timeout``.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            if await _eval(condition):
                return
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for: {description}"
        )

    @staticmethod
    async def wait_until_verbose(
        condition: Condition,
        description: str,
        timeout: float = 30.0,
        poll_interval: float = 1.0,
        log_every: int = 5,
    ) -> None:
        """
        Like ``wait_until`` but logs progress every ``log_every`` polls.

        Useful for long-running waits (agent runs, processing pipelines).
        """
        deadline = asyncio.get_event_loop().time() + timeout
        poll_count = 0
        while asyncio.get_event_loop().time() < deadline:
            if await _eval(condition):
                return
            poll_count += 1
            if poll_count % log_every == 0:
                elapsed = timeout - (deadline - asyncio.get_event_loop().time())
                logger.info(f"Still waiting ({elapsed:.1f}s): {description}")
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for: {description}"
        )

    # ── Value waits ───────────────────────────────────────────────────────

    @staticmethod
    async def wait_for_value(
        getter: Callable[[], T],
        expected: T,
        description: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> None:
        """
        Wait until ``getter()`` returns ``expected``.

        Failure includes current vs expected value for easy debugging.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        last: Any = None
        while asyncio.get_event_loop().time() < deadline:
            if asyncio.iscoroutinefunction(getter):
                last = await getter()  # type: ignore[call-arg]
            else:
                last = getter()
            if last == expected:
                return
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for: {description}\n"
            f"  Expected: {expected!r}\n"
            f"  Got:      {last!r}"
        )

    @staticmethod
    async def wait_for_value_approx(
        getter: Callable[[], float],
        expected: float,
        description: str,
        tolerance: float = 0.01,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> None:
        """
        Wait until ``getter()`` is within ``tolerance`` of ``expected``.

        Useful for floating-point carbon calculation results.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        last: float = 0.0
        while asyncio.get_event_loop().time() < deadline:
            if asyncio.iscoroutinefunction(getter):
                last = await getter()  # type: ignore[call-arg]
            else:
                last = getter()
            if abs(last - expected) <= tolerance:
                return
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for: {description}\n"
            f"  Expected: {expected!r} ± {tolerance}\n"
            f"  Got:      {last!r}"
        )

    @staticmethod
    async def wait_for_value_not(
        getter: Callable[[], T],
        not_expected: T,
        description: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> None:
        """
        Wait until ``getter()`` returns anything other than ``not_expected``.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        last: Any = not_expected
        while asyncio.get_event_loop().time() < deadline:
            if asyncio.iscoroutinefunction(getter):
                last = await getter()  # type: ignore[call-arg]
            else:
                last = getter()
            if last != not_expected:
                return
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for: {description}\n"
            f"  Value remained: {last!r}"
        )

    @staticmethod
    async def wait_for_not_none(
        getter: Callable[[], Optional[T]],
        description: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> T:
        """
        Wait until ``getter()`` returns a non-None value.

        Returns:
            The first non-None value returned by ``getter``.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            if asyncio.iscoroutinefunction(getter):
                value = await getter()  # type: ignore[call-arg]
            else:
                value = getter()
            if value is not None:
                return value  # type: ignore[return-value]
            await asyncio.sleep(poll_interval)
        raise AssertionError(
            f"Timed out after {timeout}s waiting for non-None: {description}"
        )

    # ── Negative assertion ────────────────────────────────────────────────

    @staticmethod
    async def assert_never_true(
        condition: Condition,
        description: str,
        duration: float = 5.0,
        poll_interval: float = 0.25,
    ) -> None:
        """
        Assert that ``condition`` never becomes True within ``duration`` seconds.

        Use for verifying invariants: e.g. error count stays at zero.

        Raises:
            AssertionError: If the condition ever returns True.
        """
        deadline = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < deadline:
            if await _eval(condition):
                raise AssertionError(
                    f"Condition became true (should never happen): {description}"
                )
            await asyncio.sleep(poll_interval)

    # ── Timing utilities ──────────────────────────────────────────────────

    @staticmethod
    async def wait_requests(n: int = 1, interval: float = 0.1) -> None:
        """
        Yield ``n`` times with ``interval`` sleep, simulating request cycles.

        Use when you need a brief pause for async side-effects to propagate
        without resorting to arbitrary ``sleep()`` calls.
        """
        for _ in range(n):
            await asyncio.sleep(interval)

    @staticmethod
    async def wait_for_background_tasks(extra_sleep: float = 0.2) -> None:
        """
        Yield control to the event loop to let background tasks complete.
        """
        await asyncio.sleep(0)
        await asyncio.sleep(extra_sleep)
