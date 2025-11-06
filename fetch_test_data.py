#!/usr/bin/env python3
"""Script to fetch fresh real data from NASA EPIC API for testing.

This script fetches current real data from the NASA EPIC API endpoints
and saves them as JSON files for use in our tests. This ensures our
test data is always realistic and up-to-date.
"""

import json
import sys
from pathlib import Path

import requests

# Base URL for NASA EPIC API
BASE_URL = "https://epic.gsfc.nasa.gov/api"

# Output directory for test data
TEST_DATA_DIR = Path(__file__).parent / "test_datasets"


def fetch_endpoint_data(endpoint: str, filename: str) -> bool:
    """Fetch data from an API endpoint and save to file.

    Args:
        endpoint: The API endpoint URL
        filename: Name of the file to save the data to

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Fetching data from {endpoint}...")
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()

        data = response.json()
        if not data:
            print(f"  Warning: Empty response from {endpoint}")
            return False

        # Save the data
        output_file = TEST_DATA_DIR / filename
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved {len(data)} items to {filename}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {endpoint}: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"  ✗ Error parsing JSON from {endpoint}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error with {endpoint}: {e}")
        return False


def main():
    """Fetch fresh data from all NASA EPIC API endpoints."""
    print("🌍 Fetching fresh data from NASA EPIC API...")

    # Ensure test data directory exists
    TEST_DATA_DIR.mkdir(exist_ok=True)

    # Define endpoints and their output filenames
    endpoints = [
        # Natural color endpoints
        (f"{BASE_URL}/natural", "natural_recent_response.json"),
        (f"{BASE_URL}/natural/all", "natural_all_dates_response.json"),
        # Enhanced color endpoints
        (f"{BASE_URL}/enhanced", "enhanced_recent_response.json"),
        (f"{BASE_URL}/enhanced/all", "enhanced_all_dates_response.json"),
        # Aerosol index endpoints
        (f"{BASE_URL}/aerosol", "aerosol_recent_response.json"),
        (f"{BASE_URL}/aerosol/all", "aerosol_all_dates_response.json"),
        # Cloud fraction endpoints
        (f"{BASE_URL}/cloud", "cloud_recent_response.json"),
        (f"{BASE_URL}/cloud/all", "cloud_all_dates_response.json"),
    ]

    # Fetch data from each endpoint
    success_count = 0
    for endpoint, filename in endpoints:
        if fetch_endpoint_data(endpoint, filename):
            success_count += 1

    # Try to get date-specific data if recent data is available
    try:
        # Get a recent date from natural all dates
        all_dates_response = requests.get(f"{BASE_URL}/natural/all", timeout=30)
        if all_dates_response.status_code == 200:
            all_dates = all_dates_response.json()
            if all_dates and len(all_dates) > 0:
                # Use the most recent date
                recent_date = all_dates[0]["date"]
                print(f"Using recent date {recent_date} for date-specific endpoints...")

                # Fetch date-specific data
                date_endpoints = [
                    (f"{BASE_URL}/natural/date/{recent_date}", "natural_date_response.json"),
                    (f"{BASE_URL}/enhanced/date/{recent_date}", "enhanced_date_response.json"),
                ]

                for endpoint, filename in date_endpoints:
                    if fetch_endpoint_data(endpoint, filename):
                        success_count += 1

    except Exception as e:
        print(f"Note: Could not fetch date-specific data: {e}")

    print(f"\n✨ Completed! Successfully fetched {success_count} datasets.")

    if success_count == 0:
        print("❌ No data was successfully fetched. Check your internet connection.")
        sys.exit(1)
    else:
        print("🎉 Fresh test data is ready!")


if __name__ == "__main__":
    main()
