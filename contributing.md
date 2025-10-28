# Contributing

We welcome contributions from the community! This document outlines how you can contribute to TokySnatcher.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rahaaatul/TokySnatcher.git
   cd TokySnatcher
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   # or with uv (recommended)
   uv pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   tokysnatcher --help
   ```

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:

- **TokySnatcher version**: `tokysnatcher --version`
- **Python version**: `python --version`
- **Operating system**: Windows/macOS/Linux + version
- **FFmpeg version**: `ffmpeg -version`
- **Steps to reproduce**: Detailed steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full traceback if available
- **Log output**: Any relevant log messages

### Feature Requests
For new features, please:

- **Describe the problem**: What limitation are you facing?
- **Describe the solution**: How would you like it to work?
- **Alternatives considered**: Have you considered other approaches?
- **Additional context**: Any other relevant information

## 💻 Contributing Code

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Run tests**: `python -m pytest` (if tests exist)
5. **Commit your changes**: `git commit -am 'Add some feature'`
6. **Push to the branch**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Imports**: Organize imports (standard library, third-party, local)
- **Docstrings**: Use Google-style or NumPy-style docstrings
- **Type hints**: Add type annotations where possible
- **Error handling**: Use appropriate exception handling

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=tokysnatcher

# Run specific test
pytest tests/test_specific.py
```

## 📝 Documentation

### Updating Documentation

Documentation is built with VitePress in the `docs` branch. To update:

1. **Switch to docs branch**: `git checkout docs`
2. **Make changes to markdown files**
3. **Preview locally**: `npm run docs:dev`
4. **Build and commit**: `npm run docs:build`

### README Updates

Update the main README.md file in the root directory when:
- Adding new features
- Changing installation procedures
- Modifying usage instructions
- Updating requirements

## 🔧 Development Tools

### Code Quality

```bash
# Format code with black
black tokysnatcher/

# Sort imports with isort
isort tokysnatcher/

# Lint with flake8
flake8 tokysnatcher/

# Type check with mypy
mypy tokysnatcher/
```

### Pre-commit Hooks

Consider using pre-commit hooks to automate code quality checks:

```bash
pip install pre-commit
pre-commit install
```

## 🎯 Project Structure

```
TokySnatcher/
├── tokysnatcher/          # Main package
│   ├── __main__.py       # CLI entry point
│   ├── chapters.py       # Chapter download logic
│   ├── download.py       # Download utilities
│   ├── search.py         # Search functionality
│   └── utils/            # Utility functions
├── docs/                 # Documentation (separate branch)
├── tests/                # Test suite
├── .github/              # GitHub workflows and templates
├── pyproject.toml        # Project configuration
└── README.md            # Main documentation
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] Changes are backwards compatible (where possible)

### PR Title Format
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### PR Description
Include:
- What changes were made
- Why they were made
- How to test the changes
- Any breaking changes

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 📞 Getting Help

If you need help:

1. **Check existing issues**: Search for similar problems
2. **Read the documentation**: Ensure you understand current behavior
3. **Ask in discussions**: Use GitHub Discussions for questions
4. **Create an issue**: If you found a bug or need clarification

## 🙏 Recognition

Contributors will be recognized:
- In the CHANGELOG.md for significant contributions
- As co-authors on commits
- In release notes where appropriate

Thank you for contributing to TokySnatcher! 🎵
