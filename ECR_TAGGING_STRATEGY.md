# ECR Image Tagging Strategy

## Overview
The CI/CD pipeline now uses different tagging strategies based on the type of build:

## Tagging Rules

### 🏷️ Release Builds (when creating a GitHub release)
- **Primary Tag**: Uses the exact git release tag (e.g., `v1.0.0`, `1.2.3`)
- **Latest Tag**: Also tagged as `latest`
- **Trigger**: `github.event_name == "release"`
- **Example**: Release `v1.0.0` creates:
  - `999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:v1.0.0`
  - `999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:latest`

### 🔨 Development Builds (main branch pushes)
- **Primary Tag**: Uses git commit SHA (e.g., `abc123def456`)
- **Latest Tag**: Also tagged as `latest`
- **Trigger**: Push to `main` branch
- **Example**: Commit `abc123def456` creates:
  - `999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:abc123def456`
  - `999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:latest`

## ECR Repository Lifecycle Policy

### Rule 1: Keep Release Tags (Priority 1)
- **Keep**: All images tagged with semantic version patterns (`v*`, `1.*`, `2.*`, etc.)
- **Duration**: 10 years (effectively permanent)
- **Purpose**: Preserve all release versions for rollbacks and auditing

### Rule 2: Keep Latest Tag (Priority 2)
- **Keep**: Images tagged as `latest`
- **Duration**: 10 years (effectively permanent)
- **Purpose**: Always have the most recent build available

### Rule 3: Cleanup Development Builds (Priority 3)
- **Keep**: Last 10 images (typically commit SHA tags)
- **Purpose**: Prevent repository bloat from development builds

## Usage Examples

### For Production Deployments
Use release tags for stable, versioned deployments:
```bash
# Deploy specific version
aws lambda update-function-code \
  --function-name nasa-epic-downloader \
  --image-uri 999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:v1.0.0
```

### For Development/Testing
Use latest tag for the most recent build:
```bash
# Deploy latest version
aws lambda update-function-code \
  --function-name nasa-epic-downloader \
  --image-uri 999855041308.dkr.ecr.us-west-2.amazonaws.com/nasa-epic-downloader:latest
```

## Creating a Release

1. **Create a GitHub Release**:
   - Go to GitHub repository → Releases → "Create a new release"
   - Choose or create a tag (e.g., `v1.0.0`, `1.2.3`)
   - Write release notes
   - Publish the release

2. **Automatic CI/CD**:
   - CI/CD detects the release event
   - Builds Docker image
   - Pushes to ECR with release tag and `:latest`
   - Outputs both URIs in the workflow logs

3. **Deploy to Lambda**:
   - Use the release-tagged URI for production
   - Use `:latest` for development/testing environments

## Benefits

- ✅ **Immutable Release Versions**: Each release has a permanent, unchanging image
- ✅ **Easy Rollbacks**: Can deploy any previous release version
- ✅ **Clear Versioning**: Release tags match git tags exactly
- ✅ **Development Flexibility**: Latest tag always points to most recent build
- ✅ **Storage Efficiency**: Old development builds are automatically cleaned up
- ✅ **Audit Trail**: Complete history of release deployments