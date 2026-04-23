# Contributing to DML Stream

Thank you for your interest in contributing to DML Stream!

## Quick Links

- [Development Setup](docs/contributing.md#development-setup)
- [Code Style](docs/contributing.md#code-style)
- [Testing](docs/contributing.md#testing)
- [Submitting Changes](docs/contributing.md#submitting-changes)

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/dml-stream.git
cd dml-stream
```

### 2. Set Up Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes

- Write code following our style guidelines
- Add tests for new features
- Update documentation as needed

### 5. Run Tests

```bash
pytest --cov=dml_stream
black --check src/ tests/
ruff check src/ tests/
mypy src/
```

### 6. Submit Pull Request

Push your changes and open a PR on GitHub with a clear description of what you've done.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming community.

## Need Help?

- **Questions**: [GitHub Discussions](https://github.com/devmayank-official/dml-stream/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/devmayank-official/dml-stream/issues)

For detailed contribution guidelines, see [docs/contributing.md](docs/contributing.md).
