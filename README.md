# NASA EPIC API Client

A Python client for NASA's Earth Polychromatic Imaging Camera (EPIC) API.

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
src/
├── earth_polychromatic_api/    # Main API client package
│   ├── __init__.py
│   └── client.py              # EpicApiClient class
└── tests/                     # Test suite
    ├── __init__.py
    ├── test_epic_api.py       # Comprehensive unit tests
    └── test_datasets/         # Mock API response data
        ├── natural_recent_response.json
        ├── enhanced_date_response.json
        ├── natural_all_dates_response.json
        ├── aerosol_recent_response.json
        ├── cloud_recent_response.json
        ├── enhanced_all_dates_response.json
        ├── aerosol_all_dates_response.json
        └── cloud_all_dates_response.json
```

## Installation

Install the test dependencies:
```bash
pip install -r requirements-test.txt
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

## Endpoint Verification

The `verify_endpoints.py` script provides a comprehensive test of all API endpoints against the live NASA EPIC service. This is useful for:

- Verifying API connectivity and functionality
- Testing all endpoint types (natural, enhanced, aerosol, cloud)
- Validating Pydantic model parsing with real data
- Checking image URL construction
- Confirming service layer functionality

Run the verification script:
```bash
python verify_endpoints.py
```

The script will test:
- ✅ All 4 image collection types (natural, enhanced, aerosol, cloud)
- ✅ Recent images, date-specific images, and available dates endpoints
- ✅ Raw client methods and typed service methods
- ✅ Pydantic model validation and collection methods
- ✅ Image URL construction for different formats

Example output:
```
============================================================
 NASA EPIC API Endpoint Verification
============================================================
ℹ️  This script will test all service endpoints...
✅ Service initialized successfully
✅ Found 13 recent natural images
✅ Found 12 natural images for 2023-10-15
✅ Found 150+ available dates for natural images
...
Overall Results: 6/6 tests passed
✅ 🎉 All endpoints are working correctly!
```

## NASA EPIC to S3 Download Script

The `epic_s3_downloader.py` script provides a simple way to download NASA EPIC images for specified date ranges and upload them directly to AWS S3. This is useful for:

- Building archives of Earth imagery
- Creating datasets for analysis or machine learning
- Automated data pipeline integration
- Bulk downloading historical imagery

### Usage

```bash
# Download images locally only (no S3 upload)
python epic_s3_downloader.py --start-date 2023-10-01 --end-date 2023-10-31 --local-only

# Download natural color images to S3
python epic_s3_downloader.py --start-date 2023-10-01 --end-date 2023-10-31 --bucket my-epic-bucket

# Download enhanced images for a single day
python epic_s3_downloader.py --start-date 2023-10-15 --end-date 2023-10-15 --bucket my-bucket --collection enhanced

# Keep local copies after uploading to S3
python epic_s3_downloader.py --start-date 2023-10-15 --end-date 2023-10-15 --bucket my-bucket --keep-local

# Specify custom local directory
python epic_s3_downloader.py --start-date 2023-10-15 --end-date 2023-10-15 --local-only --local-dir ./my_epic_images
```

### Requirements

```bash
pip install requests           # Always required
pip install boto3             # Only needed for S3 uploads
```

### AWS Configuration

Configure AWS credentials using any standard method:
- `aws configure` (recommended)
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- IAM roles (when running on EC2)
- AWS profiles

### Directory Structure

Images are organized locally and in S3 with the following structure:
```
# Local structure (default: ./nasa_epic_images/)
./nasa_epic_images/
├── natural/2023/10/15/epic_1b_20231015123456.png
├── enhanced/2023/10/15/epic_1b_20231015123456.png
├── aerosol/2023/10/15/epic_1b_20231015123456.png
└── cloud/2023/10/15/epic_1b_20231015123456.png

# S3 structure (when uploading to S3)
s3://your-bucket/nasa-epic/
├── natural/2023/10/15/epic_1b_20231015123456.png
├── enhanced/2023/10/15/epic_1b_20231015123456.png
├── aerosol/2023/10/15/epic_1b_20231015123456.png
└── cloud/2023/10/15/epic_1b_20231015123456.png
```

### Options

- `--start-date` / `--end-date`: Date range in YYYY-MM-DD format
- `--local-only`: Download images locally only (no S3 upload)
- `--bucket`: S3 bucket name (required for S3 upload, ignored if `--local-only`)
- `--collection`: Image type (`natural`, `enhanced`, `aerosol`, `cloud`) - default: `natural`
- `--local-dir`: Local download directory - default: `./nasa_epic_images`
- `--keep-local`: Keep local files after S3 upload (ignored if `--local-only`)

### Error Handling

The script continues processing if individual images fail to download or upload, providing status for each operation. Failed downloads are logged but don't stop the overall process.

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