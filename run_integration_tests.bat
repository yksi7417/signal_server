@echo off
REM Integration test runner for Mahjong Flask application
REM This script runs all the integration tests that verify deployment readiness

echo ==========================================
echo Running Mahjong Flask Integration Tests
echo ==========================================
echo.

echo [1/5] Running Code Quality Tests...
python -m pytest tests/engine/test_game_state.py::TestCodeQuality -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Code quality tests failed!
    pause
    exit /b 1
)

echo.
echo [2/5] Running Flask Server Integration Tests...
python -m pytest tests/integration/test_integration.py::TestFlaskServerIntegration -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Flask server integration tests failed!
    pause
    exit /b 1
)

echo.
echo [3/5] Running API Endpoints Integration Tests...
python -m pytest tests/integration/test_integration.py::TestAPIEndpointsIntegration -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: API endpoints integration tests failed!
    pause
    exit /b 1
)

echo.
echo [4/5] Running JavaScript Modules Integration Tests...
python -m pytest tests/integration/test_integration.py::TestJavaScriptModulesIntegration -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: JavaScript modules integration tests failed!
    pause
    exit /b 1
)

echo.
echo [5/5] Running Deployment Readiness Tests...
python -m pytest tests/integration/test_integration.py::TestDeploymentReadiness -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Deployment readiness tests failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ALL INTEGRATION TESTS PASSED!
echo Application is ready for deployment to fly.io
echo ==========================================
echo.
echo To deploy to fly.io, run:
echo   fly deploy
echo.
pause
