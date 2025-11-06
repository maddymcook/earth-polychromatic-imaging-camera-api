#!/usr/bin/env python3
"""NASA EPIC API Endpoint Verification Script.

This script tests all service endpoints to verify they work correctly.
Run this script to validate that all API endpoints are functioning properly.

Usage:
    python verify_endpoints.py

Requirements:
    - Install the package: pip install -e .
    - Or install dependencies: pip install -e .[dev]
"""

import sys

from src.earth_polychromatic_api.service import EpicApiService


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"ℹ️  {message}")


def test_natural_endpoints(service: EpicApiService) -> bool:
    """Test natural color imagery endpoints."""
    print_header("Testing Natural Color Imagery Endpoints")
    success_count = 0
    total_tests = 3

    try:
        # Test recent natural images
        print_info("Testing get_natural_recent_typed()...")
        recent_natural = service.get_natural_recent_typed()
        if len(recent_natural.root) > 0:
            print_success(f"Found {len(recent_natural.root)} recent natural images")
            print_info(f"Latest image: {recent_natural.root[0].image}")
            success_count += 1
        else:
            print_error("No recent natural images found")

        # Test natural images by date (using a recent date)
        test_date = "2023-10-15"  # Known date with data
        print_info(f"Testing get_natural_by_date_typed('{test_date}')...")
        try:
            dated_natural = service.get_natural_by_date_typed(test_date)
            print_success(f"Found {len(dated_natural.root)} natural images for {test_date}")
            if len(dated_natural.root) > 0:
                print_info(f"First image: {dated_natural.root[0].image}")
            success_count += 1
        except Exception as e:
            print_error(f"Date-specific natural images failed: {e}")

        # Test all available dates
        print_info("Testing get_natural_all_dates_typed()...")
        all_dates = service.get_natural_all_dates_typed()
        if len(all_dates.root) > 0:
            print_success(f"Found {len(all_dates.root)} available dates for natural images")
            print_info(f"Most recent date: {all_dates.root[0].date}")
            success_count += 1
        else:
            print_error("No available dates found for natural images")

    except Exception as e:
        print_error(f"Natural endpoints test failed: {e}")

    return success_count == total_tests


def test_enhanced_endpoints(service: EpicApiService) -> bool:
    """Test enhanced color imagery endpoints."""
    print_header("Testing Enhanced Color Imagery Endpoints")
    success_count = 0
    total_tests = 3

    try:
        # Test recent enhanced images
        print_info("Testing get_enhanced_recent_typed()...")
        recent_enhanced = service.get_enhanced_recent_typed()
        if len(recent_enhanced.root) > 0:
            print_success(f"Found {len(recent_enhanced.root)} recent enhanced images")
            print_info(f"Latest image: {recent_enhanced.root[0].image}")
            success_count += 1
        else:
            print_error("No recent enhanced images found")

        # Test enhanced images by date
        test_date = "2023-10-15"
        print_info(f"Testing get_enhanced_by_date_typed('{test_date}')...")
        try:
            dated_enhanced = service.get_enhanced_by_date_typed(test_date)
            print_success(f"Found {len(dated_enhanced.root)} enhanced images for {test_date}")
            if len(dated_enhanced.root) > 0:
                print_info(f"First image: {dated_enhanced.root[0].image}")
            success_count += 1
        except Exception as e:
            print_error(f"Date-specific enhanced images failed: {e}")

        # Test all available dates
        print_info("Testing get_enhanced_all_dates_typed()...")
        all_dates = service.get_enhanced_all_dates_typed()
        if len(all_dates.root) > 0:
            print_success(f"Found {len(all_dates.root)} available dates for enhanced images")
            print_info(f"Most recent date: {all_dates.root[0].date}")
            success_count += 1
        else:
            print_error("No available dates found for enhanced images")

    except Exception as e:
        print_error(f"Enhanced endpoints test failed: {e}")

    return success_count == total_tests


def test_aerosol_endpoints(service: EpicApiService) -> bool:
    """Test aerosol index imagery endpoints."""
    print_header("Testing Aerosol Index Imagery Endpoints")
    success_count = 0
    total_tests = 3

    try:
        # Test recent aerosol images
        print_info("Testing get_aerosol_recent_typed()...")
        recent_aerosol = service.get_aerosol_recent_typed()
        if len(recent_aerosol.root) > 0:
            print_success(f"Found {len(recent_aerosol.root)} recent aerosol images")
            print_info(f"Latest image: {recent_aerosol.root[0].image}")
            success_count += 1
        else:
            print_error("No recent aerosol images found")

        # Test aerosol images by date
        test_date = "2023-10-15"
        print_info(f"Testing get_aerosol_by_date_typed('{test_date}')...")
        try:
            dated_aerosol = service.get_aerosol_by_date_typed(test_date)
            print_success(f"Found {len(dated_aerosol.root)} aerosol images for {test_date}")
            if len(dated_aerosol.root) > 0:
                print_info(f"First image: {dated_aerosol.root[0].image}")
            success_count += 1
        except Exception as e:
            print_error(f"Date-specific aerosol images failed: {e}")

        # Test all available dates
        print_info("Testing get_aerosol_all_dates_typed()...")
        all_dates = service.get_aerosol_all_dates_typed()
        if len(all_dates.root) > 0:
            print_success(f"Found {len(all_dates.root)} available dates for aerosol images")
            print_info(f"Most recent date: {all_dates.root[0].date}")
            success_count += 1
        else:
            print_error("No available dates found for aerosol images")

    except Exception as e:
        print_error(f"Aerosol endpoints test failed: {e}")

    return success_count == total_tests


