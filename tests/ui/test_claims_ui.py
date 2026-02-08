"""
UI Tests for Claim Functionality

Tests the bug fixes implemented:
1. CHOW claim buttons respond (not frozen)
2. PUNG claim buttons respond
3. Countdown timer displays and updates
4. Bug report button works

Run with: pytest tests/ui/test_claims_ui.py -v
"""

import pytest
import asyncio
import re
from playwright.async_api import async_playwright, expect


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for CI
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """Create a new page for each test"""
    context = await browser.new_context()
    page = await context.new_page()

    # Navigate to game page
    await page.goto('http://localhost:8080/game')
    await page.wait_for_load_state('networkidle')

    # Click Reset to start a fresh game
    await page.click('#reset')
    await page.wait_for_timeout(1000)  # Wait for game to initialize

    yield page

    await context.close()


class TestCHOWClaims:
    """Test CHOW claim UI functionality - Bug Fix Verification"""

    @pytest.mark.asyncio
    async def test_chow_buttons_are_visible_and_enabled(self, page):
        """
        Bug Fix: CHOW claim buttons were frozen/unresponsive
        Test: Verify buttons become enabled when CHOW opportunity appears
        """
        # Play game until CHOW opportunity appears
        max_attempts = 20
        for _ in range(max_attempts):
            # Check if CHOW prompt appeared
            console_text = await page.inner_text('#player-console')
            if 'can claim it as a CHOW' in console_text or 'CHOW' in console_text:
                break

            # Otherwise, play a turn
            if await page.is_enabled('#btnDrawTile'):
                await page.click('#btnDrawTile')
                await page.wait_for_timeout(500)

            if await page.is_enabled('#btnDiscardTile'):
                await page.click('#btnDiscardTile')
                await page.wait_for_timeout(500)

            await page.wait_for_timeout(1000)  # Wait for AI turns

        # Verify buttons are enabled when CHOW appears
        yes_button = page.locator('#btnClaimYes')
        no_button = page.locator('#btnClaimNo')

        # Should be enabled
        await expect(yes_button).to_be_enabled()
        await expect(no_button).to_be_enabled()

    @pytest.mark.asyncio
    async def test_chow_yes_button_responds(self, page):
        """
        Bug Fix: CHOW Yes button was unresponsive (UI frozen)
        Test: Clicking Yes should process the claim without freezing
        """
        # Navigate to CHOW opportunity
        await self._navigate_to_chow_opportunity(page)

        # Get initial console text
        console_before = await page.inner_text('#player-console')

        # Click Yes button
        await page.click('#btnClaimYes')

        # Wait for response
        await page.wait_for_timeout(2000)

        # Console text should change (not frozen)
        console_after = await page.inner_text('#player-console')
        assert console_after != console_before, "Console did not update - UI may be frozen"

        # Should show success message or discard prompt
        assert any(phrase in console_after for phrase in [
            'claimed Chow',
            'Your turn to discard',
            'Chow claim'
        ]), f"Unexpected message: {console_after}"

    @pytest.mark.asyncio
    async def test_chow_no_button_responds(self, page):
        """
        Bug Fix: CHOW No button was unresponsive (UI frozen)
        Test: Clicking No should decline the claim
        """
        # Navigate to CHOW opportunity
        await self._navigate_to_chow_opportunity(page)

        # Click No button
        await page.click('#btnClaimNo')

        # Wait for response
        await page.wait_for_timeout(2000)

        # Console should show declined message
        console_text = await page.inner_text('#player-console')
        assert any(phrase in console_text for phrase in [
            'declined',
            'Game continues',
            'Chow claim declined'
        ]), f"Expected decline message, got: {console_text}"

    @staticmethod
    async def _navigate_to_chow_opportunity(page):
        """Helper: Play game until CHOW opportunity appears"""
        max_attempts = 30
        for attempt in range(max_attempts):
            console_text = await page.inner_text('#player-console')

            # Check if CHOW opportunity appeared
            if 'CHOW' in console_text and 'Do you want to claim' in console_text:
                return

            # Play turns
            if await page.is_enabled('#btnDrawTile'):
                await page.click('#btnDrawTile')
                await page.wait_for_timeout(500)

            if await page.is_enabled('#btnDiscardTile'):
                # Select first tile and discard
                tiles = page.locator('#player-hand .tile')
                if await tiles.count() > 0:
                    await tiles.first.click()
                    await page.wait_for_timeout(300)
                    await page.click('#btnDiscardTile')
                    await page.wait_for_timeout(500)

            await page.wait_for_timeout(2000)  # Wait for AI turns

        pytest.skip(f"CHOW opportunity did not appear after {max_attempts} attempts")


