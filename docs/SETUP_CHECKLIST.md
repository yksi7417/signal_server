# Setup Checklist - Running UI Tests

Quick checklist to get the UI test suite running on your machine.

## ✅ One-Time Setup

### 1. Install Playwright Dependencies
```bash
pip install playwright pytest-playwright
python -m playwright install chromium
```

**Verify Installation:**
```bash
python -m playwright --version
# Should output: Version 1.49.1
```

### 2. Verify pytest Configuration
```bash
pytest --markers
# Should show: ui, integration, slow markers
```

---

## ✅ Before Each Test Run

### 1. Start the Server
```bash
# In Terminal 1
cd c:\dvlp\signal_server
python app.py

# Wait for: "Running on http://localhost:8080"
```

### 2. Verify Server is Running
```bash
# In Terminal 2
curl http://localhost:8080
# Should return HTML content (not connection error)
```

---

## ✅ Running Tests

### Quick Test (3 minutes)
```bash
# Run just CHOW tests
pytest tests/ui/test_claims_ui.py::TestCHOWClaims -v
```

### Full Test Suite (10-15 minutes)
```bash
# Run all UI tests
pytest tests/ui/ -v -m ui
```

### Debug Mode (Visible Browser)
```bash
# See what's happening
pytest tests/ui/ -v --headed

# Slow motion for detailed observation
pytest tests/ui/ -v --headed --slowmo=1000
```

---

## ✅ Expected Results

### Success Output
```
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_buttons_are_visible_and_enabled PASSED
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds PASSED
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_no_button_responds PASSED
tests/ui/test_claims_ui.py::TestPUNGClaims::test_pung_buttons_respond PASSED
tests/ui/test_claims_ui.py::TestCountdownTimer::test_countdown_displays_30_seconds PASSED
tests/ui/test_claims_ui.py::TestCountdownTimer::test_countdown_decrements_in_realtime PASSED
tests/ui/test_claims_ui.py::TestBugReporting::test_bug_report_button_visible PASSED
tests/ui/test_claims_ui.py::TestBugReporting::test_bug_report_modal_opens PASSED
tests/ui/test_claims_ui.py::TestBugReporting::test_bug_report_submission PASSED
tests/ui/test_claims_ui.py::TestClaimPositionRules::test_chow_only_from_left_neighbor PASSED

======================== 10 passed in 123.45s ========================
```

### Expected Skips (Normal)
```
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds SKIPPED
Reason: CHOW opportunity did not appear after 30 attempts
```

**This is OK!** The game RNG didn't create the needed situation. Just re-run.

---

## ✅ Troubleshooting

### Problem: "Browser executable not found"
```bash
# Solution
python -m playwright install --force chromium
```

### Problem: "Connection refused to localhost:8080"
```bash
# Solution - Server not running
# Start server in another terminal:
python app.py
```

### Problem: "Tests hanging forever"
```bash
# Solution - Add timeout
pytest tests/ui/ -v --timeout=120
```

### Problem: "Import error: playwright"
```bash
# Solution - Reinstall
pip uninstall playwright pytest-playwright
pip install playwright pytest-playwright
python -m playwright install chromium
```

---

## ✅ Files You Created

Here's what was added to your project:

```
signal_server/
├── tests/
│   └── ui/
│       ├── __init__.py           # Package marker
│       ├── test_claims_ui.py     # UI tests (10 tests)
│       └── README.md             # Test documentation
├── docs/
│   ├── learnings.md              # Development patterns
│   ├── UI_TESTS.md               # UI testing guide
│   ├── SUMMARY.md                # Session summary
│   └── SETUP_CHECKLIST.md        # This file
├── pytest.ini                    # Test configuration
└── requirements.txt              # Updated with Playwright
```

---

## ✅ Quick Commands Reference

```bash
# Install everything
pip install -r requirements.txt
python -m playwright install chromium

# Start server
python app.py

# Run all tests
pytest tests/ -v

# Run only UI tests
pytest tests/ui/ -v -m ui

# Run only unit tests (fast)
pytest -m "not integration and not ui" -v

# Debug specific test
pytest tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds -v --headed
```

---

## ✅ Next Steps After Setup

1. **Run the full test suite once**
   ```bash
   pytest tests/ -v
   ```

2. **Read the documentation**
   - [learnings.md](learnings.md) - Development patterns
   - [UI_TESTS.md](UI_TESTS.md) - UI testing details

3. **Try manual testing**
   - Follow [TESTING_GUIDE.md](../TESTING_GUIDE.md)
   - Verify countdown timer works
   - Test CHOW/PUNG claims manually

4. **Optional: Set up GitHub token**
   ```bash
   # PowerShell
   $env:GITHUB_TOKEN="ghp_your_token_here"
   python app.py
   ```

---

## ✅ Success Criteria

You're ready to develop when:
- [ ] Server starts without errors
- [ ] Can access http://localhost:8080/game
- [ ] pytest runs without import errors
- [ ] At least 1 UI test passes
- [ ] Can see browser window with `--headed` flag

---

## 🎯 You're All Set!

The test suite is now ready to:
1. **Verify bug fixes** - Ensure CHOW/PUNG work correctly
2. **Prevent regressions** - Catch bugs before they reach production
3. **Document behavior** - Tests show how features should work
4. **Guide development** - Use tests to understand the codebase

**Happy Testing! 🚀**

---

_Need help? Check [UI_TESTS.md](UI_TESTS.md) for detailed troubleshooting._
