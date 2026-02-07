#!/bin/bash
# Run integration tests in Docker container

set -e

echo "🧪 Starting Signal Server Integration Tests"
echo "============================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.integration.yml down -v --remove-orphans 2>/dev/null || true

# Build and start services
echo "🔨 Building test environment..."
docker-compose -f docker-compose.integration.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.integration.yml up -d

# Wait for server to be healthy
echo "⏳ Waiting for server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        echo "✅ Server is ready!"
        break
    fi
    echo "   Attempt $i/30..."
    sleep 2
done

# Check if server is actually ready
if ! curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "❌ Server failed to start"
    echo "📋 Container logs:"
    docker-compose -f docker-compose.integration.yml logs signal-server
    docker-compose -f docker-compose.integration.yml down -v
    exit 1
fi

# Run tests
echo ""
echo "🧪 Running integration tests..."
echo "================================"

TEST_RESULT=0

# Run game simulation tests
echo ""
echo "📋 Test Suite: Game Simulation"
docker-compose -f docker-compose.integration.yml exec -T test-runner \
    pytest tests/integration/test_full_game.py::TestCompleteGameFlow -v --tb=short || TEST_RESULT=1

# Run rules compliance tests
echo ""
echo "📋 Test Suite: Rules Compliance"
docker-compose -f docker-compose.integration.yml exec -T test-runner \
    pytest tests/integration/test_full_game.py::TestRulesCompliance -v --tb=short || TEST_RESULT=1

# Run API contract tests
echo ""
echo "📋 Test Suite: API Contract"
docker-compose -f docker-compose.integration.yml exec -T test-runner \
    pytest tests/integration/test_full_game.py::TestAPIContract -v --tb=short || TEST_RESULT=1

# Run scenario loader tests
echo ""
echo "📋 Test Suite: Scenario Loader"
docker-compose -f docker-compose.integration.yml exec -T test-runner \
    pytest tests/integration/test_full_game.py::TestScenarioLoader -v --tb=short || TEST_RESULT=1

# Copy test results
echo ""
echo "📊 Copying test results..."
docker-compose -f docker-compose.integration.yml cp test-runner:/app/test-results ./test-results 2>/dev/null || true

# Show test report location
if [ -f "./test-results/report.html" ]; then
    echo ""
    echo "📈 Test report available at:"
    echo "   file://$(pwd)/test-results/report.html"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.integration.yml down -v

# Final result
echo ""
echo "================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All integration tests passed!"
    exit 0
else
    echo "❌ Some integration tests failed"
    exit 1
fi
