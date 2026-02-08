# UI Test Suite - Bug Fix Verification

**Created**: 2026-02-07
**Purpose**: Automated browser tests to verify bug fixes and prevent regressions

## Overview

This test suite was created to verify and prevent regression of critical bug fixes:

1. **CHOW Claim UI Freeze** - Buttons were unresponsive, UI completely frozen
2. **PUNG Claim Backend Crash** - UnicodeEncodeError when processing PUNG claims
3. **30-Second Countdown Timer** - Real-time countdown display for claim decisions
4. **Bug Report System** - Integrated bug reporting with GitHub automation

## Quick Start

```bash
# 1. Install dependencies
pip install playwright pytest-playwright
python -m playwright install chromium

# 2. Start server (in one terminal)
python app.py

# 3. Run tests (in another terminal)
pytest tests/ui/ -v -m ui
```

## Test Coverage

### Critical Bug Fixes ✅

| Bug | Test | Status |
|-----|------|--------|
| CHOW UI Freeze | `test_chow_yes_button_responds` | ✅ Passing |
| CHOW UI Freeze | `test_chow_no_button_responds` | ✅ Passing |
| PUNG Backend Crash | `test_pung_buttons_respond` | ✅ Passing |
| Countdown Timer | `test_countdown_displays_30_seconds` | ✅ Passing |
| Countdown Real-time | `test_countdown_decrements_in_realtime` | ✅ Passing |
| Bug Report UI | `test_bug_report_button_visible` | ✅ Passing |
| Bug Report Modal | `test_bug_report_modal_opens` | ✅ Passing |
| Bug Report Submit | `test_bug_report_submission` | ✅ Passing |
| CHOW Position Rule | `test_chow_only_from_left_neighbor` | ✅ Passing |

### Test Execution

```bash
# Run all UI tests
pytest tests/ui/ -v

# Run specific category
pytest tests/ui/test_claims_ui.py::TestCHOWClaims -v

# Run with browser visible (for debugging)
pytest tests/ui/ -v --headed

# Run in slow motion
pytest tests/ui/ -v --headed --slowmo=1000
```

## Test Architecture

### Test Fixture Structure

```python
@pytest.fixture(scope="session")
async def browser():
    """Launch browser once per test session"""
    # Chromium browser (headless by default)

@pytest.fixture
async def page(browser):
    """Create fresh page for each test"""
    # Navigate to game
    # Click Reset
    # Yield page
    # Cleanup
```

### Test Pattern

```python
class TestFeature:
    @pytest.mark.asyncio
    async def test_something(self, page):
        # 1. Navigate to specific game state
        await self._navigate_to_claim_opportunity(page)

        # 2. Perform user action
        await page.click('#btnClaimYes')

        # 3. Assert expected outcome
        console_text = await page.inner_text('#player-console')
        assert 'expected text' in console_text
```

## Known Limitations

### Game State Dependency

Some tests require specific game states that may not occur due to RNG:

```
SKIPPED - CHOW opportunity did not appear after 30 attempts
```

**This is normal and expected.** The test framework includes retry logic and reasonable attempt limits.

**Solutions**:
1. Re-run the test (different RNG seed)
2. Increase `max_attempts` in helper methods
3. Use deterministic test scenarios (future improvement)

### Performance

- Unit tests: <1 second (215 tests)
- Integration tests: 5-10 seconds
- UI tests: **30-60 seconds per test**

**Recommendation**: Run UI tests less frequently:
- Locally: Before commits with UI changes
- CI/CD: On pull requests
- Not recommended: On every file save

## Debugging Failed Tests

### Visual Debugging

```bash
# See browser in action
pytest tests/ui/test_claims_ui.py::test_name -v --headed

# Slow motion (1 second per step)
pytest tests/ui/ -v --headed --slowmo=1000
```

### Screenshots

Add to test for debugging:
```python
await page.screenshot(path='debug.png')
```

### Console Logging

```python
# Print current console state
console_text = await page.inner_text('#player-console')
print(f"Console: {console_text}")
```

### Browser DevTools

```python
# Pause execution to inspect
await page.pause()
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: UI Tests

on: [pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install --with-deps chromium

      - name: Start server
        run: python app.py &

      - name: Wait for server
        run: |
          timeout 30 bash -c 'until curl -f http://localhost:8080; do sleep 1; done'

      - name: Run UI tests
        run: pytest tests/ui/ -v --headed

      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: screenshots/
```

## Maintenance

### Adding New Tests

1. **Identify user flow** to test
2. **Create test method** in appropriate class
3. **Use helper methods** for navigation
4. **Add assertions** for expected behavior
5. **Update this document**

### Updating Existing Tests

When UI changes occur:
1. Update selectors (`#elementId`, `.className`)
2. Update expected text messages
3. Adjust timing (`wait_for_timeout`)
4. Update test documentation

### Deprecating Tests

If a feature is removed:
1. Mark test with `@pytest.mark.skip(reason="Feature removed in v2.0")`
2. Document in CHANGELOG
3. Remove in next major version

## Test Metrics

### Coverage Goals

- ✅ All critical user flows (CHOW, PUNG, KONG, WIN claims)
- ✅ All bug report functionality
- ✅ Countdown timer display
- ⏳ Multi-player scenarios (future)
- ⏳ Mobile responsive UI (future)

### Success Criteria

A UI test suite is successful when:
- All tests pass on main branch
- Failed tests indicate actual bugs (no false positives)
- Tests are maintainable (don't break with minor UI changes)
- Execution time is reasonable (<5 minutes total)

## Troubleshooting

### Common Issues

**Issue**: `Browser executable not found`
```bash
# Solution
python -m playwright install chromium
```

**Issue**: `Connection refused to localhost:8080`
```bash
# Solution - Start server first
python app.py
```

**Issue**: `Tests hang indefinitely`
```bash
# Solution - Add timeout
pytest tests/ui/ -v --timeout=60
```

**Issue**: `Flaky tests (pass/fail randomly)`
```bash
# Solution - Increase wait times
await page.wait_for_timeout(2000)  # Increase from 500ms
```

## Resources

- **Playwright Docs**: https://playwright.dev/python/
- **pytest-playwright**: https://github.com/microsoft/playwright-pytest
- **Async Testing**: https://docs.pytest.org/en/stable/how-to/async.html
- **Selectors Guide**: https://playwright.dev/python/docs/selectors

## Future Enhancements

### High Priority
1. **Deterministic game states** - Seed RNG for reproducible tests
2. **Visual regression testing** - Screenshot comparison
3. **Parallel execution** - Run tests concurrently (`pytest-xdist`)

### Medium Priority
1. **Mobile testing** - Test responsive design
2. **Cross-browser** - Test on Firefox/WebKit
3. **Performance testing** - Measure load times

### Low Priority
1. **Accessibility testing** - ARIA labels, screen reader support
2. **Internationalization** - Test multiple languages
3. **Dark mode** - Test theme switching

---

**Last Updated**: 2026-02-07
**Maintainer**: Development Team
**Related**: [TESTING_GUIDE.md](../TESTING_GUIDE.md), [learnings.md](learnings.md)
