# 🚀 Learning Copilot - Learn by Doing

A Karpathy-inspired learning platform that emphasizes **project-based learning** and **learning by building**. Create personalized curricula from any topic, syllabus, or GitHub repository, and learn through hands-on coding projects.

> *"What I cannot create, I do not understand"* - Richard Feynman

## ✨ Features

- **🎯 Multiple Input Methods**
  - Manual topic entry
  - Upload course syllabus (PDF, TXT, MD)
  - Import from GitHub repositories
  - Quick-start templates

- **🏗️ Project-Based Learning**
  - Every concept taught through building
  - Progressive difficulty projects
  - Real-world applications
  - Debugging challenges

- **🤖 AI-Powered Guidance**
  - GPT-5 powered learning assistant
  - Personalized curriculum generation
  - Code review and feedback
  - Adaptive learning paths

- **📊 Progress Tracking**
  - Module completion tracking
  - Project submissions
  - Learning analytics
  - Persistent chat history

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-5 API
- **Database**: SQLite
- **Languages**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key with GPT-5 access
- (Optional) GitHub personal access token for better rate limits

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/learning-copilot.git
cd learning-copilot
```

### 2. Install dependencies

#### Option A: Automated Setup Script (Fastest! 🚀)

```bash
# Run the setup script
./setup.sh

# This will:
# - Install uv if needed
# - Create virtual environment
# - Install all dependencies
# - Set up .env file
# - Initialize database
```

#### Option B: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or if using an existing virtual environment
uv pip install -r requirements.txt
```

#### Option C: Using pip (Traditional)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# REQUIRED: Get your API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...your-actual-api-key-here...

# Optional: For better GitHub rate limits
GITHUB_ACCESS_TOKEN=ghp-...your-github-token...

# Recommended model (cost-effective)
MODEL_NAME=gpt-5-mini
```

**Important**: Make sure to use your actual OpenAI API key, not the placeholder!

### 4. Run the application

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run from the learning-copilot directory
cd learning-copilot
streamlit run app.py

# Or use the venv's streamlit directly
.venv/bin/streamlit run learning-copilot/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Starting Your Learning Journey

1. **Enter your username** to create/load your profile
2. **Choose an input method**:
   - **Manual Topic**: Type what you want to learn
   - **Upload Syllabus**: Upload a PDF/TXT/MD file
   - **GitHub Repo**: Paste a repository URL
   - **Quick Templates**: Choose from pre-made paths

### Learning Interface

Once your curriculum is generated:

1. **📖 Curriculum Tab**: View all modules and projects
2. **💬 Learning Assistant**: Chat with AI for help
3. **📊 Progress Tab**: Track your completion
4. **🛠️ Current Project**: Work on coding projects

### Working on Projects

1. Click "Generate Project" for any module
2. Review the project requirements and starter code
3. Implement the solution
4. Submit for AI feedback
5. Iterate based on suggestions

## 🏗️ Project Structure

```
learning-copilot/
├── app.py                    # Main Streamlit application
├── backend/
│   ├── ai_engine.py         # GPT-5 integration
│   ├── curriculum.py        # Curriculum generation
│   └── database.py          # SQLite operations
├── prompts/
│   └── curriculum_gen.py    # Prompt templates
├── utils/
│   ├── github_fetcher.py   # GitHub integration
│   └── file_handlers.py    # File processing
├── .env.example            # Environment template
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `GITHUB_ACCESS_TOKEN` | GitHub token (optional) | None |
| `MODEL_NAME` | OpenAI model to use | gpt-5 |
| `TEMPERATURE` | AI creativity (0-1) | 0.7 |
| `MAX_TOKENS` | Max response length | 4000 |
| `DATABASE_URL` | SQLite database path | sqlite:///learning_copilot.db |

### GPT-5 Specific Features

The app leverages GPT-5's new capabilities:
- **Verbosity control**: Adjusts response length
- **Reasoning effort**: Controls thinking depth
- **JSON mode**: Structured curriculum generation

## 📚 Example: Learning LLMs (Karpathy Style)

1. **Input**: "https://github.com/karpathy/LLM101n"
2. **Generated Curriculum**:
   - Module 1: Bigram Language Model
   - Module 2: N-gram with Smoothing
   - Module 3: Neural Language Model
   - Module 4: Attention Mechanism
   - Module 5: Transformer Architecture
   - Module 6: Mini-GPT Implementation

Each module includes:
- Hands-on coding projects
- Progressive complexity
- Test cases
- Debugging exercises
- Real applications

## 🛠️ Development Setup

### Using uv for Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run code formatters
black .
ruff check --fix .

# Run type checking
mypy backend/

# Run tests (when added)
pytest
```

### Quick Install Script

```bash
# One-liner to set up everything with uv
curl -LsSf https://astral.sh/uv/install.sh | sh && uv venv && source .venv/bin/activate && uv pip install -e . && cp .env.example .env
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more language support beyond Python
- [ ] Implement collaborative learning features
- [ ] Add video/resource recommendations
- [ ] Create mobile-friendly interface
- [ ] Add export to Jupyter notebooks
- [ ] Implement peer code review

## 🐛 Troubleshooting

### Common Issues

**API Key Errors**
```bash
ValueError: OPENAI_API_KEY not found
```
Solution: Ensure your `.env` file contains valid API key

**Rate Limiting**
```
openai.RateLimitError
```
Solution: Add delays or upgrade your OpenAI plan

**Database Errors**
```bash
sqlite3.OperationalError
```
Solution: Delete `learning_copilot.db` and restart

## 📝 License

MIT License - feel free to use for educational purposes!

## 🙏 Acknowledgments

- Inspired by [Andrej Karpathy's](https://karpathy.ai/) teaching philosophy
- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI GPT-5](https://openai.com/)

## 🚦 Roadmap

- **v1.0** ✅ Basic curriculum generation and chat
- **v1.1** 🔄 Code execution environment
- **v1.2** 📱 Mobile app
- **v2.0** 👥 Collaborative learning
- **v3.0** 🎥 Video generation for concepts

---

Built with ❤️ for learners who build to understand