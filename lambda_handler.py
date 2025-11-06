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


def get_date_range(event: dict[str, Any]) -> tuple[str, str]:
    """
    Get date range from event parameters or calculate default.
    Priority: event params > environment vars > default (yesterday)
    """
    # Check event parameters first
    start_date = event.get("start_date")
    end_date = event.get("end_date")

    if start_date and end_date:
        return start_date, end_date

    # Check environment variables
    start_date = os.getenv("START_DATE")
    end_date = os.getenv("END_DATE")

    if start_date and end_date:
        return start_date, end_date

    # Default to yesterday (EPIC has processing delays)
    days_back = int(event.get("days_back", os.getenv("DAYS_BACK", "1")))
    target_date = datetime.now(tz=timezone.utc) - timedelta(days=days_back)
    date_str = target_date.strftime("%Y-%m-%d")

    logger.info("Using default date range: %s (going back %d days)", date_str, days_back)

    # Check if we want a date range
    date_range = int(event.get("date_range_days", os.getenv("DATE_RANGE_DAYS", "1")))
    if date_range > 1:
        end_date_obj = target_date
        start_date_obj = target_date - timedelta(days=date_range - 1)
        return start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d")

    return date_str, date_str


def build_command(event: dict[str, Any]) -> list[str]:
    """Build the epic_s3_downloader.py command with parameters."""
    start_date, end_date = get_date_range(event)

    cmd = [
        "python", "epic_s3_downloader.py",
        "--start-date", start_date,
        "--end-date", end_date,
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

    return cmd


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda handler for NASA EPIC image downloader.

    Event parameters (all optional):
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - bucket: S3 bucket name
    - collection: Image collection (natural, enhanced, aerosol, cloud)
    - days_back: How many days back from today (default: 1)
    - date_range_days: Number of days to download (default: 1)
    - local_dir: Local directory path
    - keep_local: Keep local files after upload (true/false)

    Environment variables (fallbacks):
    - S3_BUCKET: Default S3 bucket
    - COLLECTION: Default collection type
    - START_DATE/END_DATE: Default date range
    - DAYS_BACK: Default days back
    - DATE_RANGE_DAYS: Default date range
    - LOCAL_DIR: Default local directory
    - KEEP_LOCAL: Keep local files
    """
    print(f"Lambda started with event: {json.dumps(event, default=str)}")
    print(f"Request ID: {context.aws_request_id}")

    start_time = datetime.now()

    try:
        # Build and execute the download command
        cmd = build_command(event)
        print(f"Executing command: {' '.join(cmd)}")

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603

        end_time = datetime.now()
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
                "end_time": end_time.isoformat()
            },
            "stdout": result.stdout,
            "stderr": result.stderr if result.stderr else None
        }

        print(f"Job completed successfully in {duration:.2f} seconds")
        print(f"Downloaded {images_downloaded} images")

        return response

    except subprocess.CalledProcessError as e:
        error_details = {
            "exit_code": e.returncode,
            "command": " ".join(cmd) if 'cmd' in locals() else "Unknown",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "execution_time_seconds": (datetime.now() - start_time).total_seconds()
        }

        print(f"Command failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

        return {
            "statusCode": 500,
            "success": False,
            "error": "Command execution failed",
            "details": error_details
        }

    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "execution_time_seconds": (datetime.now() - start_time).total_seconds()
        }

        print(f"Job failed with error: {e}")

        return {
            "statusCode": 500,
            "success": False,
            "error": str(e),
            "details": error_details
        }