class TestPUNGClaims:
    """Test PUNG claim UI functionality - Bug Fix Verification"""

    @pytest.mark.asyncio
    async def test_pung_buttons_respond(self, page):
        """
        Bug Fix: PUNG claims had Unicode crash on backend
        Test: PUNG claim should complete without server error
        """
        # Navigate to PUNG opportunity
        await self._navigate_to_pung_opportunity(page)

        # Click Yes button
        await page.click('#btnClaimYes')

        # Wait for response
        await page.wait_for_timeout(2000)

        # Should not show backend error
        console_text = await page.inner_text('#player-console')
        assert 'Backend failed' not in console_text, "Backend crash detected"
        assert 'Error claiming' not in console_text, "Claim processing failed"

    @staticmethod
    async def _navigate_to_pung_opportunity(page):
        """Helper: Play game until PUNG opportunity appears"""
        max_attempts = 30
        for attempt in range(max_attempts):
            console_text = await page.inner_text('#player-console')

            if 'PUNG' in console_text and 'Do you want to claim' in console_text:
                return

            # Play turns
            if await page.is_enabled('#btnDrawTile'):
                await page.click('#btnDrawTile')
                await page.wait_for_timeout(500)

            if await page.is_enabled('#btnDiscardTile'):
                tiles = page.locator('#player-hand .tile')
                if await tiles.count() > 0:
                    await tiles.first.click()
                    await page.wait_for_timeout(300)
                    await page.click('#btnDiscardTile')
                    await page.wait_for_timeout(500)

            await page.wait_for_timeout(2000)

        pytest.skip(f"PUNG opportunity did not appear after {max_attempts} attempts")


class TestCountdownTimer:
    """Test countdown timer functionality - Feature Verification"""

    @pytest.mark.asyncio
    async def test_countdown_displays_30_seconds(self, page):
        """
        Feature: 30-second countdown timer with real-time display
        Test: Countdown should start at 30 and decrement every second
        """
        # Navigate to any claim opportunity
        await self._navigate_to_claim_opportunity(page)

        # Get initial countdown value
        console_text = await page.inner_text('#player-console')

        # Extract countdown value using regex
        match = re.search(r'(\d+)s\)', console_text)
        if match:
            initial_seconds = int(match.group(1))
            assert initial_seconds == 30, f"Expected 30s, got {initial_seconds}s"
        else:
            pytest.fail(f"Countdown not found in: {console_text}")

    @pytest.mark.asyncio
    async def test_countdown_decrements_in_realtime(self, page):
        """
        Feature: Real-time countdown updates
        Test: Countdown value should decrease every second
        """
        # Navigate to claim opportunity
        await self._navigate_to_claim_opportunity(page)

        # Capture countdown values over 3 seconds
        countdown_values = []
        for _ in range(3):
            console_text = await page.inner_text('#player-console')
            match = re.search(r'(\d+)s\)', console_text)
            if match:
                countdown_values.append(int(match.group(1)))
            await page.wait_for_timeout(1000)  # Wait 1 second

        # Verify countdown is decreasing
        assert len(countdown_values) >= 2, "Could not capture countdown values"
        assert countdown_values[0] > countdown_values[-1], \
            f"Countdown not decreasing: {countdown_values}"

    @staticmethod
    async def _navigate_to_claim_opportunity(page):
        """Helper: Play until any claim opportunity appears"""
        max_attempts = 30
        for attempt in range(max_attempts):
            console_text = await page.inner_text('#player-console')

            # Check for any claim type
            if any(claim in console_text for claim in ['CHOW', 'PUNG', 'KONG', 'WIN']):
                if 'Do you want to claim' in console_text:
                    return

            # Play turns
            if await page.is_enabled('#btnDrawTile'):
                await page.click('#btnDrawTile')
                await page.wait_for_timeout(500)

            if await page.is_enabled('#btnDiscardTile'):
                tiles = page.locator('#player-hand .tile')
                if await tiles.count() > 0:
                    await tiles.first.click()
                    await page.wait_for_timeout(300)
                    await page.click('#btnDiscardTile')
                    await page.wait_for_timeout(500)

            await page.wait_for_timeout(2000)

        pytest.skip(f"Claim opportunity did not appear after {max_attempts} attempts")


