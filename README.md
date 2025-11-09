# NASA EPIC API Client

A Python client for NASA's Earth Polychromatic Imaging Camera (EPIC) API with professional CLI tools and AWS Lambda integration.

## 🚀 CLI Tools

The package includes professional command-line tools for downloading NASA EPIC imagery:

### Installation & Setup

```bash
# Install the package (includes CLI tools)
pip install -e .

# Verify CLI tools are available
epic --help
epic-images --help
epic-metadata --help
```

### Quick Start

```bash
# Download yesterday's natural images locally
epic-images --local-only

# Download specific date to S3
epic-images --date 2024-11-01 --bucket my-bucket

# Get image metadata for yesterday
epic-metadata

# Download enhanced images to custom local directory
epic-images --date 2025-07-01 --collection enhanced --local-dir ./my_images --local-only
```

### CLI Commands

#### `epic-images` - Download NASA EPIC Images
Download NASA EPIC images with flexible options for date, collection type, and storage.

```bash
# Basic usage (downloads yesterday's natural images locally)
epic-images --local-only

# Specific date and collection (local download)
epic-images --date 2024-01-15 --collection enhanced --local-only

# Upload to S3 bucket
epic-images --date 2024-01-15 --bucket my-epic-bucket

# Custom local directory
epic-images --date 2024-01-15 --local-dir ./epic_data --local-only

# S3 upload with custom local directory (then upload)
epic-images --date 2024-01-15 --collection aerosol --bucket my-bucket --local-dir ./epic
```

**Options:**
- `--date` (YYYY-MM-DD): Date to download, defaults to yesterday
- `--collection`: Image type (`natural`, `enhanced`, `aerosol`, `cloud`)
- `--bucket`: S3 bucket for upload (optional)
- `--local-dir`: Local directory (default: `nasa_epic_images`)
- `--local-only`: Download only, skip S3 upload

#### `epic-metadata` - Get Image Metadata
Retrieve metadata for NASA EPIC images without downloading.

```bash
# Get yesterday's natural image metadata
epic-metadata

# Specific date and collection
epic-metadata --date 2024-01-15 --collection enhanced

# All available options
epic-metadata --date 2024-01-15 --collection aerosol
```

**Options:**
- `--date` (YYYY-MM-DD): Date for metadata, defaults to yesterday
- `--collection`: Image type (`natural`, `enhanced`, `aerosol`, `cloud`)

#### `epic` - Main Command Group
Access all NASA EPIC CLI tools through a unified interface.

```bash
# Show all available commands
epic --help

# Download images (same as epic-images)
epic download-images --date 2024-01-15 --bucket my-bucket

# Get metadata (same as epic-metadata)
epic get-metadata --date 2024-01-15 --collection enhanced

# Check version
epic --version
```

### CLI Features

- **Rich Terminal Output**: Beautiful tables and progress indicators using Rich library
- **Date Range Support**: Easy date specification with sensible defaults
- **Multiple Entry Points**: Use `epic`, `epic-images`, or `epic-metadata` commands
- **S3 Integration**: Direct upload to AWS S3 with organized folder structure
- **Error Handling**: Comprehensive error messages and validation
- **Flexible Storage**: Local-only mode or S3 upload with optional local retention

> **📅 Date Availability**: NASA EPIC images are available for recent dates (typically last few months). For testing, use recent dates like `2024-11-01` or omit `--date` to get yesterday's images automatically.

### CLI Examples

```bash
# Education: Download a week of natural images for analysis
for date in 2024-01-{15..21}; do
  epic-images --date $date --local-dir ./weekly_data --local-only
done

# Production: Automated daily S3 archival (yesterday's images)
epic-images --bucket nasa-epic-archive --collection natural

# Research: Compare different image types for same date
epic-images --date 2024-01-15 --collection natural --local-only
epic-images --date 2024-01-15 --collection enhanced --local-only
epic-images --date 2024-01-15 --collection aerosol --local-only

# Metadata analysis: Get image info before downloading
epic-metadata --date 2024-01-15 --collection natural > metadata.json
```

## 🎓 AWS Lambda Integration

The package includes full AWS Lambda support for serverless deployment:

## Versioning

This package uses automatic versioning based on Git tags:
- **Release versions**: When you create a Git tag (e.g., `v1.2.3`), that becomes the package version
- **Development versions**: Between releases, versions include commit info (e.g., `1.2.4.dev0+g1a2b3c4`)
- **CI/CD Integration**: GitHub Actions automatically uses the Git tag for publishing

To create a new release:
```bash
git tag v1.2.3
git push origin v1.2.3
# Creates GitHub release, which triggers CI/CD to publish with version 1.2.3
```

## Project Structure

