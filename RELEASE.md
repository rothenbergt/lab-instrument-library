# Release Process

This document explains how to create and publish new releases of the Lab Instrument Library.

## Prerequisites

Before creating your first release, you need to set up **PyPI Trusted Publishing** (recommended) or a PyPI API token.

### Option 1: Trusted Publishing (Recommended)

Trusted Publishing allows GitHub Actions to publish to PyPI without storing any secrets. It's more secure and easier to maintain.

1. Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/publishing/)
2. Add a new publisher with these details:
   - **PyPI Project Name**: `pylabinstruments`
   - **Owner**: `rothenbergt`
   - **Repository name**: `pylabinstruments`
   - **Workflow name**: `publish.yml`
   - **Environment name**: (leave blank)

### Option 2: API Token (Alternative)

If you prefer using an API token:

1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add it to GitHub Secrets as `PYPI_API_TOKEN`
3. Update `.github/workflows/publish.yml` to use the token instead of trusted publishing

## Release Workflow

### 1. Update Version and Changelog

Before creating a release:

**Update version in `pyproject.toml`:**
```toml
[project]
name = "pylabinstruments"
version = "0.2.0"  # Update this
```

**Update `CHANGELOG.md`:**
```markdown
## [0.2.0] - 2024-01-15

### Added
- New instrument support for XYZ
- Feature ABC

### Fixed
- Bug in multimeter connection handling
- Typo in documentation

### Changed
- Improved error messages for VISA connection failures
```

Commit these changes:
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
git push origin main
```

### 2. Create and Push a Tag

The publishing workflow is triggered by pushing a version tag:

```bash
# Create tag (use the same version as pyproject.toml)
git tag v0.2.0

# Push the tag to GitHub
git push origin v0.2.0
```

### 3. Automated Publishing

Once the tag is pushed:

1. GitHub Actions will automatically:
   - Build the package (sdist + wheel)
   - Run `twine check` to validate the build
   - Publish to PyPI
   - Create a GitHub Release with auto-generated notes

2. Monitor the workflow at:
   ```
   https://github.com/rothenbergt/pylabinstruments/actions
   ```

3. If successful, your package will be available at:
   ```
   https://pypi.org/project/pylabinstruments/
   ```

### 4. Verify the Release

After publishing:

```bash
# Install from PyPI in a fresh environment
pip install --upgrade pylabinstruments

# Verify it works
python -c "from pylabinstruments import Multimeter; print('Success!')"
```

## Release Checklist

Use this checklist for each release:

- [ ] All tests passing on main branch
- [ ] CHANGELOG.md updated with changes
- [ ] Version bumped in `pyproject.toml`
- [ ] Changes committed and pushed to main
- [ ] Git tag created with `v` prefix (e.g., `v0.2.0`)
- [ ] Tag pushed to GitHub
- [ ] GitHub Action completed successfully
- [ ] Package available on PyPI
- [ ] GitHub Release created automatically
- [ ] Installation tested from PyPI

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Breaking changes, incompatible API changes
- **MINOR** version (0.X.0): New features, backwards-compatible
- **PATCH** version (0.0.X): Bug fixes, backwards-compatible

Examples:
- `v0.1.0` → `v0.2.0`: Added new instrument support (new feature)
- `v0.2.0` → `v0.2.1`: Fixed bug in multimeter class (bug fix)
- `v0.9.0` → `v1.0.0`: Stable API, breaking changes from beta (major)

## Troubleshooting

### Build Fails

If the build fails:
```bash
# Test locally first
python -m pip install build
python -m build
python -m pip install twine
twine check dist/*
```

### Publishing Fails

Common issues:
- **403 Forbidden**: Check PyPI trusted publishing configuration
- **400 Bad Request**: Version already exists (bump version number)
- **File already exists**: Delete and recreate tag, bump version

### Manual Publishing (Emergency)

If automated publishing fails, you can publish manually:

```bash
# Build locally
python -m build

# Upload to PyPI
python -m pip install twine
twine upload dist/*
```

## First-Time Setup

For your very first release to PyPI:

1. **Create a PyPI account** at https://pypi.org/account/register/
2. **Set up trusted publishing** (see Prerequisites above)
3. **Test with TestPyPI first** (optional but recommended):
   ```bash
   python -m build
   twine upload --repository testpypi dist/*
   pip install --index-url https://test.pypi.org/simple/ pylabinstruments
   ```
4. **Create your first release** following the workflow above

## Questions?

If you encounter issues or have questions about the release process, please:
- Check the [GitHub Actions logs](https://github.com/rothenbergt/pylabinstruments/actions)
- Review [PyPI's publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- Open an issue on GitHub