class TestBugReporting:
    """Test bug report functionality"""

    @pytest.mark.asyncio
    async def test_bug_report_button_visible(self, page):
        """
        Feature: Bug report button
        Test: Button should be visible on page load
        """
        # Scroll to bottom where button is located
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

        # Check if bug report button exists and is visible
        bug_button = page.locator('#btnReportBug')
        await expect(bug_button).to_be_visible()

    @pytest.mark.asyncio
    async def test_bug_report_modal_opens(self, page):
        """
        Feature: Bug report modal
        Test: Clicking button should open modal
        """
        # Scroll and click bug report button
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.click('#btnReportBug')

        # Modal should appear
        modal = page.locator('#bugReportModal')
        await expect(modal).to_be_visible()

        # Modal should have title
        title = page.locator('#bugReportModal h2')
        await expect(title).to_have_text('Report a Bug')

    @pytest.mark.asyncio
    async def test_bug_report_submission(self, page):
        """
        Feature: Bug report submission
        Test: Submitting report should succeed
        """
        # Open modal
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.click('#btnReportBug')
        await page.wait_for_timeout(500)

        # Fill in description
        await page.fill('#bugDescription', 'Automated UI test bug report')

        # Submit
        await page.click('#submitBugReport')

        # Wait for response
        await page.wait_for_timeout(2000)

        # Should show success message
        result_area = page.locator('#bugReportResult')
        await expect(result_area).to_be_visible()

        result_text = await result_area.inner_text()
        assert 'Bug reported' in result_text or 'success' in result_text.lower(), \
            f"Unexpected result: {result_text}"


class TestClaimPositionRules:
    """Test CHOW position rule enforcement"""

    @pytest.mark.asyncio
    async def test_chow_only_from_left_neighbor(self, page):
        """
        Rule: CHOW can only be claimed from left neighbor (Player 3 → Player 0)
        Test: CHOW prompt should only appear when Player 3 discards
        """
        # Track which players trigger CHOW prompts
        chow_prompts_from_players = set()

        # Play multiple rounds
        for _ in range(20):
            console_text = await page.inner_text('#player-console')

            # Check if CHOW prompt appeared
            if 'CHOW' in console_text and 'Player' in console_text:
                # Extract player number (e.g., "Player 3 discarded")
                match = re.search(r'Player (\d+)', console_text)
                if match:
                    player_num = int(match.group(1))
                    chow_prompts_from_players.add(player_num)

                # Decline to continue testing
                if await page.is_enabled('#btnClaimNo'):
                    await page.click('#btnClaimNo')
                    await page.wait_for_timeout(1000)

            # Play a turn
            if await page.is_enabled('#btnDrawTile'):
                await page.click('#btnDrawTile')
                await page.wait_for_timeout(500)

            if await page.is_enabled('#btnDiscardTile'):
                tiles = page.locator('#player-hand .tile')
                if await tiles.count() > 0:
                    await tiles.first.click()
                    await page.wait_for_timeout(300)
                    await page.click('#btnDiscardTile')
                    await page.wait_for_timeout(500)

            await page.wait_for_timeout(2000)

        # Verify only Player 3 (left neighbor) triggered CHOW prompts
        if chow_prompts_from_players:
            assert chow_prompts_from_players == {3}, \
                f"CHOW should only come from Player 3, got: {chow_prompts_from_players}"


# Mark all tests as UI tests for selective running
pytestmark = pytest.mark.ui
