# Using Python 3.13 (Chocolatey Installation)

You already have Python 3.13 installed via Chocolatey! Here's how to use it.

## Quick Setup

```powershell
# 1. Navigate to your project
cd C:\dvlp\signal_server

# 2. Create virtual environment with Python 3.13
C:\ProgramData\chocolatey\bin\python313.exe -m venv venv313

# 3. Activate the virtual environment
.\venv313\Scripts\Activate.ps1

# If you get an execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate again:
.\venv313\Scripts\Activate.ps1

# 4. Verify you're using Python 3.13
python --version
# Should show: Python 3.13.x

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install all requirements
pip install -r requirements.txt

# 7. Verify installations
python -c "import aiohttp; print('✓ aiohttp OK')"
python -c "import pyarrow; print('✓ pyarrow OK')"
python -c "from github import Github; print('✓ PyGithub OK')"
python -c "import mahjong_engine; print('✓ mahjong_engine OK')"

# 8. Run tests
python -m pytest -m "not integration" -v tests/engine/
```

## Your Prompt Should Look Like This

```powershell
(venv313) PS C:\dvlp\signal_server>
```

The `(venv313)` prefix means you're using the virtual environment with Python 3.13.

## Daily Usage

### Starting a new PowerShell session:
```powershell
# Navigate to project
cd C:\dvlp\signal_server

# Activate virtual environment
.\venv313\Scripts\Activate.ps1

# Now you're ready to work!
python --version  # Shows 3.13.x
```

### When you're done:
```powershell
# Deactivate virtual environment
deactivate
```

## Running Commands in the Virtual Environment

Once activated (you see `(venv313)` in your prompt):

```powershell
# Run tests
python -m pytest -v

# Run the autonomous loop
python autonomous_loop.py --dry-run

# Install new packages
pip install package-name

# Run the server
python app.py
```

## Alternative: Add Alias to PowerShell Profile

To make activation easier, add an alias:

```powershell
# Open your PowerShell profile
notepad $PROFILE

# Add this line:
function Activate-Signal { Set-Location C:\dvlp\signal_server; .\venv313\Scripts\Activate.ps1 }
Set-Alias signal Activate-Signal

# Save and close, then reload:
. $PROFILE

# Now you can just type:
signal
# And it will navigate to the project and activate the venv!
```

## Checking Your Python Installations

```powershell
# Chocolatey Python 3.13
C:\ProgramData\chocolatey\bin\python313.exe --version

# Anaconda Python 3.8 (if still in PATH)
C:\ProgramData\Anaconda3\python.exe --version

# Whatever 'python' points to
python --version

# List all Python versions found
where.exe python*
```

## Python 3.13 Benefits

- ✅ **Fastest Python ever** (~40% faster than 3.8!)
- ✅ **Free-threaded mode** (experimental, no GIL)
- ✅ **Better JIT** (Just-In-Time compilation)
- ✅ **Latest packages** with newest features
- ✅ **Improved error messages**
- ✅ **Better type system**

## Troubleshooting

### Virtual environment activation fails
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv313\Scripts\Activate.ps1
```

### "python" command not found after activation
```powershell
# Make sure you activated the venv
.\venv313\Scripts\Activate.ps1

# Check if Python is in the venv
Get-Command python
# Should show: ...\venv313\Scripts\python.exe
```

### Package installation fails
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### ImportError for mahjong_engine
```powershell
# Make sure you're in the project directory
cd C:\dvlp\signal_server

# The project directory should be in your Python path
python -c "import sys; print('\n'.join(sys.path))"
```

## Clean Installation (If Needed)

If you want to start fresh:

```powershell
# Remove old virtual environment
rm -r venv313

# Create new one
C:\ProgramData\chocolatey\bin\python313.exe -m venv venv313

# Activate
.\venv313\Scripts\Activate.ps1

# Install everything
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Quick Test After Setup

```powershell
# Should all pass
python -c "import sys; print(f'Python {sys.version}')"
python -c "import aiohttp; print('aiohttp OK')"
python -c "from github import Github; print('PyGithub OK')"
python -m pytest -m "not integration" -v tests/engine/ | Select-String "passed"
```

If you see "216 passed", you're all set! 🚀

## Next Steps

1. ✅ Create virtual environment
2. ✅ Activate it
3. ✅ Install requirements
4. ✅ Run tests
5. Set GITHUB_TOKEN: `$env:GITHUB_TOKEN = "your_token"`
6. Run autonomous loop: `python autonomous_loop.py --dry-run`
