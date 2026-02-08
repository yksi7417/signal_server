# UI Tests

Browser-based automated tests using Playwright to verify user interface functionality.

## Setup

1. **Install Playwright**:
```bash
pip install playwright pytest-playwright
python -m playwright install chromium
```

2. **Start the server**:
```bash
# In one terminal
python app.py
```

3. **Run UI tests**:
```bash
# In another terminal
pytest tests/ui/ -v -m ui
```

## Test Categories

### CHOW Claims (`TestCHOWClaims`)
Tests the bug fix for frozen CHOW claim buttons:
- `test_chow_buttons_are_visible_and_enabled` - Buttons should be enabled
- `test_chow_yes_button_responds` - Clicking Yes processes claim
- `test_chow_no_button_responds` - Clicking No declines claim

### PUNG Claims (`TestPUNGClaims`)
Tests the bug fix for PUNG claim backend crashes:
- `test_pung_buttons_respond` - PUNG claim completes without error

### Countdown Timer (`TestCountdownTimer`)
Tests the 30-second countdown feature:
- `test_countdown_displays_30_seconds` - Timer starts at 30s
- `test_countdown_decrements_in_realtime` - Timer updates every second

### Bug Reporting (`TestBugReporting`)
Tests the bug report functionality:
- `test_bug_report_button_visible` - Button is visible on page
- `test_bug_report_modal_opens` - Modal opens when clicked
- `test_bug_report_submission` - Reports can be submitted

### Position Rules (`TestClaimPositionRules`)
Tests CHOW position enforcement:
- `test_chow_only_from_left_neighbor` - CHOW only from Player 3

## Running Specific Tests

```bash
# Run only CHOW tests
pytest tests/ui/test_claims_ui.py::TestCHOWClaims -v

# Run specific test
pytest tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds -v

# Run with visible browser (non-headless)
pytest tests/ui/ -v --headed

# Run in slow motion (for debugging)
pytest tests/ui/ -v --slowmo=1000
```

## Troubleshooting

### Server Not Running
If tests fail with connection errors, ensure server is running on port 8080:
```bash
python app.py
```

### Browser Not Installing
If Playwright browsers don't install:
```bash
python -m playwright install --force chromium
```

### Tests Timing Out
Some tests require specific game states (e.g., CHOW opportunity). If tests skip with timeout, this is normal - the RNG didn't produce the needed game state. Re-run the tests.

### Headless Mode Issues
Some tests may behave differently in headless mode. Use `--headed` flag to see browser:
```bash
pytest tests/ui/ -v --headed
```

## Test Output

### Success
```
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds PASSED
tests/ui/test_claims_ui.py::TestCountdownTimer::test_countdown_displays_30_seconds PASSED
```

### Skip (Expected)
```
tests/ui/test_claims_ui.py::TestCHOWClaims::test_chow_yes_button_responds SKIPPED
Reason: CHOW opportunity did not appear after 30 attempts
```

This is normal - rerun the test to try again.

## Adding New UI Tests

1. **Create test class** in `test_claims_ui.py`:
```python
class TestMyFeature:
    @pytest.mark.asyncio
    async def test_my_feature(self, page):
        # Navigate to page
        await page.goto('http://localhost:8080/game')

        # Interact with UI
        await page.click('#myButton')

        # Assert expected result
        text = await page.inner_text('#myElement')
        assert 'expected' in text
```

2. **Use page fixture** provided by `conftest.py`
3. **Mark with `@pytest.mark.asyncio`** for async tests
4. **Add to test matrix** in learnings.md

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Install Playwright
  run: |
    pip install playwright pytest-playwright
    python -m playwright install --with-deps chromium

- name: Start Server
  run: python app.py &

- name: Run UI Tests
  run: pytest tests/ui/ -v --headed
```

## Performance

- **Unit tests**: <1s for 215 tests
- **Integration tests**: ~5-10s
- **UI tests**: ~30-60s per test (depends on game RNG)

**Recommendation**: Run UI tests less frequently (pre-commit hook or CI/CD only)

## Known Issues

1. **Flaky tests**: Tests requiring specific game states may skip randomly
   - **Solution**: Retry logic or increased attempt counts

2. **Slow execution**: Browser automation is slower than unit tests
   - **Solution**: Run in parallel with `pytest-xdist`

3. **Windows compatibility**: Some Playwright features may differ on Windows
   - **Solution**: Test on target platform
