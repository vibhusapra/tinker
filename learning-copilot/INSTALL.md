# 📦 Installation Guide

## Quick Start (30 seconds)

```bash
# Clone and setup everything
git clone https://github.com/yourusername/learning-copilot.git
cd learning-copilot
./setup.sh
```

Then add your OpenAI API key to `.env` and run:
```bash
streamlit run app.py
```

## Detailed Installation Options

### 🚀 Method 1: Using uv (Fastest)

[uv](https://github.com/astral-sh/uv) is a blazing-fast Python package installer written in Rust.

#### Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Via pip:**
```bash
pip install uv
```

#### Install Learning Copilot with uv

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install the project
uv pip install -e .
```

### 📦 Method 2: Traditional pip

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 🐳 Method 3: Docker (Coming Soon)

```bash
# Build image
docker build -t learning-copilot .

# Run container
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env learning-copilot
```

## Environment Configuration

### Required API Keys

1. **OpenAI API Key** (Required)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`

2. **GitHub Token** (Optional, for better rate limits)
   - Get from: https://github.com/settings/tokens
   - Add to `.env`: `GITHUB_ACCESS_TOKEN=ghp_...`

### Configuration Options

Edit `.env` file:

```env
# Required
OPENAI_API_KEY=your-key-here

# Optional
GITHUB_ACCESS_TOKEN=your-token-here
MODEL_NAME=gpt-5              # or gpt-5-mini for faster/cheaper
TEMPERATURE=0.7                # 0.0-1.0, higher = more creative
MAX_TOKENS=4000               # Max response length
DATABASE_URL=sqlite:///learning_copilot.db
DEBUG_MODE=False
```

## Troubleshooting

### uv Installation Issues

**"uv: command not found" after installation:**
```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
# Add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

**Permission denied on setup.sh:**
```bash
chmod +x setup.sh
./setup.sh
```

### Python Version Issues

**Requires Python 3.8+:**
```bash
# Check version
python --version

# If needed, install Python 3.8+ via:
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Windows: Download from python.org
```

### API Key Issues

**"OPENAI_API_KEY not found":**
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key
3. Ensure no spaces around the `=` sign
4. Restart the application

### Database Issues

**"sqlite3.OperationalError":**
```bash
# Reset database
rm learning_copilot.db
python -c "from backend.database import Database; Database()"
```

## Performance Tips

### Using uv for Faster Installs

uv is 10-100x faster than pip:

```bash
# Benchmark comparison
time pip install -r requirements.txt  # ~30-60 seconds
time uv pip install -r requirements.txt  # ~1-3 seconds
```

### Caching for Faster Startup

```bash
# Pre-compile Python files
python -m compileall .

# Cache Streamlit
streamlit cache clear
```

## Development Setup

### Install with Dev Dependencies

```bash
# Using uv
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

### Run Code Quality Tools

```bash
# Format code
black .
ruff check --fix .

# Type checking
mypy backend/

# Run tests
pytest
```

## Platform-Specific Notes

### macOS

- Tested on macOS 12+ (Monterey and later)
- Apple Silicon (M1/M2) fully supported
- May need Xcode Command Line Tools: `xcode-select --install`

### Windows

- Use PowerShell or WSL2 for best experience
- Path separators in `.env` should use forward slashes
- Activate venv with: `.venv\Scripts\Activate.ps1`

### Linux

- Tested on Ubuntu 20.04+, Debian 11+, Fedora 35+
- May need python3-venv: `sudo apt install python3-venv`
- May need build tools: `sudo apt install build-essential`

## Getting Help

- **Issues**: https://github.com/yourusername/learning-copilot/issues
- **Discussions**: https://github.com/yourusername/learning-copilot/discussions
- **Quick fixes**: Try `./setup.sh` to reinstall everything