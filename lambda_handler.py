"""
AWS Lambda handler for NASA EPIC image downloader.
Configurable via event parameters or environment variables.
"""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any
from pathlib import Path


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Constants for Lambda timeout validation
MAX_RECOMMENDED_DAYS = 3
ESTIMATED_SECONDS_PER_DAY = 45
MIN_RECOMMENDED_TIMEOUT_SECONDS = 60

# Constants for output parsing
MIN_COMPLETION_LINE_PARTS = 2


def validate_date_range_for_lambda(start_date: str, end_date: str, context: Any) -> None:
    """Validate date range is appropriate for Lambda execution limits."""
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_span = (end_dt - start_dt).days + 1

    # Get remaining time in milliseconds, convert to seconds
    remaining_time = context.get_remaining_time_in_millis() / 1000

    # Estimate: roughly 30-60 seconds per day for cloud images (which can be numerous)
    # Conservative estimate: 45 seconds per day
    estimated_time = days_span * ESTIMATED_SECONDS_PER_DAY

    if estimated_time > remaining_time * 0.8:  # Use 80% of remaining time as safety margin
        logger.warning(
            "Date range may exceed Lambda timeout: %d days estimated %d seconds, "
            "remaining %.1f seconds. Consider splitting into smaller ranges.",
            days_span,
            estimated_time,
            remaining_time,
        )

        if days_span > MAX_RECOMMENDED_DAYS:
            logger.error(
                "Date range too large for Lambda (%d days). "
                "Recommend maximum %d days per invocation for reliable execution.",
                days_span,
                MAX_RECOMMENDED_DAYS,
            )
            error_msg = (
                f"Date range too large ({days_span} days). Lambda may timeout. "
                f"Maximum recommended: {MAX_RECOMMENDED_DAYS} days per invocation. "
                f"Split into smaller ranges or increase timeout beyond {remaining_time:.0f}s."
            )
            raise ValueError(error_msg)


def get_date_range(event: dict[str, Any]) -> tuple[str, str]:
    """
    Get date range from event parameters or calculate default.
    Priority:
    1. Explicit dates (start_date/end_date)
    2. Relative dates (days_back/date_range_days)
    3. Environment variables (START_DATE/END_DATE)
    4. Default to yesterday (1 day back, 1 day range)
    """
    # Priority 1: Check explicit date parameters first
    start_date = event.get("start_date")
    end_date = event.get("end_date")

    if start_date and end_date:
        logger.info("Using explicit date range: %s to %s", start_date, end_date)
        return start_date, end_date

    # Priority 2: Check relative date parameters
    days_back = event.get("days_back")
    date_range_days = event.get("date_range_days")

    if days_back is not None or date_range_days is not None:
        days_back = int(days_back or 1)  # Default to 1 day back
        date_range_days = int(date_range_days or 1)  # Default to 1 day range

        # Calculate end date (days_back from today)
        end_date_obj = datetime.now(tz=timezone.utc) - timedelta(days=days_back)
        # Calculate start date (date_range_days before end date)
        start_date_obj = end_date_obj - timedelta(days=date_range_days - 1)

        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")

        logger.info(
            "Using relative dates: %d days back, %d day range (%s to %s)",
            days_back,
            date_range_days,
            start_date,
            end_date,
        )
        return start_date, end_date

    # Priority 3: Check environment variables for explicit dates
    env_start = os.getenv("START_DATE")
    env_end = os.getenv("END_DATE")

    if env_start and env_end:
        logger.info("Using environment date range: %s to %s", env_start, env_end)
        return env_start, env_end

    # Priority 4: Default behavior (yesterday only)
    default_days_back = int(os.getenv("DAYS_BACK", "1"))
    target_date = datetime.now(tz=timezone.utc) - timedelta(days=default_days_back)
    date_str = target_date.strftime("%Y-%m-%d")

    logger.info("Using default date: %s (%d days back)", date_str, default_days_back)
    return date_str, date_str


