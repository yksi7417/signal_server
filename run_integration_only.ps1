# Run only integration tests
Write-Host "Running integration tests only..." -ForegroundColor Yellow
pytest -m "integration" -v tests/integration/ -s

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Integration tests passed!" -ForegroundColor Green
} else {
    Write-Host "Integration tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
