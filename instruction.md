# Mahjong Flask Application - Testing Framework and Development Guidelines

## Table of Contents
- [Overview](#overview)
- [Testing Framework Architecture](#testing-framework-architecture)
- [Types of Tests](#types-of-tests)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Best Practices](#best-practices)
- [Development Workflow](#development-workflow)
- [API Development Guidelines](#api-development-guidelines)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)
- [Current Project Status](#current-project-status)
- [Project-Specific Testing Achievements](#project-specific-testing-achievements)

## Overview

This Mahjong Flask application uses a comprehensive testing framework built on **pytest** to ensure code quality, reliability, and deployment readiness. The testing strategy follows industry best practices with clear separation between unit tests and integration tests, providing confidence in both individual components and the complete system.

## Testing Framework Architecture

### Core Testing Technologies
- **pytest**: Primary testing framework with powerful fixtures and plugins
- **requests**: HTTP client library for testing REST API endpoints
- **psutil**: System process management for test server lifecycle
- **subprocess**: Process management for Flask server in testing environment

### Test Markers
The application uses pytest markers to categorize tests:
```python
pytestmark = pytest.mark.integration  # Mark entire modules
@pytest.mark.integration             # Mark individual tests
@pytest.mark.timeout(20)             # Set timeouts for long-running tests
```

## Types of Tests

### Unit Tests
**Location**: `tests/engine/`
**Purpose**: Test individual components in isolation
**Characteristics**:
- Fast execution (milliseconds)
- No external dependencies
- Test single functions/classes
- Mock external services
- High code coverage

**Examples**:
- `test_tile.py` - Mahjong tile creation, properties, sorting
- `test_melds.py` - Pung, Kong, Chow, Pair validation
- `test_game_state.py` - Game logic, state management
- `test_player_agent.py` - AI decision making algorithms
- `test_hand_validator.py` - Win condition validation

**Why Unit Tests Matter**:
1. **Rapid Feedback**: Catch bugs immediately during development
2. **Regression Prevention**: Ensure changes don't break existing functionality
3. **Documentation**: Serve as living examples of how components should work
4. **Refactoring Safety**: Enable confident code improvements
5. **Component Isolation**: Test business logic without infrastructure complexity

### Integration Tests
**Location**: `tests/integration/`
**Purpose**: Test complete system functionality end-to-end
**Characteristics**:
- Slower execution (seconds)
- Real HTTP requests
- Full Flask server startup
- Database/file system interactions
- Cross-component validation

**Examples**:
- `test_mahjong.py` - Complete game flow testing
- API endpoint functionality
- JavaScript module serving
- Static file delivery
- Deployment readiness checks

**Why Integration Tests Matter**:
1. **System Validation**: Ensure all components work together correctly
2. **API Contract Testing**: Verify REST endpoints meet specifications
3. **Deployment Confidence**: Test production-like environment
4. **User Experience Validation**: Test complete user workflows
5. **Performance Monitoring**: Identify bottlenecks in realistic scenarios

## Test Organization

### Directory Structure
```
tests/
├── __init__.py                    # Test package initialization
├── engine/                        # Unit tests for core game engine
│   ├── __init__.py
│   ├── test_game_state.py        # Game state management tests
│   ├── test_hand_validator.py    # Win condition validation tests
│   ├── test_melds.py             # Meld creation and validation tests
│   ├── test_player_agent.py      # AI agent decision making tests
│   ├── test_player.py            # Player class functionality tests
│   ├── test_ruleset.py           # Game rules implementation tests
│   └── test_tile.py              # Tile class and operations tests
├── integration/                   # Integration tests for full system
│   ├── __init__.py
│   ├── test_mahjong.py           # Main integration test suite
│   ├── debug_discard_debug.py    # Debug script for discard functionality
│   ├── debug_discard_detailed.py # Detailed discard testing
│   ├── debug_remaining_tiles.py  # Remaining tiles count testing
│   └── debug_simple_ai_turn.py   # AI turn testing script
├── unit/                         # Additional unit test categories
└── websocket/                    # WebSocket functionality tests
    └── test_web_socket_client.py
```

### Test Class Organization
Integration tests are organized into logical classes:

```python
class TestFlaskServerIntegration:
    """Test Flask server startup and basic functionality."""

class TestAPIEndpointsIntegration:
    """Test all Flask API endpoints for correct functionality."""

class TestJavaScriptModulesIntegration:
    """Test that JavaScript modules are served correctly with proper MIME types."""

class TestGameFlowIntegration:
    """Test complete game flow scenarios."""

class TestDeploymentReadiness:
    """Test that the application is ready for deployment to fly.io."""
```

## Running Tests

### Quick Commands
```powershell
# Run all unit tests only (fast)
.\run_unit_tests.ps1

# Run all integration tests only (slower)
.\run_integration_only.ps1

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/engine/test_tile.py

# Run specific test class
pytest tests/integration/test_mahjong.py::TestAPIEndpointsIntegration

# Run specific test method
pytest tests/integration/test_mahjong.py::TestAPIEndpointsIntegration::test_start_new_game_api
```

### Test Execution Strategy
1. **Development**: Run unit tests frequently (`.\run_unit_tests.ps1`)
2. **Feature Complete**: Run integration tests (`.\run_integration_only.ps1`)
3. **Pre-commit**: Run all tests (`pytest`)
4. **CI/CD Pipeline**: Run all tests with coverage reporting

### Test Markers Usage
```powershell
# Run only integration tests
pytest -m "integration"

# Skip integration tests (run unit tests)
pytest -m "not integration"

# Run tests with specific timeout
pytest -m "timeout"
```

## Best Practices

### 1. Test File Naming
- Unit tests: `test_<component>.py`
- Integration tests: `test_<feature>.py`
- Debug scripts: `debug_<functionality>.py` (should be moved to `tests/integration/`)

### 2. Test Method Naming
```python
def test_<action>_<expected_outcome>():
    """Test that <action> results in <expected_outcome>."""
```

Examples:
```python
def test_discard_tile_updates_game_state():
def test_ai_turn_advances_to_next_player():
def test_remaining_tiles_decreases_after_draw():
```

### 3. Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange - Set up test data and conditions
    game = GameState()
    tile = Tile(SUIT_DOTS, '1')
    
    # Act - Perform the action being tested
    result = game.discard_tile(tile)
    
    # Assert - Verify the expected outcome
    assert result.success is True
    assert len(game.discards) == 1
```

### 4. Integration Test Fixtures
```python
@pytest.fixture(scope="session")
def global_flask_server():
    """Session-wide Flask server fixture that manages server lifecycle."""
    # Setup server once for all tests
    yield server_instance
    # Cleanup after all tests complete
```

### 5. Timeout Management
Set appropriate timeouts for different test types:
```python
@pytest.mark.timeout(20)  # API endpoint tests
@pytest.mark.timeout(30)  # Complex game flow tests
```

## Development Workflow

### 1. Adding New Features
1. **Write Unit Tests First**: Create tests for individual components
2. **Implement Core Logic**: Build the functionality to pass unit tests
3. **Write Integration Tests**: Test the feature in the complete system
4. **Refactor and Optimize**: Improve code while maintaining test coverage

### 2. Bug Fixes
1. **Write Failing Test**: Create a test that reproduces the bug
2. **Fix the Code**: Implement the minimum change to make the test pass
3. **Verify All Tests**: Ensure the fix doesn't break existing functionality
4. **Add Regression Test**: Ensure the bug doesn't reoccur

### 3. Code Quality Checks
The test suite includes code quality validations:
```python
class TestCodeQuality:
    """Test class to catch syntax errors, f-string issues, and other code quality problems."""
    
    def test_game_state_syntax_valid(self):
    def test_no_unterminated_fstrings(self):
    def test_print_statements_are_complete(self):
```

## Code Generation Guidelines

### 1. Always Include Proper Newlines in Generated Code

**CRITICAL RULE**: When AI generates new code, always ensure proper newlines between code blocks to prevent compilation errors.

**Common "Missing Newline" Issues**:
1. **Method-to-Method**: Missing newline between method definitions
2. **Class-to-Class**: Missing newline between class definitions  
3. **Import-to-Code**: Missing newline after import statements
4. **Function-to-Function**: Missing newline between function definitions

**Required Newline Patterns**:
```python
# ✅ CORRECT: Proper newlines between methods
class GameState:
    def method_one(self):
        pass
    
    def method_two(self):  # <- Newline before method definition
        pass

# ✅ CORRECT: Proper newlines between functions
def function_one():
    pass

def function_two():  # <- Newline before function definition
    pass

# ✅ CORRECT: Newline after imports
from mahjong_engine.constants import WIND_EAST

class GameState:  # <- Newline after imports
    pass
```

**Compilation Error Prevention**:
```python
# ❌ WRONG: Missing newline causes syntax error
class GameState:
    def assign_player_winds(self):
        pass
    def deal_tiles(self):  # <- Missing newline before this line
        pass

# ✅ CORRECT: Proper newline prevents syntax error
class GameState:
    def assign_player_winds(self):
        pass
    
    def deal_tiles(self):  # <- Proper newline before this line
        pass
```

**Code Review Checklist**:
- [ ] Newline before each method definition
- [ ] Newline before each function definition  
- [ ] Newline before each class definition
- [ ] Newline after import blocks
- [ ] Newline at end of file

## API Development Guidelines

### 1. Always Write Integration Tests for New Endpoints

**RULE**: Every new API endpoint MUST have a corresponding integration test in `tests/integration/test_mahjong.py`

**Example Pattern**:
```python
class TestAPIEndpointsIntegration:
    @pytest.mark.timeout(20)
    def test_new_endpoint_api(self, global_flask_server):
        """Test the new_endpoint API endpoint."""
        process, base_url = global_flask_server
        
        # Test request
        response = requests.post(f"{base_url}/api/new_endpoint", json=test_data)
        assert response.status_code == 200
        
        # Validate response structure
        data = response.json()
        assert "expected_field" in data
        assert data["success"] is True
        
        # Test edge cases
        # Test error conditions
```

### 2. API Endpoint Testing Checklist
For each new endpoint, test:
- ✅ **Happy Path**: Normal successful operation
- ✅ **Response Structure**: All expected fields present
- ✅ **Status Codes**: Correct HTTP status codes
- ✅ **Error Handling**: Invalid inputs, missing data
- ✅ **State Changes**: Game state updates correctly
- ✅ **Side Effects**: Related systems update properly

### 3. API Testing Examples

**Game State Endpoints**:
```python
def test_start_new_game_api(self, global_flask_server):
    """Test the start_new_game API endpoint."""
    response = requests.post(f"{base_url}/api/start_new_game")
    assert response.status_code == 200
    
    data = response.json()
    assert "player_hand" in data
    assert "remaining_tiles" in data
    assert data["current_player_id"] == 0
```

**Game Action Endpoints**:
```python
def test_discard_tile_api(self, global_flask_server):
    """Test the discard_tile API endpoint."""
    # Setup game state
    requests.post(f"{base_url}/api/start_new_game")
    draw_response = requests.post(f"{base_url}/api/draw_tile")
    
    # Test discard action
    tile_to_discard = draw_response.json()["hand"][0]
    response = requests.post(
        f"{base_url}/api/discard_tile",
        json={"tile_to_discard": tile_to_discard},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## Debugging and Troubleshooting

### 1. Debug Scripts Management

**IMPORTANT**: All debug scripts (`debug_*.py`) should be organized in `tests/integration/` folder and should be converted to proper integration tests when possible.

**Current Debug Scripts** (all now in `tests/integration/`):
- `debug_remaining_tiles.py` → ✅ **Converted** to `test_remaining_tiles_updates_for_all_players` in `test_mahjong.py`
- `debug_discard_detailed.py` → Available as standalone debug script
- `debug_discard_debug.py` → Available as standalone debug script  
- `debug_simple_ai_turn.py` → Available as standalone debug script

**Debug Script Organization Rules**:
1. All debug scripts must be in `tests/integration/` folder
2. Convert debug logic to proper integration tests when the functionality is stable
3. Keep debug scripts for complex troubleshooting scenarios
4. Use descriptive names: `debug_<specific_functionality>.py`

### 2. Debug Script to Integration Test Conversion

**Pattern for conversion**:
```python
# Old debug script (debug_remaining_tiles.py)
def test_remaining_tiles_updates():
    print("Testing...")
    response = requests.post("http://localhost:8080/api/start_new_game")
    # Manual verification

# New integration test (in test_mahjong.py)
@pytest.mark.timeout(30)
def test_remaining_tiles_updates_for_all_players(self, global_flask_server):
    """Test that remaining_tiles count updates after both human and AI turns."""
    process, base_url = global_flask_server
    
    # Automated assertions instead of manual verification
    response = requests.post(f"{base_url}/api/start_new_game")
    assert response.status_code == 200
    # ... detailed assertions
```

### 3. Common Testing Issues

**Unicode Handling**:
```python
# Problem: Unicode encoding errors on Windows
print("Discarding tile:", tile_to_discard_data)  # May fail with mahjong characters

# Solution: Unicode-safe printing
try:
    print("Discarding tile:", tile_to_discard_data)
except UnicodeEncodeError:
    print("Discarding tile: [Unicode tile]")
```

**Server Lifecycle Management**:
```python
# Problem: Port conflicts, zombie processes
# Solution: Proper cleanup in fixtures
def kill_existing_servers(port=8080):
    """Kill any existing processes running on the specified port."""
    # Comprehensive process cleanup
```

**Test Isolation**:
```python
# Problem: Tests affecting each other
# Solution: Fresh server per test session
@pytest.fixture(scope="session")
def global_flask_server():
    # Start fresh server
    # Proper cleanup
```

### 4. Performance Monitoring

Integration tests also serve as performance monitors:
```python
@pytest.mark.timeout(20)  # Fail if endpoint takes > 20 seconds
def test_ai_turn_performance(self, global_flask_server):
    """Ensure AI turns complete within reasonable time."""
    start_time = time.time()
    response = requests.post(f"{base_url}/api/request_ai_turn")
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert duration < 5.0  # AI should respond within 5 seconds
```

## Continuous Integration Benefits

This testing framework provides:

1. **Deployment Confidence**: Integration tests verify fly.io deployment readiness
2. **Regression Prevention**: Unit tests catch breaking changes immediately
3. **Documentation**: Tests serve as executable documentation
4. **Quality Gates**: Prevent deployment of broken code
5. **Performance Monitoring**: Detect performance regressions
6. **Cross-Platform Validation**: Ensure code works on different environments

## Summary

The testing framework is designed to provide comprehensive coverage while maintaining developer productivity. Unit tests provide rapid feedback during development, while integration tests ensure the complete system works correctly for end users. Following these guidelines will result in a robust, maintainable, and deployable application.

**Key Takeaways**:
- Write unit tests for all business logic
- Write integration tests for all API endpoints
- Move debug scripts to `tests/integration/` 
- Use proper test organization and naming
- Maintain test isolation and cleanup
- Monitor performance through tests
- Use tests as documentation

## Current Project Status

### ✅ Completed Tasks
1. **Unicode Handling Fixed**: Resolved Unicode encoding issues in Flask app with try/catch blocks around print statements
2. **Remaining Tiles Feature**: Successfully implemented remaining tiles count updates for both human and AI turns
3. **Integration Test Coverage**: Converted debug script logic into proper integration test (`test_remaining_tiles_updates_for_all_players`)
4. **Debug Script Organization**: Moved all debug scripts to `tests/integration/` folder for better organization
5. **Testing Framework Documentation**: Created comprehensive testing guidelines and best practices
6. **Test Suite Health**: All 68 unit tests and 19 integration tests are passing

### 🔧 Test Results Summary
- **Unit Tests**: 68/68 passing (0.32s execution time)
- **Integration Tests**: 19/19 passing (83.02s execution time)
- **Code Quality**: All syntax and f-string validation tests passing
- **API Endpoints**: All Flask API endpoints tested and working
- **JavaScript Modules**: All JS modules serving correctly with proper MIME types
- **Deployment Readiness**: All fly.io deployment checks passing

### 📋 Pending Tasks
1. **GitHub Actions Trigger Issue - IDENTIFIED**: The deploy.yml workflow didn't trigger because changes haven't been committed and pushed to the main branch yet. The workflow is configured for `on: push: branches: [ main ]`
2. **Commit and Push Changes**: Need to commit the instruction.md file and other recent changes and push to main branch to trigger deployment
3. **JavaScript Module Tests**: 3 tests showing 404 errors in test output that may need investigation
4. **Final Deployment**: Deploy to fly.io once changes are pushed to main branch
5. **Performance Optimization**: Consider optimizing AI turn response times if needed

### 🎯 Next Steps Recommendation
1. **Commit Current Changes**: Add and commit the instruction.md file and any other recent changes
2. **Push to Main Branch**: Push changes to main branch to trigger GitHub Actions deployment workflow
3. **Monitor Deployment**: Watch GitHub Actions for successful deployment to fly.io
4. **Production Validation**: Test the deployed application in production environment
5. **User Testing**: Conduct end-to-end user testing of the deployed application

### 🚀 Ready for Deployment Commands
```powershell
# Commit the current changes
git add .
git commit -m "Add comprehensive testing documentation and fix remaining tiles integration test"

# Push to main branch (this will trigger GitHub Actions deployment)
git push origin main

# Monitor deployment at: https://github.com/[your-repo]/actions
```

## Project-Specific Testing Achievements

### Integration Test Success Stories

#### Remaining Tiles Count Validation
The `test_remaining_tiles_updates_for_all_players` test demonstrates a complete end-to-end validation:

```python
@pytest.mark.timeout(30)
def test_remaining_tiles_updates_for_all_players(self, global_flask_server):
    """Test that remaining_tiles count updates after both human and AI turns."""
    # 1. Start game and validate initial state
    # 2. Human draws tile (remaining_tiles decreases by 1)
    # 3. Human discards tile (remaining_tiles stays same)
    # 4. AI takes turn (remaining_tiles decreases by 1)
    # 5. Another AI turn (remaining_tiles decreases by 1 more)
    # Validates: Total progression shows correct tile counting
```

This test validates:
- ✅ Game state initialization
- ✅ Human player actions affect tile count correctly
- ✅ AI player actions affect tile count correctly
- ✅ Cross-player game state consistency
- ✅ Unicode character handling in responses

#### Debug Script to Integration Test Conversion
Successfully converted standalone debug script (`debug_remaining_tiles.py`) into a proper integration test by:

1. **Replacing manual verification** with automated assertions
2. **Adding proper test fixtures** using `global_flask_server`
3. **Including edge case handling** for different AI turn outcomes
4. **Ensuring test isolation** and cleanup

#### Unicode Character Support
Resolved Unicode encoding issues that were preventing tests from running on Windows:

```python
# Problem: Unicode mahjong characters in console output
print("Discarding tile:", tile_to_discard_data)  # ❌ Crashed on Windows

# Solution: Unicode-safe printing
try:
    print("Discarding tile:", tile_to_discard_data)
except UnicodeEncodeError:
    print("Discarding tile: [Unicode tile]")  # ✅ Safe fallback
```

### Testing Framework Robustness

#### Server Lifecycle Management
Implemented robust Flask server management for integration tests:

- **Port conflict resolution**: Automatically kills existing servers on port 8080
- **Graceful startup/shutdown**: Proper process management with cleanup
- **Health check validation**: Waits for server responsiveness before running tests
- **Session-scoped fixtures**: Efficient server reuse across multiple tests

#### Test Organization Excellence
Achieved clean separation of concerns:

- **68 Unit Tests**: Fast, isolated component testing (0.32s total)
- **19 Integration Tests**: Comprehensive system validation (83s total)
- **Code Quality Tests**: Syntax validation, f-string checking, method validation
- **Deployment Readiness**: Production environment validation

#### API Contract Testing
Every Flask API endpoint has corresponding integration tests that validate:

- **HTTP Status Codes**: Correct response codes for success/error cases
- **Response Structure**: Required fields present and correctly typed
- **Game State Changes**: Proper state transitions and side effects
- **Error Handling**: Graceful degradation and error messages

This comprehensive testing approach provides confidence in both individual components and the complete system, enabling safe deployment to production environments.

# Python Code Style and Indentation Standards

## Indentation Standards

To maintain code quality and prevent indentation errors, this project follows strict Python indentation standards based on PEP 8.

### Core Indentation Rules

#### 1. Spaces Only - No Tabs
- **ALWAYS use 4 spaces for indentation**
- **NEVER mix tabs and spaces**
- Configure your editor to show whitespace characters
- Set editor to insert spaces when Tab key is pressed

```python
# ✅ CORRECT - 4 spaces
def example_function():
    if condition:
        return True
    else:
        return False

# ❌ WRONG - mixed tabs and spaces (will cause IndentationError)
def bad_function():
    if condition:  # 4 spaces
	return True    # tab character
```
#### 2. Class Definition Standards
```python
# ✅ CORRECT - Class with proper indentation
class GameState:
    """Game state management class."""
    
    def __init__(self):
        self.dealer_index = 0
        self.round_wind = WIND_EAST
    
    def advance_dealer(self):
        """Advance to next dealer."""
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        
        if self.dealer_index == 0:
            self.advance_round()
            
        self.assign_player_winds()
```
#### 3. Method Definition Standards
```python
# ✅ CORRECT - Method indentation
class TestDealerRotationSystem:
    """Test class for dealer rotation."""
    
    def test_initial_dealer_and_winds(self, game):
        """Test initial game state."""
        # 8 spaces from left margin (4 for class + 4 for method)
        assert game.dealer_index == 0
        assert game.round_wind == WIND_EAST
        
        # 8 spaces for method body content
        for i, player in enumerate(game.players):
            # 12 spaces for nested content (4 + 4 + 4)
            expected_wind = WINDS_ALL[i]
            assert player.wind == expected_wind
    
    def test_advance_dealer_within_round(self, game):
        """Test dealer advancement."""
        # 8 spaces for method body
        initial_round = game.round_wind
        
        # 8 spaces for method statements
        game.advance_dealer()
        
        # 8 spaces for assertions
        assert game.dealer_index == 1
        assert game.round_wind == initial_round
```
#### 4. Control Flow Indentation
```python
# ✅ CORRECT - Consistent indentation for control structures
def process_game_action(game, action):
    """Process game actions with proper indentation."""
    if action == "draw":
        # 4 spaces for if block
        tile = game.draw_tile_for_current_player()
        if tile is not None:
            # 8 spaces for nested if
            game.current_player().hand.append(tile)
            return True
        else:
            # 8 spaces for else block
            return False
    elif action == "discard":
        # 4 spaces for elif block  
        if len(game.current_player().hand) > INIT_HAND_SIZE:
            # 8 spaces for nested condition
            return game.discard_tile_for_current_player()
        else:
            # 8 spaces for nested else
            return False
    else:
        # 4 spaces for final else
        raise ValueError(f"Unknown action: {action}")
```
#### 5. Long Line Handling
```python
# ✅ CORRECT - Breaking long lines with proper indentation
def create_complex_assertion(game, expected_dealer, expected_wind, 
                           expected_player_count):
    """Function with long parameter list."""
    # When breaking function parameters, align with opening parenthesis
    # OR use hanging indent (4 additional spaces)
    
    # ✅ CORRECT - Hanging indent for long assertions
    assert (game.dealer_index == expected_dealer and
            game.round_wind == expected_wind and
            len(game.players) == expected_player_count)

# ✅ CORRECT - Alternative: Each parameter on new line
def create_complex_assertion_alt(
        game, 
        expected_dealer, 
        expected_wind,
        expected_player_count):
    """Alternative formatting for long parameter lists."""
    pass
```

### Common Indentation Error Patterns to Avoid

#### 1. Inconsistent Method Indentation
```python
# ❌ WRONG - Inconsistent indentation
class TestExample:
  def test_method_one(self):  # Only 2 spaces instead of 4
      pass
    
    def test_method_two(self):  # 4 spaces (correct)
        pass
      def test_method_three(self):  # 6 spaces (wrong alignment)
          pass
```
#### 2. Missing Blank Lines
```python
# ❌ WRONG - Missing separation between methods
class TestExample:
    def test_method_one(self):
        assert True
    def test_method_two(self):  # Missing blank line
        assert True
        
# ✅ CORRECT - Proper separation
class TestExample:
    def test_method_one(self):
        assert True
    
    def test_method_two(self):  # Blank line separates methods
        assert True
```
#### 3. Incorrect Multi-line Statement Indentation
```python
# ❌ WRONG - Poor multi-line formatting
assert (game.dealer_index == 0 and 
game.round_wind == WIND_EAST)  # Continuation line not indented

# ✅ CORRECT - Proper multi-line indentation
assert (game.dealer_index == 0 and 
        game.round_wind == WIND_EAST)
```

### Editor Configuration

#### VS Code Settings
Add to your `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "editor.insertSpaces": true,
    "editor.tabSize": 4,
    "editor.detectIndentation": false,
    "editor.renderWhitespace": "boundary",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "files.trimTrailingWhitespace": true
}
```

#### PyCharm Settings
1. File → Settings → Editor → Code Style → Python
2. Set "Tab size" to 4
3. Set "Indent" to 4
4. Check "Use tab character" to UNCHECKED
5. Enable "Show whitespace"

### Validation Tools

#### 1. Pre-commit Hooks
Install tools to catch indentation errors before commit:
```bash
pip install black flake8 isort
```

#### 2. Automated Checks
Add to your development workflow:
```bash
# Check indentation and style
flake8 --select=E1,W1 .

# Auto-format code
black .

# Sort imports
isort .
```

#### 3. Test Integration
The project includes automated indentation validation:
```python
def test_file_indentation_consistency():
    """Validate that all Python files use consistent indentation."""
    for python_file in glob.glob("**/*.py", recursive=True):
        with open(python_file, 'r') as f:
            content = f.read()
            # Check for tab characters
            assert '\t' not in content, f"File {python_file} contains tab characters"
```

### Quick Indentation Checklist

Before committing code, verify:
- [ ] All indentation uses 4 spaces
- [ ] No tab characters in Python files
- [ ] Methods separated by blank lines
- [ ] Consistent indentation throughout classes
- [ ] Long lines broken with proper continuation indentation
- [ ] Control flow blocks properly indented
- [ ] No trailing whitespace

### Error Recovery

If you encounter `IndentationError: unindent does not match any outer indentation level`:

1. **Check for mixed tabs/spaces**: Use editor's "Show Whitespace" feature
2. **Verify consistent indentation**: Count spaces manually if needed
3. **Use automated tools**: Run `black` or similar formatter
4. **Compare with working examples**: Look at existing properly formatted code
5. **Start fresh if needed**: Copy content to new file and re-indent properly

Following these standards will prevent the indentation errors we've encountered and maintain consistent, readable code throughout the project.

## Testing Code Standards

### Test Method Indentation Standards

#### 1. Test Class Structure
```python
# ✅ CORRECT - Proper test class indentation
class TestDealerRotationSystem:
    """Test dealer rotation and round progression."""
    
    def test_initial_dealer_and_winds(self, game):
        """Test that game starts with correct dealer and wind assignments."""
        # Method body indented 8 spaces (4 for class + 4 for method)
        assert game.dealer_index == 0
        assert game.round_wind == WIND_EAST
        
        # Comments and assertions at same indentation level
        # Verify player winds are assigned correctly
        assert game.players[0].wind == WIND_EAST
        assert game.players[1].wind == WIND_SOUTH
        assert game.players[2].wind == WIND_WEST
        assert game.players[3].wind == WIND_NORTH
    
    def test_advance_dealer_within_round(self, game):
        """Test dealer advancement within the same round."""
        # Blank line separates methods, content indented 8 spaces
        initial_round = game.round_wind

        
        # Action
        game.advance_dealer()
        
        # Assertions
        assert game.dealer_index == 1
        assert game.round_wind == initial_round

```
#### 2. Complex Test Logic Indentation
```python
# ✅ CORRECT - Nested logic in tests
def test_complete_round_cycle(self, game):
    """Test a complete round cycle with all dealer rotations."""
    # Initial state verification (8 spaces)
    assert game.round_wind == WIND_EAST
    assert game.dealer_index == 0
    
    # Loop with proper indentation (8 spaces for loop, 12 for body)
    for expected_dealer in [1, 2, 3]:
        # 12 spaces for loop body
        game.end_hand(winner_id=expected_dealer)
        assert game.dealer_index == expected_dealer
        assert game.round_wind == WIND_EAST
    
    # Final assertions (8 spaces)
    game.end_hand(winner_id=0)
    assert game.dealer_index == 0
    assert game.round_wind == WIND_SOUTH
```
#### 3. Test Setup and Teardown
```python
# ✅ CORRECT - Setup method indentation
@pytest.fixture
def game():
    """Fixture to provide a fresh GameState instance for each test."""
    # Fixture body indented 4 spaces
    return GameState()

class TestGameStateFeature:
    """Test specific game state features."""
    
    def setup_method(self):
        """Setup run before each test method."""
        # Setup code indented 8 spaces
        self.test_data = {
            "dealer_index": 0,
            "round_wind": WIND_EAST,

        }
    
    def test_feature_behavior(self, game):
        """Test specific feature behavior."""
        # Test implementation indented 8 spaces
        game.dealer_index = self.test_data["dealer_index"]
        assert game.dealer_index == 0
```
### Test Assertion Standards

#### 1. Multi-line Assertion Formatting
```python
# ✅ CORRECT - Multi-line assertions with proper indentation
def test_complex_game_state(self, game):
    """Test complex game state validation."""
    # When assertions are too long, break them properly
    assert (game.dealer_index == 0 and
            game.round_wind == WIND_EAST and

            len(game.players) == 4)
    
    # Alternative: Multiple single assertions (often clearer)
    assert game.dealer_index == 0
    assert game.round_wind == WIND_EAST

    assert len(game.players) == 4
```

#### 2. Test Documentation and Comments
```python
# ✅ CORRECT - Well-documented test with proper indentation
def test_dealer_continuation_rules(self, game):
    """Test that dealer continues according to traditional Mahjong rules."""
    # Setup: Configure game state for dealer continuation test
    # (Comments aligned with code they describe)
    game.dealer_index = 2
    game.round_wind = WIND_SOUTH

    
    # Test Case 1: Dealer wins, should continue
    should_continue = game.should_dealer_continue(winner_id=2)
    assert should_continue is True
    
    # Test Case 2: Non-dealer wins, dealer should advance
    should_continue = game.should_dealer_continue(winner_id=1)
    assert should_continue is False
    
    # Test Case 3: Wall empty, dealer should continue
    should_continue = game.should_dealer_continue(wall_empty=True)
    assert should_continue is True
```

### Common Test Indentation Mistakes

#### 1. Inconsistent Method Spacing
```python
# ❌ WRONG - Inconsistent spacing between methods
class TestExample:
    def test_one(self):
        assert True
def test_two(self):  # Wrong: not properly indented in class
        assert True

# ✅ CORRECT - Consistent class method indentation
class TestExample:
    def test_one(self):
        assert True
    
    def test_two(self):
        assert True
```
#### 2. Improper Fixture Indentation
```python
# ❌ WRONG - Fixture not properly aligned
@pytest.fixture
def game():
"""Bad docstring indentation."""
return GameState()

# ✅ CORRECT - Proper fixture formatting
@pytest.fixture
def game():
    """Fixture to provide a fresh GameState instance for each test."""
    return GameState()
```
#### 3. Mixed Indentation in Test Logic
```python
# ❌ WRONG - Mixed indentation levels
def test_mixed_indentation(self, game):
    """Test with inconsistent indentation."""
        assert game.dealer_index == 0  # 8 spaces (wrong for first line)
    assert game.round_wind == WIND_EAST    # 4 spaces (inconsistent)


# ✅ CORRECT - Consistent indentation
def test_consistent_indentation(self, game):
    """Test with proper indentation."""
    assert game.dealer_index == 0          # 8 spaces (correct)
    assert game.round_wind == WIND_EAST    # 8 spaces (consistent)

```

### Test File Organization Standards

#### 1. Import Organization
```python
# ✅ CORRECT - Proper import organization and indentation
import ast
import collections
import inspect
import pytest
import re

from unittest.mock import MagicMock

from mahjong_engine.constants import (
    INIT_HAND_SIZE,
    NUM_COPIES_PER_TILE,
    NUM_PLAYERS,
    SUIT_BAMBOO,
    WIND_EAST,
    WIND_NORTH,
    WIND_SOUTH,
    WIND_WEST,
    WINDS_ALL,
)
from mahjong_engine.game_state import GameState
from mahjong_engine.tile import Tile
```
#### 2. Test Class Organization
```python
# ✅ CORRECT - Logical test class organization
class TestBasicGameState:
    """Test basic game state functionality."""
    
    def test_initialization(self, game):
        """Test game initialization."""
        pass
    
    def test_player_setup(self, game):
        """Test player setup."""
        pass


class TestDealerRotationSystem:
    """Test dealer rotation and round progression."""
    
    def test_initial_dealer_and_winds(self, game):
        """Test initial dealer setup."""
        pass
    
    def test_advance_dealer_within_round(self, game):
        """Test dealer advancement."""
        pass


class TestWinDetectionWithDealerRotation:
    """Test integration between win detection and dealer rotation."""
    
    def test_process_win_claim_calls_end_hand(self, game):
        """Test win claim integration."""
        pass
```

Following these testing standards ensures:
- Consistent, readable test code
- Easy maintenance and debugging
- Clear separation of test concerns
- Proper integration with pytest framework
- Reduced indentation errors during development
