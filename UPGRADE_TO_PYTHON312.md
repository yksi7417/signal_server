# Upgrade to Python 3.12 Guide

## Step 1: Install Python 3.12

### Option A: Using winget (Recommended)
```powershell
winget install Python.Python.3.12
```

### Option B: Manual Download
1. Go to https://www.python.org/downloads/
2. Download Python 3.12.x (latest)
3. Run installer
4. ✅ Check "Add Python 3.12 to PATH"
5. ✅ Check "Install for all users" (optional)

### Verify Installation
```powershell
# Close and reopen PowerShell, then:
python --version
# Should show: Python 3.12.x

# If it shows 3.8.3, you may need to specify:
python3.12 --version
```

## Step 2: Create Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated:

```powershell
# Navigate to project directory
cd C:\dvlp\signal_server

# Create virtual environment with Python 3.12
python -m venv venv312

# Activate it
.\venv312\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv312\Scripts\Activate.ps1

# Verify you're using Python 3.12
python --version
# Should show: Python 3.12.x
```

Your prompt should now show `(venv312)` prefix.

## Step 3: Update requirements.txt for Python 3.12

I'll create an updated requirements.txt with modern versions:

```txt
# Core web server dependencies
aiohttp>=3.10.0
aiohttp-cors>=0.7.0
websockets>=13.0

# Data processing
pyarrow>=17.0.0
numpy>=2.0.0

# GitHub integration
PyGithub>=2.8.0
requests>=2.32.0

# Testing
pytest>=8.3.0
pytest-timeout>=2.3.0
psutil>=6.0.0

# Direct dependencies
aiohappyeyeballs>=2.6.0
aiosignal>=1.3.0
attrs>=25.0.0
certifi>=2025.4.0
charset-normalizer>=3.4.0
colorama>=0.4.6
frozenlist>=1.6.0
idna>=3.10
multidict>=6.4.0
propcache>=0.3.0
typing_extensions>=4.13.0
urllib3>=2.4.0
yarl>=1.20.0
```

## Step 4: Install Dependencies

```powershell
# Make sure venv is activated (you should see (venv312) in prompt)

# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

## Step 5: Verify Everything Works

### Test Python Version
```powershell
python --version  # Should be 3.12.x
```

### Test Imports
```powershell
python -c "import aiohttp; print('aiohttp OK')"
python -c "import pyarrow; print('pyarrow OK')"
python -c "from github import Github; print('PyGithub OK')"
python -c "import mahjong_engine; print('mahjong_engine OK')"
```

### Run Tests
```powershell
# Unit tests
python -m pytest -m "not integration" -v tests/engine/

# Integration tests
python -m pytest tests/integration/ -v
```

## Step 6: Update Code for Python 3.12 (Optional)

Python 3.12 allows modern type hints:

### Old (Python 3.8):
```python
from typing import List, Dict, Optional

def process_tiles(tiles: List[str]) -> Dict[str, int]:
    pass
```

### New (Python 3.12):
```python
def process_tiles(tiles: list[str]) -> dict[str, int]:
    pass
```

You can gradually update these, but it's not required - the old syntax still works!

## Step 7: Deactivate Old Environment (Optional)

If you want to completely switch:

```powershell
# Deactivate current venv
deactivate

# Remove old Anaconda Python from PATH (optional)
# Edit System Environment Variables
# Remove: C:\ProgramData\Anaconda3
# Remove: C:\ProgramData\Anaconda3\Scripts

# Or just always use the venv
```

## Common Issues & Solutions

### "python" still shows 3.8.3
```powershell
# Use full path or py launcher
py -3.12 -m venv venv312

# Or update PATH to prioritize Python 3.12
```

### ImportError after upgrade
```powershell
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Virtual environment activation fails
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv312\Scripts\Activate.ps1
```

### Tests fail after upgrade
```powershell
# Clear pytest cache
rm -r .pytest_cache
rm -r **/__pycache__

# Run tests again
python -m pytest -v
```

## Benefits of Python 3.12

1. **Performance**: ~25% faster than Python 3.8
2. **Better error messages**: More helpful tracebacks
3. **Modern type hints**: Use `list[str]` instead of `List[str]`
4. **Latest packages**: Access to newest versions
5. **Better async**: Improved asyncio performance
6. **Pattern matching**: `match/case` statements (if you want)

## Quick Commands Reference

```powershell
# Activate venv
.\venv312\Scripts\Activate.ps1

# Deactivate venv
deactivate

# Check Python version
python --version

# Install package
pip install package_name

# Run tests
python -m pytest -v

# Run autonomous loop
python autonomous_loop.py --dry-run
```

## Next Steps After Upgrade

1. ✅ Activate virtual environment
2. ✅ Install dependencies
3. ✅ Run tests to verify
4. ✅ Set GITHUB_TOKEN
5. ✅ Try autonomous loop

```powershell
# Quick verification
.\venv312\Scripts\Activate.ps1
python --version
pip install -r requirements.txt
python -m pytest -m "not integration" -v tests/engine/
```

If all tests pass, you're ready to go! 🚀
