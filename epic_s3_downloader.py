"""NASA EPIC Image Download Script.

Downloads NASA EPIC images between date ranges. Can optionally upload to S3 or just save locally.

Usage:
    # Local download only
    python epic_s3_downloader.py --start-date 2023-10-01 --end-date 2023-10-31 --local-only

    # Download and upload to S3
    python epic_s3_downloader.py --start-date 2023-10-01 --end-date 2023-10-31 --bucket my-bucket

Requirements:
    pip install requests
    pip install boto3  # Only needed for S3 uploads
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

from src.earth_polychromatic_api.service import EpicApiService


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download EPIC images locally or to S3")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--bucket", help="S3 bucket name (optional, for S3 upload)")
    parser.add_argument(
        "--collection",
        choices=["natural", "enhanced", "aerosol", "cloud"],
        default="natural",
        help="Image collection type",
    )
    parser.add_argument(
        "--local-dir", default="./nasa_epic_images", help="Local download directory"
    )
    parser.add_argument(
        "--local-only", action="store_true", help="Download locally only (no S3 upload)"
    )
    parser.add_argument(
        "--keep-local",
        action="store_true",
        help="Keep local files after S3 upload (ignored if --local-only)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.local_only and not args.bucket:
        print("Error: Must specify either --local-only or --bucket for S3 upload")
        return 1

    # Parse dates
    try:
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
        end = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as e:
        print(f"Invalid date format: {e}")
        return 1

    # Initialize services
    try:
        service = EpicApiService()
        s3_client = None

        if not args.local_only and args.bucket:
            import boto3

            s3_client = boto3.client("s3")
            s3_client.head_bucket(Bucket=args.bucket)

    except Exception as e:
        print(f"Setup failed: {e}")
        return 1

    local_dir = Path(args.local_dir)
    total_downloaded = 0
    total_uploaded = 0

    # Process each date
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        print(f"Processing {args.collection} images for {date_str}")

        try:
            # Get images for the date
            method_map = {
                "natural": service.get_natural_by_date_typed,
                "enhanced": service.get_enhanced_by_date_typed,
                "aerosol": service.get_aerosol_by_date_typed,
                "cloud": service.get_cloud_by_date_typed,
            }

            images_response = method_map[args.collection](date_str)
            images = images_response.root

            if not images:
                print(f"  No images found for {date_str}")
                current += timedelta(days=1)
                continue

            print(f"  Found {len(images)} images")

            for image in images:
                # Build URLs and paths
                image_url = service.client.build_image_url(
                    collection=args.collection,
                    date=date_str,
                    image_name=image.image,
                    format_type="png",
                )

                filename = f"{image.image}.png"
                local_path = local_dir / args.collection / date_str.replace("-", "/") / filename
                s3_key = f"nasa-epic/{args.collection}/{date_str.replace('-', '/')}/{filename}"

                # Download
                try:
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()

                    with local_path.open("wb") as f:
                        f.write(response.content)

                    print(f"  ✅ Downloaded {filename}")
                    total_downloaded += 1

                    # Upload to S3 if not local-only
                    if not args.local_only and s3_client:
                        s3_client.upload_file(str(local_path), args.bucket, s3_key)
                        total_uploaded += 1
                        print(f"  ☁️  Uploaded {filename}")

                        # Clean up if requested
                        if not args.keep_local:
                            local_path.unlink()

                except requests.RequestException as e:
                    print(f"  ❌ Failed {filename}: {e}")

        except Exception as e:
            print(f"  Error processing {date_str}: {e}")

        current += timedelta(days=1)

    # Summary
    if args.local_only:
        print(f"\nCompleted: {total_downloaded} images downloaded to {local_dir}/")
    else:
        print(
            f"\nCompleted: {total_downloaded} images downloaded, {total_uploaded} uploaded to s3://{args.bucket}/nasa-epic/"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
