# Contributing to Lab Instrument Library

Thank you for considering contributing to the Lab Instrument Library! This document provides guidelines and instructions for contributing.

## Development Process

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Create a feature branch**: `git checkout -b feature/your-feature-name`
4. **Make your changes** and commit them with clear messages
5. **Push to your branch**: `git push origin feature/your-feature-name`
6. **Submit a Pull Request** to the main repository

## Adding Support for New Instruments

When adding support for a new instrument:

1. Create a new module in the `lab_instrument_library` directory named after the instrument type
2. Inherit from `LibraryTemplate` to ensure consistent API
3. Implement standard methods like `__init__`, `reset`, and `close`
4. Add comprehensive docstrings for all public methods
5. Update `__init__.py` to import and expose your new class

## Code Style

- Follow PEP 8 guidelines
- Include type annotations for all function parameters and return types
- Use docstrings in Google style format
- Keep line length to 88 characters maximum

## Testing

While comprehensive tests may be difficult without physical instruments:

- Consider using mock objects to simulate instrument responses
- Test basic connectivity and command formation logic
- Include validation for command string formatting

## Documentation

- Each module should have a docstring explaining its purpose and supported devices
- Each class should have a clear docstring explaining its functionality
- All public methods should have comprehensive docstrings with:
  - Description of functionality
  - Parameters (with types and descriptions)
  - Return values (with types and descriptions)
  - Examples where appropriate

## Questions?

If you have questions about contributing, feel free to open an issue on GitHub.