```
earth-polychromatic-imaging-camera-api/
├── .github/workflows/
│   └── ci-cd.yml              # GitHub Actions CI/CD pipeline
├── src/
│   ├── earth_polychromatic_api/   # Main API package
│   │   ├── __init__.py           # Package initialization
│   │   ├── _version.py           # Auto-versioning with hatch-vcs
│   │   ├── cli.py               # Professional CLI tools
│   │   ├── client.py            # NASA EPIC API client
│   │   ├── models.py            # Pydantic data models
│   │   └── service.py           # Typed service layer
│   └── tests/                   # Comprehensive test suite
│       ├── __init__.py
│       ├── test_cli.py          # CLI tool unit tests
│       ├── test_epic_api.py     # API client tests
│       ├── test_lambda_basic.py # Lambda handler tests
│       ├── test_typed_methods.py # Typed service tests
│       └── test_datasets/       # Mock API response data
│           ├── natural_recent_response.json
│           ├── enhanced_date_response.json
│           ├── natural_all_dates_response.json
│           ├── aerosol_recent_response.json
│           ├── cloud_recent_response.json
│           ├── enhanced_all_dates_response.json
│           └── aerosol_all_dates_response.json
├── Dockerfile.lambda            # AWS Lambda container
├── lambda_handler.py           # AWS Lambda entry point
├── pyproject.toml             # Package config + CLI entry points
├── conftest.py                # Pytest configuration
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## Installation

### For Users (CLI Tools + API Client)
```bash
# Install the package with CLI tools
pip install -e .

# Verify installation
epic --version
epic --help
```

### For Development
```bash
# Install with test dependencies
pip install -r requirements-test.txt
pip install -e .
```

### Package Building
```bash
# Build distribution packages
python -m build

# The package uses hatch-vcs for automatic versioning:
# - Release versions from Git tags (v1.2.3 → 1.2.3)
# - Development versions with commit info (1.2.3.post4+g1a2b3c4)
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test class:
```bash
pytest src/tests/test_epic_api.py::TestNaturalEndpoints -v
```

Run with coverage:
```bash
pytest --cov=earth_polychromatic_api
```

## AWS Lambda Handler

The `lambda_handler.py` provides a serverless AWS Lambda function that uses the CLI package directly for cloud-based image processing. This enables:

- **Serverless Image Downloads**: Trigger NASA EPIC downloads via Lambda events
- **Flexible Date Parameters**: Multiple ways to specify date ranges with clear priority
- **Production Logging**: Proper logging for AWS CloudWatch integration
- **Error Handling**: Comprehensive error handling with structured responses

### Parameter Priority System

The Lambda handler uses a 4-tier priority system for date parameters to eliminate confusion:

1. **Explicit Dates** (highest priority)
   ```json
   {
     "start_date": "2024-01-01",
     "end_date": "2024-01-05"
   }
   ```

2. **Relative Dates** (when no explicit dates provided)
   ```json
   {
     "days_back": 3,
     "date_range_days": 2
   }
   ```

3. **Environment Variables** (fallback)
   - `START_DATE` and `END_DATE` environment variables

4. **Default** (last resort)
   - Yesterday with 1-day range

### Example Usage

```json
// Explicit date range (recommended for specific periods)
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-05",
  "bucket": "my-epic-bucket",
  "collection": "natural"
}

// Relative dates (good for recent data)
{
  "days_back": 7,
  "date_range_days": 3,
  "bucket": "my-epic-bucket"
}

// Mixed parameters (explicit dates take priority)
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-05",
  "days_back": 10,  // Ignored - explicit dates win
  "bucket": "my-epic-bucket"
}
```

### Response Format

```json
{
  "statusCode": 200,
  "success": true,
  "message": "NASA EPIC images downloaded successfully",
  "details": {
    "execution_time_seconds": 45.67,
    "images_downloaded": 12,
    "command_equivalent": "epic-images --date 2024-01-01 ...",
    "start_time": "2024-01-01T10:00:00Z",
    "end_time": "2024-01-01T10:00:45Z"
  },
  "stdout": "Downloaded 12 images...",
  "stderr": null
}
```

## API Endpoints Covered

The test suite covers all NASA EPIC API endpoints:

### Natural Color Imagery
- `GET /api/natural` - Most recent natural color images
- `GET /api/natural/date/{date}` - Natural images for specific date
- `GET /api/natural/all` - All available dates for natural images

### Enhanced Color Imagery
- `GET /api/enhanced` - Most recent enhanced color images
- `GET /api/enhanced/date/{date}` - Enhanced images for specific date
- `GET /api/enhanced/all` - All available dates for enhanced images

### Aerosol Index Imagery
- `GET /api/aerosol` - Most recent aerosol index images
- `GET /api/aerosol/date/{date}` - Aerosol images for specific date
- `GET /api/aerosol/all` - All available dates for aerosol images

### Cloud Fraction Imagery
- `GET /api/cloud` - Most recent cloud fraction images
- `GET /api/cloud/date/{date}` - Cloud images for specific date
- `GET /api/cloud/all` - All available dates for cloud images

### Image URL Builder
- `build_image_url()` - Constructs archive download URLs for images

## Test Features

- **Comprehensive Coverage**: Tests all API endpoints with proper arrange/act/assert structure
- **Mocked Responses**: Uses pytest monkeypatch with pre-built test data
- **Error Handling**: Tests HTTP error responses and edge cases
- **URL Construction**: Validates image archive URL building for all formats (PNG, JPG, thumbs)
- **Fixtures**: Organized test data fixtures for easy maintenance
- **Documentation**: Each test includes detailed docstrings explaining what it tests

## Test Data

All test responses are stored as JSON files in `src/tests/test_datasets/` and represent realistic API responses with proper metadata structure including:

- Image identifiers and timestamps
- Satellite position coordinates (DSCOVR J2000)
- Earth centroid coordinates
- Moon and sun positions
- Attitude quaternions
- Image captions and version info