def test_cloud_endpoints(service: EpicApiService) -> bool:
    """Test cloud fraction imagery endpoints."""
    print_header("Testing Cloud Fraction Imagery Endpoints")
    success_count = 0
    total_tests = 3

    try:
        # Test recent cloud images
        print_info("Testing get_cloud_recent_typed()...")
        recent_cloud = service.get_cloud_recent_typed()
        if len(recent_cloud.root) > 0:
            print_success(f"Found {len(recent_cloud.root)} recent cloud images")
            print_info(f"Latest image: {recent_cloud.root[0].image}")
            success_count += 1
        else:
            print_error("No recent cloud images found")

        # Test cloud images by date
        test_date = "2023-10-15"
        print_info(f"Testing get_cloud_by_date_typed('{test_date}')...")
        try:
            dated_cloud = service.get_cloud_by_date_typed(test_date)
            print_success(f"Found {len(dated_cloud.root)} cloud images for {test_date}")
            if len(dated_cloud.root) > 0:
                print_info(f"First image: {dated_cloud.root[0].image}")
            success_count += 1
        except Exception as e:
            print_error(f"Date-specific cloud images failed: {e}")

        # Test all available dates
        print_info("Testing get_cloud_all_dates_typed()...")
        all_dates = service.get_cloud_all_dates_typed()
        if len(all_dates.root) > 0:
            print_success(f"Found {len(all_dates.root)} available dates for cloud images")
            print_info(f"Most recent date: {all_dates.root[0].date}")
            success_count += 1
        else:
            print_error("No available dates found for cloud images")

    except Exception as e:
        print_error(f"Cloud endpoints test failed: {e}")

    return success_count == total_tests


def test_client_methods(service: EpicApiService) -> bool:
    """Test raw client methods (non-typed)."""
    print_header("Testing Raw Client Methods")
    success_count = 0
    total_tests = 2

    try:
        # Test build_image_url method
        print_info("Testing build_image_url()...")
        url = service.client.build_image_url(
            collection="natural",
            date="2023-10-15",
            image_name="epic_1b_20231015123456",
            format_type="png",
        )
        expected_parts = ["natural", "2023", "10", "15", "png", "epic_1b_20231015123456.png"]
        if all(part in url for part in expected_parts):
            print_success("Image URL construction works correctly")
            print_info(f"Sample URL: {url}")
            success_count += 1
        else:
            print_error(f"Image URL construction failed. Got: {url}")

        # Test raw client method
        print_info("Testing raw client get_natural_recent()...")
        raw_data = service.client.get_natural_recent()
        if isinstance(raw_data, list) and len(raw_data) > 0:
            print_success(f"Raw client method returned {len(raw_data)} items")
            print_info(f"First item keys: {list(raw_data[0].keys())}")
            success_count += 1
        else:
            print_error("Raw client method failed or returned no data")

    except Exception as e:
        print_error(f"Client methods test failed: {e}")

    return success_count == total_tests


def test_model_validation(service: EpicApiService) -> bool:
    """Test Pydantic model validation."""
    print_header("Testing Pydantic Model Validation")
    success_count = 0
    total_tests = 2

    try:
        # Test that models validate correctly
        print_info("Testing model validation with real data...")
        recent_natural = service.get_natural_recent_typed()

        if len(recent_natural.root) > 0:
            first_image = recent_natural.root[0]
            print_success("Natural image model validation passed")
            print_info(f"Image ID: {first_image.identifier}")
            print_info(f"Caption: {first_image.caption[:50]}...")
            coords = first_image.centroid_coordinates
            print_info(f"Coordinates: lat={coords.lat:.2f}, lon={coords.lon:.2f}")
            success_count += 1
        else:
            print_error("No natural images available for model validation")

        # Test iteration and indexing
        print_info("Testing model collection methods...")
        if len(recent_natural.root) > 0:
            # Test iteration
            count = sum(1 for _ in recent_natural)
            # Test indexing
            first_item = recent_natural[0]
            # Test length
            length = len(recent_natural)

            if count == length and first_item.identifier:
                print_success("Model collection methods work correctly")
                print_info(f"Collection length: {length}, iteration count: {count}")
                success_count += 1
            else:
                print_error("Model collection methods failed")
        else:
            print_error("Cannot test model collection methods without data")

    except Exception as e:
        print_error(f"Model validation test failed: {e}")

    return success_count == total_tests


def main() -> int:
    """Main function to run all endpoint tests."""
    print_header("NASA EPIC API Endpoint Verification")
    print_info("This script will test all service endpoints to verify they work correctly.")
    print_info("Make sure you have internet connectivity to reach the NASA EPIC API.")

    try:
        # Initialize the service
        print_info("Initializing EPIC API Service...")
        service = EpicApiService()
        print_success("Service initialized successfully")

        # Run all tests
        tests = [
            ("Natural Endpoints", test_natural_endpoints),
            ("Enhanced Endpoints", test_enhanced_endpoints),
            ("Aerosol Endpoints", test_aerosol_endpoints),
            ("Cloud Endpoints", test_cloud_endpoints),
            ("Client Methods", test_client_methods),
            ("Model Validation", test_model_validation),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func(service)
                results.append((test_name, result))
            except Exception as e:
                print_error(f"{test_name} failed with exception: {e}")
                results.append((test_name, False))

        # Print summary
        print_header("Test Results Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            if result:
                print_success(f"{test_name}: PASSED")
            else:
                print_error(f"{test_name}: FAILED")

        print(f"\nOverall Results: {passed}/{total} tests passed")

        if passed == total:
            print_success("🎉 All endpoints are working correctly!")
            return 0
        print_error(f"⚠️  {total - passed} test(s) failed. Check the output above for details.")
        return 1

    except Exception as e:
        print_error(f"Failed to initialize service: {e}")
        print_info("Make sure you have installed the package: pip install -e .")
        return 1


if __name__ == "__main__":
    sys.exit(main())
