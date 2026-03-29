"""
Tests for app.utils.retry module.
"""

import time
import pytest
from unittest.mock import MagicMock, call

from app.utils.retry import retry_with_backoff, RetryableAPIClient


class TestRetryWithBackoff:
    """Tests for the retry_with_backoff decorator."""

    def test_succeeds_first_try(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def success():
            nonlocal call_count
            call_count += 1
            return "ok"

        assert success() == "ok"
        assert call_count == 1

    def test_retries_then_succeeds(self):
        attempts = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def fail_twice():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("not yet")
            return "finally"

        assert fail_twice() == "finally"
        assert attempts == 3

    def test_raises_after_max_retries(self):
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fail():
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError, match="always fails"):
            always_fail()

    def test_only_retries_specified_exceptions(self):
        attempts = 0

        @retry_with_backoff(
            max_retries=3, initial_delay=0.01, exceptions=(ValueError,)
        )
        def raises_type_error():
            nonlocal attempts
            attempts += 1
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()
        assert attempts == 1  # No retries for TypeError

    def test_on_retry_callback(self):
        callback = MagicMock()
        attempts = 0

        @retry_with_backoff(
            max_retries=3, initial_delay=0.01, on_retry=callback
        )
        def fail_once():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ValueError("first fail")
            return "ok"

        fail_once()
        callback.assert_called_once()
        args = callback.call_args[0]
        assert isinstance(args[0], ValueError)
        assert args[1] == 1  # retry count


class TestRetryableAPIClient:
    """Tests for RetryableAPIClient."""

    def test_call_with_retry_success(self):
        client = RetryableAPIClient(max_retries=3, initial_delay=0.01)
        result = client.call_with_retry(lambda: "success")
        assert result == "success"

    def test_call_with_retry_retries(self):
        client = RetryableAPIClient(max_retries=3, initial_delay=0.01)
        counter = {"n": 0}

        def flaky():
            counter["n"] += 1
            if counter["n"] < 3:
                raise ConnectionError("flaky")
            return "recovered"

        result = client.call_with_retry(flaky)
        assert result == "recovered"

    def test_call_with_retry_fails(self):
        client = RetryableAPIClient(max_retries=2, initial_delay=0.01)

        def always_fail():
            raise IOError("permanent failure")

        with pytest.raises(IOError, match="permanent failure"):
            client.call_with_retry(always_fail)

    def test_call_batch_with_retry_all_succeed(self):
        client = RetryableAPIClient(max_retries=2, initial_delay=0.01)
        items = [1, 2, 3]
        results, failures = client.call_batch_with_retry(
            items, lambda x: x * 2
        )
        assert results == [2, 4, 6]
        assert failures == []

    def test_call_batch_with_retry_partial_failure(self):
        client = RetryableAPIClient(max_retries=1, initial_delay=0.01)

        def process(x):
            if x == 2:
                raise ValueError("bad item")
            return x * 10

        results, failures = client.call_batch_with_retry(
            [1, 2, 3], process, continue_on_failure=True
        )
        assert results == [10, 30]
        assert len(failures) == 1
        assert failures[0]["index"] == 1

    def test_call_batch_stops_on_failure(self):
        client = RetryableAPIClient(max_retries=1, initial_delay=0.01)

        def process(x):
            if x == 2:
                raise ValueError("stop here")
            return x

        with pytest.raises(ValueError, match="stop here"):
            client.call_batch_with_retry(
                [1, 2, 3], process, continue_on_failure=False
            )
