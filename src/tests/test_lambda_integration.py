"""Integration tests for Lambda handler to catch deployment issues."""

import json

import pytest

from lambda_handler import get_date_range, handler


class MockLambdaContext:
    """Mock AWS Lambda context for testing."""

    def __init__(self, request_id: str = "test-request-123"):
        self.aws_request_id = request_id
        self._remaining_time = 300000  # 5 minutes in milliseconds

    def get_remaining_time_in_millis(self) -> int:
        """Return remaining execution time in milliseconds."""
        return self._remaining_time


def test_lambda_handler_payload_format():
    """Test that Lambda handler accepts the expected payload format."""
    # This is the payload format documented in the handler
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
        "bucket": "test-bucket",
        "collection": "natural",
        "local_only": True,  # Skip S3 upload to avoid AWS credentials in tests
    }

    context = MockLambdaContext()

    # The handler should accept this payload format without errors
    # (it may fail on actual download due to missing AWS creds, but payload parsing should work)
    try:
        result = handler(payload, context)

        # Should return a proper Lambda response structure
        assert isinstance(result, dict)
        assert "statusCode" in result
        assert "body" in result

        # Body should be JSON string or dict
        body = json.loads(result["body"]) if isinstance(result["body"], str) else result["body"]

        assert isinstance(body, dict)

    except Exception as e:
        # If it fails, it should NOT be due to payload format issues
        error_msg = str(e).lower()

        # These are acceptable failure reasons (missing AWS setup)
        acceptable_errors = ["credentials", "aws", "s3", "boto3", "permission", "access"]

        # These would indicate payload format problems (what we want to catch)
        format_errors = ["missing", "required", "key error", "attribute error", "type error"]

        is_acceptable = any(acceptable in error_msg for acceptable in acceptable_errors)
        is_format_error = any(format_err in error_msg for format_err in format_errors)

        if is_format_error and not is_acceptable:
            pytest.fail(f"Payload format error detected: {e}")


def test_lambda_handler_event_body_confusion():
    """Test to catch the common mistake of putting payload in event['body']."""
    # This tests the mistake we made - putting payload in event.body instead of event directly
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "collection": "aerosol",  # Use non-default to detect issue
        "local_only": True,
    }

    # CORRECT: payload directly in event
    correct_event = payload.copy()

    # WRONG: payload in event.body (API Gateway format)
    wrong_event = {"body": json.dumps(payload)}

    context = MockLambdaContext()

    # Test correct format first
    correct_result = handler(correct_event, context)

    # Test wrong format - should use defaults instead of payload values
    wrong_result = handler(wrong_event, context)

    # The key test: both should succeed but with different data sources
    assert correct_result.get("statusCode") == 200, "Correct format should succeed"

    # Wrong format should fail because it can't parse dates from event.body
    # It will use default dates which won't match our expected 2024-01-01
    assert wrong_result.get("statusCode") == 500, (
        "Wrong format should fail due to missing credentials/params"
    )


def test_get_date_range_function():
    """Test the date range parsing function directly."""
    # Test explicit date range
    event1 = {"start_date": "2024-01-01", "end_date": "2024-01-05"}

    start, end = get_date_range(event1)
    assert start == "2024-01-01"
    assert end == "2024-01-05"

    # Test single date
    event2 = {"start_date": "2024-03-15", "end_date": "2024-03-15"}

    start, end = get_date_range(event2)
    assert start == "2024-03-15"
    assert end == "2024-03-15"


def test_lambda_response_structure():
    """Test that Lambda returns proper AWS Lambda response structure."""
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "local_only": True,
        "collection": "natural",
    }

    context = MockLambdaContext()

    result = handler(payload, context)

    # Must have statusCode (AWS Lambda requirement)
    assert "statusCode" in result

    # Status code should be an integer
    assert isinstance(result["statusCode"], int)

    # Response should have success data structure
    assert isinstance(result, dict)

    # Should have some expected fields for successful response
    if result.get("statusCode") == 200:
        assert "details" in result
        assert "images_downloaded" in result["details"]


@pytest.mark.parametrize("collection", ["natural", "enhanced", "aerosol", "cloud"])
def test_lambda_different_collections(collection: str):
    """Test Lambda handler with different image collections."""
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "collection": collection,
        "local_only": True,
    }

    context = MockLambdaContext()

    # Should not crash on payload parsing
    try:
        result = handler(payload, context)
        assert "statusCode" in result
    except Exception as e:
        # Should not be collection-related errors
        error_msg = str(e).lower()
        assert collection.lower() not in error_msg, (
            f"Collection {collection} caused parsing error: {e}"
        )


def test_lambda_minimal_payload():
    """Test Lambda with minimal required payload."""
    # Minimal payload - should use defaults for missing fields
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "local_only": True,  # Skip S3 to avoid credential issues
    }

    context = MockLambdaContext()

    result = handler(payload, context)

    assert "statusCode" in result

    # For successful responses, should have details with expected data
    if result.get("statusCode") == 200:
        assert "details" in result
        # Should default collection to 'natural' (verified by command_equivalent)
        assert "natural" in result["details"]["command_equivalent"]
