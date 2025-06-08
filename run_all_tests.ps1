# Run all tests (unit + integration)
Write-Host "Running all tests (unit + integration)..." -ForegroundColor Cyan
pytest -v

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
