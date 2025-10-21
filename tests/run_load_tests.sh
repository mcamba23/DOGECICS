#!/bin/bash
# Run K6 load tests

echo "================================================"
echo "Running DOGECICS Load Tests with K6"
echo "================================================"

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "K6 is not installed. Installing..."
    
    # Check OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install k6
    else
        echo "Please install k6 manually from https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
fi

# Create reports directory
mkdir -p tests/reports

# Run basic load test
echo ""
echo "1. Running Basic Load Test..."
k6 run tests/load/basic-load-test.js

# Run stress test
echo ""
echo "2. Running Stress Test..."
k6 run tests/load/stress-test.js

# Run spike test
echo ""
echo "3. Running Spike Test..."
k6 run tests/load/spike-test.js

# Run soak test (optional, takes long time)
if [ "$1" == "--full" ]; then
    echo ""
    echo "4. Running Soak Test (this will take ~24 minutes)..."
    k6 run tests/load/soak-test.js
else
    echo ""
    echo "4. Skipping Soak Test (use --full flag to run it)"
fi

echo ""
echo "================================================"
echo "Load test reports saved to tests/reports/"
echo "================================================"
