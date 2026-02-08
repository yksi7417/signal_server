# PowerShell Setup Guide for Windows Development

This guide helps you set up the autonomous development loop on Windows using PowerShell.

## Prerequisites

### 1. Install Python 3.8+
Already installed ✓ (Python 3.8.3)

### 2. Install Git
```powershell
# Check if git is installed
git --version

# If not installed, download from: https://git-scm.com/download/win
# Or use winget:
winget install --id Git.Git
```

### 3. Install Required Python Packages
```powershell
# Install dependencies
pip install PyGithub

# Or install from requirements.txt
pip install -r requirements.txt
```

## Environment Setup

### 1. Set GITHUB_TOKEN Environment Variable

**Option A: Temporary (Current PowerShell Session Only)**
```powershell
$env:GITHUB_TOKEN = "your_github_personal_access_token_here"
```

**Option B: Permanent (For Your User Account)**
```powershell
# Set permanently
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_token_here", "User")

# Restart PowerShell, then verify
echo $env:GITHUB_TOKEN
```

**Create GitHub Personal Access Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: "Signal Server Development"
4. Scopes: Check `repo` (all sub-scopes)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)

### 2. Verify Environment
```powershell
# Check Python
python --version

# Check pip
pip --version

# Check git
git --version

# Check GITHUB_TOKEN (should show your token)
echo $env:GITHUB_TOKEN

# Test PyGithub
python -c "from github import Github; print('PyGithub OK')"
```

## Running the Autonomous Loop

### Test Mode (Dry Run)
```powershell
# Shows what would be done without making changes
python autonomous_loop.py --dry-run
```

### Live Mode
```powershell
# Actually fixes bugs (use with caution!)
python autonomous_loop.py --max-bugs 5
```

### With Custom Repository
```powershell
python autonomous_loop.py --repo "username/repository" --dry-run
```

## Testing

### Run Unit Tests
```powershell
# All unit tests (not integration)
python -m pytest -m "not integration" -v tests/engine/

# Specific test file
python -m pytest tests/engine/test_action_log.py -v

# With coverage
python -m pytest --cov=mahjong_engine tests/engine/
```

### Run Integration Tests
```powershell
# All integration tests (requires server to be running or auto-start)
python -m pytest tests/integration/ -v

# Skip slow tests
python -m pytest -m "not slow" tests/integration/ -v
```

## Common Commands

### Git Operations
```powershell
# Check status
git status

# Stage all changes
git add -A

# Commit with message
git commit -m "Your message here"

# Push to remote
git push

# View recent commits
git log --oneline -10
```

### File Operations
```powershell
# List files
ls

# Find files
ls -Recurse -Filter "*.py"

# Search in files (equivalent to grep)
Select-String -Path "*.py" -Pattern "pattern"

# View file content
Get-Content file.txt

# View last N lines (equivalent to tail)
Get-Content file.txt -Tail 20
```

### Process Management
```powershell
# Find processes using port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# Kill process by PID
Stop-Process -Id <PID> -Force

# Kill process by name
Stop-Process -Name python -Force
```

## Decoding Bug Report Parquet Files

When a bug is reported with a gist attachment:

```powershell
# Download the .b64 file from the gist, then:

# Decode base64 to parquet
[System.Convert]::FromBase64String((Get-Content actions.parquet.b64)) | Set-Content actions.parquet -Encoding Byte

# View the decoded actions
python -m mahjong_engine.action_log actions.parquet

# Or view as JSON
python -m mahjong_engine.action_log actions.parquet --json

# View specific player's actions
python -m mahjong_engine.action_log actions.parquet --player 0
```

## Troubleshooting

### "PyGithub not found"
```powershell
pip install PyGithub
```

### "GITHUB_TOKEN not set"
```powershell
# Set it temporarily
$env:GITHUB_TOKEN = "your_token_here"

# Or set permanently (see Environment Setup above)
```

### "Permission denied"
```powershell
# Run PowerShell as Administrator, or
# Use --user flag for pip:
pip install --user PyGithub
```

### "Module not found"
```powershell
# Make sure you're in the project directory
cd c:\dvlp\signal_server

# Verify Python can find the modules
python -c "import mahjong_engine; print('OK')"
```

### Integration Tests Fail
```powershell
# Check if server is running on port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# If yes, kill it
Stop-Process -Id <PID> -Force

# Then run tests again
python -m pytest tests/integration/ -v
```

## PowerShell Aliases (Optional)

Add to your PowerShell profile for convenience:

```powershell
# Open profile
notepad $PROFILE

# Add these lines:
function pytest { python -m pytest $args }
function pytest-unit { python -m pytest -m "not integration" -v tests/engine/ $args }
function pytest-integration { python -m pytest tests/integration/ -v $args }
function auto-loop { python autonomous_loop.py $args }

# Reload profile
. $PROFILE
```

Then you can use:
```powershell
pytest-unit
pytest-integration
auto-loop --dry-run
```

## Next Steps

1. ✅ Verify environment setup
2. ✅ Set GITHUB_TOKEN
3. ✅ Run dry-run mode: `python autonomous_loop.py --dry-run`
4. ✅ Check open bugs
5. 🔄 Run autonomous loop to fix bugs

## Cross-Platform Notes

This project works on both Windows (PowerShell) and Linux:
- **Windows Dev**: Use PowerShell, pip, python
- **Linux Deployment**: Docker containers use bash, same Python code
- **Scripts**: Python scripts work on both platforms
- **Tests**: pytest works identically on both platforms

All Python code and tests are platform-independent!
