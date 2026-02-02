# Contributing to Meter Reader

Thank you for considering contributing to Meter Reader! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the issue list as you might find out that you don't need to create one. When creating a bug report, include:

- **Clear description** of what the bug is
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Python version** and **gateway model**
- **Relevant output** (error messages, debug logs)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When suggesting an enhancement:

- **Use a clear title**
- **Provide a step-by-step description**
- **Provide examples** to demonstrate the enhancement
- **Explain why** this enhancement would be useful

### Pull Requests

1. Fork the repository and create a branch from `main`
2. Make your changes
3. Run tests and linting checks
4. Write clear commit messages
5. Push to your fork and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/meter_reader.git
cd meter_reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/
```

## Code Style

This project uses:

- **black** for code formatting (100 character line length)
- **isort** for import sorting
- **mypy** for type checking

Format your code:

```bash
black src/ tests/
isort src/ tests/
```

Check types:

```bash
mypy src/
```

## Commit Messages

Write clear, concise commit messages:

```
Capitalize the first line, keep it under 50 characters
Blank line
More detailed explanation if needed, wrapped at 72 characters.
```

Example:

```
Fix socket timeout handling in gateway communication

Previously, socket.makefile() could block indefinitely if the
gateway sent incomplete data. Now using socket.recv() with
proper timeout support.
```

## Documentation

- Update README.md if adding/changing features
- Add docstrings to new functions and classes
- Include type hints in all code
- Update this CONTRIBUTING.md if needed

## License

By contributing, you agree that your contributions will be licensed under the BSD 2-Clause License.

## Questions?

Feel free to open an issue or discussion for questions about contributing.
