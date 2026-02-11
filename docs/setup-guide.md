# ⚙️ Setup & Installation Guide

## Prerequisites

- **Python**: 3.10 or higher ([Download](https://python.org/downloads))
- **pip**: Python package manager (included with Python)
- **Git**: Version control ([Download](https://git-scm.com/downloads))
- **ScaleDown API Key**: From the Intel Unnati / ScaleDown challenge

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Niranjan070/Data-Analysis-Agent.git
cd Data-Analysis-Agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | Purpose |
|---|---|
| `fastapi` | Web framework for the backend API |
| `uvicorn` | ASGI server to run FastAPI |
| `pandas` | Data manipulation and analysis |
| `matplotlib` | Chart generation |
| `seaborn` | Statistical visualizations |
| `numpy` | Numerical computing |
| `scipy` | Scientific computing |
| `python-dotenv` | Environment variable management |
| `requests` | HTTP client for ScaleDown API |
| `python-multipart` | File upload handling |
| `jinja2` | Template engine |
| `aiofiles` | Async file operations |

### 4. Configure Environment Variables

```bash
# Copy the example config
cp .env.example .env

# Edit .env and add your ScaleDown API key
# Windows:
notepad .env

# macOS / Linux:
nano .env
```

Set the following values in `.env`:
```env
SCALEDOWN_API_KEY=your_actual_api_key_here
SCALEDOWN_API_URL=https://api.scaledown.xyz/compress/raw/
```

### 5. Run the Application

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 6. Open in Browser

Navigate to: **http://localhost:8000**

---

## Troubleshooting

### Port Already in Use
If port 8000 is busy, modify `app.py` last line:
```python
uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
```

### Import Errors
Ensure the virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# Check python location
where python
# Should show: ...\venv\Scripts\python.exe
```

### ScaleDown API Issues
If the ScaleDown API returns errors, the app automatically falls back to local heuristic compression. No action needed — the app will continue working.

### Chart Generation Issues
If charts don't appear, ensure matplotlib's Agg backend is being used (already configured in `code_executor.py`):
```python
import matplotlib
matplotlib.use('Agg')
```

---

## Development Mode

The app runs with `--reload` by default, which means:
- Code changes are automatically detected
- The server restarts when you save a file
- No need to manually restart during development
