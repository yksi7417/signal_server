# Integration test runner for Mahjong Flask application
# This script runs all the integration tests that verify deployment readiness

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Mahjong Flask Integration Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "[1/5] Running Code Quality Tests..." -ForegroundColor Yellow
    python -m pytest tests/engine/test_game_state.py::TestCodeQuality -v
    if ($LASTEXITCODE -ne 0) {
        throw "Code quality tests failed!"
    }

    Write-Host ""
    Write-Host "[2/5] Running Flask Server Integration Tests..." -ForegroundColor Yellow
    python -m pytest tests/integration/test_integration.py::TestFlaskServerIntegration -v
    if ($LASTEXITCODE -ne 0) {
        throw "Flask server integration tests failed!"
    }

    Write-Host ""
    Write-Host "[3/5] Running API Endpoints Integration Tests..." -ForegroundColor Yellow
    python -m pytest tests/integration/test_integration.py::TestAPIEndpointsIntegration -v
    if ($LASTEXITCODE -ne 0) {
        throw "API endpoints integration tests failed!"
    }

    Write-Host ""
    Write-Host "[4/5] Running JavaScript Modules Integration Tests..." -ForegroundColor Yellow
    python -m pytest tests/integration/test_integration.py::TestJavaScriptModulesIntegration -v
    if ($LASTEXITCODE -ne 0) {
        throw "JavaScript modules integration tests failed!"
    }

    Write-Host ""
    Write-Host "[5/5] Running Deployment Readiness Tests..." -ForegroundColor Yellow
    python -m pytest tests/integration/test_integration.py::TestDeploymentReadiness -v
    if ($LASTEXITCODE -ne 0) {
        throw "Deployment readiness tests failed!"
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "ALL INTEGRATION TESTS PASSED!" -ForegroundColor Green
    Write-Host "Application is ready for deployment to fly.io" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To deploy to fly.io, run:" -ForegroundColor Cyan
    Write-Host "  fly deploy" -ForegroundColor White
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Integration tests failed. Please fix the issues before deploying." -ForegroundColor Red
    exit 1
}