def run_download_for_date(
    date_str: str,
    collection: str,
    bucket: str | None,
    local_dir: str | None,
    local_only: bool,
) -> tuple[int, int]:
    """Run download for a single date using CLI commands."""
    try:
        # Build the epic-images command
        cmd = ["epic-images", "--date", date_str, "--collection", collection]

        if local_dir:
            cmd.extend(["--local-dir", local_dir])

        if local_only:
            cmd.append("--local-only")
        elif bucket:
            cmd.extend(["--bucket", bucket])
        else:
            raise ValueError("bucket required when not using local-only mode")

        # Execute the command
        logger.info("Executing command: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # noqa: S603

        if result.returncode != 0:
            logger.error("Command failed with code %d", result.returncode)
            logger.error("stderr: %s", result.stderr)
            return 0, 0

        # Parse output to extract counts
        output = result.stdout
        logger.info("Command output: %s", output.strip())

        # Look for success message like "✅ Downloaded 10 images to /path"
        downloaded = 0
        uploaded = 0

        for line in output.split("\n"):
            if "✅ Downloaded" in line and "images" in line:
                # Extract number from line like "✅ Downloaded 10 images to /path"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "Downloaded" and i + 1 < len(parts):
                        try:
                            downloaded = int(parts[i + 1])
                            break
                        except ValueError:
                            continue
            if "📤 Uploaded" in line and "images" in line:
                # Extract upload count
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "Uploaded" and i + 1 < len(parts):
                        try:
                            uploaded = int(parts[i + 1])
                            break
                        except ValueError:
                            continue

        return downloaded, uploaded

    except subprocess.TimeoutExpired:
        logger.error("Command timeout for date %s", date_str)
        return 0, 0
    except Exception:
        logger.exception("Error downloading for date %s", date_str)
        return 0, 0


def execute_downloads(event: dict[str, Any]) -> tuple[int, int, str]:
    """Execute image downloads using the new CLI."""
    start_date, end_date = get_date_range(event)

    # S3 bucket (required unless local_only)
    local_only = event.get("local_only", os.getenv("LOCAL_ONLY", "false").lower() == "true")
    bucket = event.get("bucket", os.getenv("S3_BUCKET"))
    if not bucket and not local_only:
        msg = "bucket parameter or S3_BUCKET environment variable required (unless local_only=true)"
        raise ValueError(msg)

    # Collection type
    collection = event.get("collection", os.getenv("COLLECTION", "natural"))

    # Local directory (use /tmp in Lambda environment)
    local_dir = event.get("local_dir", os.getenv("LOCAL_DIR"))
    if not local_dir and os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        # Lambda environment - use writable temp directory
        temp_dir = tempfile.gettempdir()  # Returns /tmp on Lambda
        local_dir = f"{temp_dir}/nasa_epic_images"
        logger.info("Using Lambda temp directory: %s", local_dir)

    # Keep local files feature not implemented yet

    # Process date range
    current_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    total_downloaded = 0
    total_uploaded = 0
    dates_processed = []

    while current_date <= end_date_dt:
        date_str = current_date.strftime("%Y-%m-%d")
        logger.info("Processing date: %s", date_str)

    from earth_polychromatic_api.cli import download_images_programmatic
    
    downloaded, uploaded = download_images_programmatic(
        date=date_str,
        collection=collection,
        bucket=bucket,
        local_dir=Path(local_dir) if local_dir else None,
        local_only=local_only
    )


        total_downloaded += downloaded
        total_uploaded += uploaded
        dates_processed.append(date_str)

        current_date += timedelta(days=1)

    command_equivalent = f"epic-images --date {start_date} --collection {collection}"
    if bucket:
        command_equivalent += f" --bucket {bucket}"
    if local_dir:
        command_equivalent += f" --local-dir {local_dir}"
    if local_only:
        command_equivalent += " --local-only"

    return total_downloaded, total_uploaded, command_equivalent


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda handler for NASA EPIC image downloader.

    Uses the epic-images CLI command in Docker container to download images.
    All event parameters are passed through to the CLI.

    Example payload:
    {
        "start_date": "2024-01-01",
        "end_date": "2024-01-05",
        "bucket": "my-s3-bucket",
        "collection": "aerosol",
        "local_only": false
    }

    Event parameters (all optional):
    - start_date & end_date: Explicit date range (YYYY-MM-DD)
    - days_back & date_range_days: Relative date range from today
    - bucket: S3 bucket name (required unless local_only=true)
    - collection: Image collection (natural, enhanced, aerosol, cloud)
    - local_dir: Local directory path
    - local_only: Skip S3 upload, download only

    Environment variables (fallbacks):
    - S3_BUCKET: Default S3 bucket
    - COLLECTION: Default collection type
    - START_DATE/END_DATE: Default explicit date range
    - DAYS_BACK: Default days back from today
    - LOCAL_DIR: Default local directory
    """
    logger.info("Lambda started with event: %s", json.dumps(event, default=str))
    request_id = getattr(context, "aws_request_id", "local-test")
    logger.info("Request ID: %s", request_id)

    # Check Lambda timeout configuration
    timeout_ms = context.get_remaining_time_in_millis()
    timeout_seconds = timeout_ms / 1000
    logger.info("Lambda timeout: %.1f seconds remaining", timeout_seconds)

    # Allow environment variable to override minimum timeout warning
    min_timeout = int(os.getenv("MIN_RECOMMENDED_TIMEOUT", MIN_RECOMMENDED_TIMEOUT_SECONDS))

    if timeout_seconds < min_timeout:
        logger.warning(
            "⚠️  Lambda timeout is short (%.1f seconds). "
            "Recommend increasing to %d+ seconds for reliable image downloads.",
            timeout_seconds,
            min_timeout,
        )

    start_time = datetime.now(tz=timezone.utc)

    try:
        # Execute downloads using new CLI integration
        images_downloaded, images_uploaded, command_equivalent = execute_downloads(event)
        logger.info("CLI execution: downloaded=%d, uploaded=%d", images_downloaded, images_uploaded)

        end_time = datetime.now(tz=timezone.utc)
        duration = (end_time - start_time).total_seconds()

        response = {
            "statusCode": 200,
            "success": True,
            "message": "NASA EPIC images downloaded successfully",
            "details": {
                "execution_time_seconds": round(duration, 2),
                "images_downloaded": images_downloaded,
                "images_uploaded": images_uploaded,
                "command_equivalent": command_equivalent,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
        }

        logger.info("Job completed successfully in %.2f seconds", duration)
        logger.info("Downloaded %d images, uploaded %d to S3", images_downloaded, images_uploaded)

        return response

    except Exception as e:
        end_time = datetime.now(tz=timezone.utc)
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "execution_time_seconds": (end_time - start_time).total_seconds(),
        }

        logger.exception("Download execution failed")

        return {
            "statusCode": 500,
            "success": False,
            "error": "Download execution failed",
            "details": error_details,
        }
