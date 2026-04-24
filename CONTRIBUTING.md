# Contributing to pydoge

Thank you for your interest in contributing to pydoge! We welcome contributions from the community.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jonheaven/pydoge.git
   cd pydoge
   ```

2. **Install with development dependencies:**
   ```bash
   uv sync
   # or pip install -e .[dev]
   ```

3. **Run tests:**
   ```bash
   uv run pytest
   ```

4. **Check code quality:**
   ```bash
   uv run ruff check .
   uv run mypy src
   ```

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for new functionality

4. **Run the full test suite:**
   ```bash
   uv run pytest --cov=pydoge --cov-report=html
   ```

5. **Check code quality:**
   ```bash
   uv run ruff check . --fix
   uv run mypy src
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **Push and create a PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Code Style
- Follow PEP 8 with Ruff formatting
- Use type hints everywhere
- Write comprehensive docstrings
- Keep functions small and focused

### Commit Messages
Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring

### Testing
- Write tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Mock external dependencies

### Documentation
- Update README.md for user-facing changes
- Add docstrings to all public functions
- Update type hints as needed

## Project Structure

```
pydoge/
├── src/pydoge/          # Main package
│   ├── __init__.py     # Package exports
│   ├── client.py       # RPC client
│   ├── wallet.py       # Wallet abstraction
│   ├── models.py       # Pydantic models
│   ├── exceptions.py   # Custom exceptions
│   └── cli.py          # Command-line interface
├── tests/              # Test suite
│   ├── conftest.py     # Test fixtures
│   ├── test_client.py  # Client tests
│   └── test_wallet.py  # Wallet tests
├── pyproject.toml      # Project configuration
└── README.md           # Documentation
```

## Testing Strategy

### Unit Tests
- Mock all RPC calls
- Test success and error cases
- Validate input parameters
- Check return types

### Integration Tests
- Test against regtest dogecoind
- Verify end-to-end functionality
- Check real RPC responses

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Update** documentation
6. **Submit** a pull request
7. **Address** review feedback

## Code Review Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Type hints are complete
- [ ] Documentation is updated
- [ ] No breaking changes without discussion
- [ ] Commit messages are clear

## Questions?

Feel free to open an issue or discussion for questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.