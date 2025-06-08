# Run only unit tests (skip integration tests)
Write-Host "Running unit tests only (skipping integration tests)..." -ForegroundColor Green
pytest -m "not integration" -v

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Unit tests passed!" -ForegroundColor Green
} else {
    Write-Host "Unit tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
