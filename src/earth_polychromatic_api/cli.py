"""
Command-line interface for the NASA EPIC API client.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

try:
    import boto3  # type: ignore

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from earth_polychromatic_api.client import EpicApiClient
from earth_polychromatic_api.service import EpicApiService

console = Console()


def get_date_range(
    start_date: str | None,
    end_date: str | None,
    days_back: int | None,
    date_range_days: int | None,
) -> tuple[str, str]:
    """Calculate date range from parameters."""
    if start_date and end_date:
        return start_date, end_date

    if days_back is not None or date_range_days is not None:
        days_back = days_back or 1
        date_range_days = date_range_days or 1
        end_dt = datetime.now(tz=timezone.utc) - timedelta(days=days_back)
        start_dt = end_dt - timedelta(days=date_range_days - 1)
        return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")

    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    return date_str, date_str


@click.group()
@click.version_option()
def main() -> None:
    """NASA EPIC API command-line tools."""


@main.command()
@click.option("--date", help="Date (YYYY-MM-DD), defaults to yesterday")
@click.option(
    "--collection",
    type=click.Choice(["natural", "enhanced", "aerosol", "cloud"]),
    default="natural",
    help="Image collection",
)
@click.option("--bucket", help="S3 bucket for upload")
@click.option(
    "--local-dir",
    type=click.Path(path_type=Path),
    help="Local directory (default: nasa_epic_images)",
)
@click.option("--local-only", is_flag=True, help="Download only, no S3")
def download_images(
    date: str | None,
    collection: str,
    bucket: str | None,
    local_dir: Path | None,
    local_only: bool,
) -> None:
    """Download NASA EPIC images."""
    if not local_only and not bucket:
        console.print("[red]Error: --bucket required (or use --local-only)[/red]")
        raise click.Abort()

    if not local_dir:
        local_dir = Path("nasa_epic_images")

    date_str = date or (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    client = EpicApiClient()

    # Get images
    collection_methods = {
        "natural": client.get_natural_by_date,
        "enhanced": client.get_enhanced_by_date,
        "aerosol": client.get_aerosol_by_date,
        "cloud": client.get_cloud_by_date,
    }

    images = collection_methods[collection](date_str)

    if not images:
        console.print(f"No {collection} images found for {date_str}")
        return

    console.print(f"Found {len(images)} {collection} images for {date_str}")

    # Create directories
    date_path = Path(date_str.replace("-", "/"))
    full_local_dir = local_dir / collection / date_path
    full_local_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    uploaded = 0

    for image_data in images:
        image_name = image_data["image"]

        # Build filename based on collection
        if collection == "cloud":
            filename = f"epic_cloudfraction_{image_name.split('_')[-1]}.png"
        elif collection == "aerosol":
            filename = f"epic_aerosol_{image_name.split('_')[-1]}.png"
        else:
            filename = f"{image_name}.png"

        # Download image
        image_url = client.build_image_url(collection, image_data["date"], image_name, "png")
        local_file = full_local_dir / filename

        try:
            response = client.session.get(image_url)
            response.raise_for_status()

            with local_file.open("wb") as f:
                f.write(response.content)

            downloaded += 1
            console.print(f"✅ Downloaded {filename}")

            # Upload to S3 if requested
            if not local_only and bucket and HAS_BOTO3:
                s3_key = f"nasa-epic/{collection}/{date_path}/{filename}"
                try:
                    s3_client = boto3.client("s3")
                    s3_client.upload_file(str(local_file), bucket, s3_key)
                    uploaded += 1
                    console.print(f"📤 Uploaded to s3://{bucket}/{s3_key}")
                except Exception as e:
                    console.print(f"❌ S3 upload failed: {e}")
            elif not local_only and not HAS_BOTO3:
                console.print("❌ boto3 not available for S3 upload")

        except Exception as e:
            console.print(f"❌ Error downloading {filename}: {e}")
            continue

    # Summary
    console.print(f"\n✅ Downloaded {downloaded} images to {local_dir}")
    if not local_only:
        console.print(f"📤 Uploaded {uploaded} images to S3")


@main.command()
@click.option("--date", help="Date (YYYY-MM-DD), defaults to yesterday")
@click.option(
    "--collection",
    type=click.Choice(["natural", "enhanced", "aerosol", "cloud"]),
    default="natural",
    help="Image collection",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option("--output-file", type=click.Path(), help="Save to file")
def get_metadata(
    date: str | None,
    collection: str,
    output_format: str,
    output_file: str | None,
) -> None:
    """Get metadata for NASA EPIC images."""
    date_str = date or (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    service = EpicApiService()

    # Get images using service for typed access
    service_methods = {
        "natural": service.get_natural_by_date_typed,
        "enhanced": service.get_enhanced_by_date_typed,
        "aerosol": service.get_aerosol_by_date_typed,
        "cloud": service.get_cloud_by_date_typed,
    }

    response = service_methods[collection](date_str)
    images = response.root  # type: ignore

    if not images:
        console.print(f"No {collection} images found for {date_str}")
        return

    # Build metadata
    metadata = []
    for image in images:
        data = {
            "date": date_str,
            "collection": collection,
            "image_name": image.image,
            "caption": image.caption,
            "centroid_lat": image.centroid_coordinates.lat,
            "centroid_lon": image.centroid_coordinates.lon,
            "version": image.version,
        }
        metadata.append(data)

    # Output results
    if output_format == "json":
        result = {
            "metadata": metadata,
            "total_images": len(metadata),
            "date": date_str,
            "collection": collection,
        }
        output_json = json.dumps(result, indent=2)

        if output_file:
            Path(output_file).write_text(output_json)
            console.print(f"Metadata saved to {output_file}")
        else:
            click.echo(output_json)
    else:
        # Table output
        table = Table(title=f"EPIC {collection.title()} Images - {date_str}")
        table.add_column("Image", style="green")
        table.add_column("Caption", style="yellow")
        table.add_column("Lat/Lon", style="blue")
        table.add_column("Version", style="magenta")

        for item in metadata:
            caption = item["caption"][:40] + "..." if len(item["caption"]) > 40 else item["caption"]
            table.add_row(
                item["image_name"],
                caption,
                f"{item['centroid_lat']:.2f}, {item['centroid_lon']:.2f}",
                item["version"],
            )

        console.print(table)

        if output_file:
            result = {
                "metadata": metadata,
                "total_images": len(metadata),
                "date": date_str,
                "collection": collection,
            }
            Path(output_file).write_text(json.dumps(result, indent=2))
            console.print(f"Metadata also saved to {output_file}")


if __name__ == "__main__":
    main()
