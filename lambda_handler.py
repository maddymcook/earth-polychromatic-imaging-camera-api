"""
AWS Lambda handler for NASA EPIC image downloader.
Configurable via event parameters or environment variables.
"""

import contextlib
import json
import logging
import os
import subprocess  # noqa: S404
from datetime import datetime, timedelta, timezone
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Constants for Lambda timeout validation
MAX_RECOMMENDED_DAYS = 3
ESTIMATED_SECONDS_PER_DAY = 45


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


def build_command(event: dict[str, Any]) -> list[str]:
    """Build the epic_s3_downloader.py command with parameters."""
    start_date, end_date = get_date_range(event)

    cmd = [
        "python",
        "epic_s3_downloader.py",
        "--start-date",
        start_date,
        "--end-date",
        end_date,
    ]

    # S3 bucket (required)
    bucket = event.get("bucket", os.getenv("S3_BUCKET"))
    if not bucket:
        msg = "bucket parameter or S3_BUCKET environment variable required"
        raise ValueError(msg)
    cmd.extend(["--bucket", bucket])

    # Collection type
    collection = event.get("collection", os.getenv("COLLECTION", "natural"))
    cmd.extend(["--collection", collection])

    # Local directory (optional)
    if local_dir := event.get("local_dir", os.getenv("LOCAL_DIR")):
        cmd.extend(["--local-dir", local_dir])

    # Keep local files
    keep_local = event.get("keep_local", os.getenv("KEEP_LOCAL", "false").lower() == "true")
    if keep_local:
        cmd.append("--keep-local")

    # Local only (skip S3 upload entirely)
    local_only = event.get("local_only", os.getenv("LOCAL_ONLY", "false").lower() == "true")
    if local_only:
        cmd.append("--local-only")

    return cmd


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda handler for NASA EPIC image downloader.

    Event parameters (all optional):

    DATE OPTIONS (choose one approach):
    - start_date & end_date: Explicit date range (YYYY-MM-DD)
    - days_back & date_range_days: Relative date range from today

    OTHER OPTIONS:
    - bucket: S3 bucket name (required if S3_BUCKET env var not set)
    - collection: Image collection (natural, enhanced, aerosol, cloud)
    - local_dir: Local directory path
    - keep_local: Keep local files after upload (true/false)

    Environment variables (fallbacks):
    - S3_BUCKET: Default S3 bucket
    - COLLECTION: Default collection type
    - START_DATE/END_DATE: Default explicit date range
    - DAYS_BACK: Default days back from today
    - LOCAL_DIR: Default local directory
    - KEEP_LOCAL: Keep local files
    """
    logger.info("Lambda started with event: %s", json.dumps(event, default=str))
    logger.info("Request ID: %s", context.aws_request_id)

    start_time = datetime.now(tz=timezone.utc)

    try:
        # Build and execute the download command
        cmd = build_command(event)
        logger.info("Executing command: %s", " ".join(cmd))

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603

        end_time = datetime.now(tz=timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Parse output for image count (if available)
        stdout_lines = result.stdout.strip().split("\n")
        images_downloaded = 0
        for line in stdout_lines:
            if "Downloaded" in line and "images" in line:
                with contextlib.suppress(IndexError, ValueError):
                    images_downloaded = int(line.split()[1])

        response = {
            "statusCode": 200,
            "success": True,
            "message": "NASA EPIC images downloaded successfully",
            "details": {
                "execution_time_seconds": round(duration, 2),
                "images_downloaded": images_downloaded,
                "command": " ".join(cmd),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            "stdout": result.stdout,
            "stderr": result.stderr if result.stderr else None,
        }

        logger.info("Job completed successfully in %.2f seconds", duration)
        logger.info("Downloaded %d images", images_downloaded)

        return response

    except subprocess.CalledProcessError as e:
        end_time = datetime.now(tz=timezone.utc)
        error_details = {
            "exit_code": e.returncode,
            "command": " ".join(cmd) if "cmd" in locals() else "Unknown",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "execution_time_seconds": (end_time - start_time).total_seconds(),
        }

        logger.exception("Command failed with exit code %d", e.returncode)
        if e.stdout:
            logger.info("Command STDOUT: %s", e.stdout)
        if e.stderr:
            logger.warning("Command STDERR: %s", e.stderr)

        return {
            "statusCode": 500,
            "success": False,
            "error": "Command execution failed",
            "details": error_details,
        }

    except Exception as e:
        end_time = datetime.now(tz=timezone.utc)
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "execution_time_seconds": (end_time - start_time).total_seconds(),
        }

        logger.exception("Job failed with error")

        return {"statusCode": 500, "success": False, "error": str(e), "details": error_details}
