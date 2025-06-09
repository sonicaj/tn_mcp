#!/bin/bash

# Script to run TrueNAS middleware unit tests using Docker
# Based on the GitHub Actions workflow

set -e

# Configuration
CONTAINER_NAME="truenas-middleware-test"
MIDDLEWARE_PATH="${1:-/Users/waqar/Desktop/work/ixsystems/codes/middleware}"
TEST_FILE="$2"

# Show usage
show_usage() {
    echo "Usage: $0 [path_to_middleware_repo] [test_file|--cleanup]"
    echo ""
    echo "Options:"
    echo "  path_to_middleware_repo  Path to middleware repository (default: /Users/waqar/Desktop/work/ixsystems/codes/middleware)"
    echo "  test_file               Specific test file to run (e.g., test_construct_schema.py)"
    echo "  --cleanup               Remove the test container"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 /path/to/middleware                # Run all tests with custom path"
    echo "  $0 . test_construct_schema.py         # Run specific test"
    echo "  $0 /path/to/middleware --cleanup      # Clean up container"
}

if [ ! -d "$MIDDLEWARE_PATH" ]; then
    echo "Error: Middleware repository not found at $MIDDLEWARE_PATH"
    show_usage
    exit 1
fi

echo "Running middleware unit tests from: $MIDDLEWARE_PATH"

# Check for cleanup option first
if [ "$2" = "--cleanup" ]; then
    echo "Cleaning up: Stopping and removing container..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    echo "Container removed."
    exit 0
fi

# Enable Docker buildx if not already enabled
docker buildx version >/dev/null 2>&1 || docker buildx install

# Check if container exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container '${CONTAINER_NAME}' already exists."
    
    # Check if container is running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "Container is already running."
    else
        echo "Starting existing container..."
        docker start "${CONTAINER_NAME}"
    fi
else
    echo "Creating new container '${CONTAINER_NAME}'..."
    
    # Create and start container with initial setup
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --platform linux/amd64 \
        -v "$MIDDLEWARE_PATH:/workspace/middleware" \
        -w /workspace/middleware \
        ghcr.io/truenas/middleware:master \
        tail -f /dev/null  # Keep container running
    
    echo "Container created. Running initial setup..."
    
    # Run initial setup in the container
    docker exec "${CONTAINER_NAME}" bash -c "
        set -e
        echo 'Installing development tools...'
        
        # Install dev tools
        ./src/freenas/usr/bin/install-dev-tools
        
        # Reinstall middleware in container
        echo 'Reinstalling middleware in container...'
        cd src/middlewared && make reinstall_container
        
        # Create a marker file to indicate setup is complete
        touch /tmp/setup_complete
        
        echo 'Initial setup completed!'
    "
    
    echo "Initial setup finished. Container is ready for testing."
fi

# Check if initial setup is complete
echo "Checking if container setup is complete..."
if ! docker exec "${CONTAINER_NAME}" test -f /tmp/setup_complete 2>/dev/null; then
    echo "ERROR: Container setup is not complete or was not successful."
    echo "This can happen if:"
    echo "  1. The container is still being set up (can take up to 10 minutes)"
    echo "  2. The initial setup failed"
    echo ""
    echo "You can:"
    echo "  - Wait a few minutes and try again"
    echo "  - Check container logs: docker logs ${CONTAINER_NAME}"
    echo "  - Remove and recreate: $0 $1 --cleanup && $0 $1"
    exit 1
fi

# Determine what tests to run
if [ -n "$TEST_FILE" ]; then
    echo "Searching for test file: $TEST_FILE"
    
    # Search for the test file in the container
    TEST_PATH=$(docker exec "${CONTAINER_NAME}" bash -c "
        find /usr/local/lib/python3.11/dist-packages/middlewared/pytest -name '$TEST_FILE' -type f 2>/dev/null | head -1
    ")
    
    if [ -z "$TEST_PATH" ]; then
        echo "ERROR: Test file '$TEST_FILE' not found in the pytest directory"
        echo "Available test files:"
        docker exec "${CONTAINER_NAME}" bash -c "
            find /usr/local/lib/python3.11/dist-packages/middlewared/pytest -name '*.py' -type f | grep -E 'test_.*\.py$' | sort
        "
        exit 1
    fi
    
    echo "Found test file at: $TEST_PATH"
    TEST_COMMAND="pytest-3 -v --disable-pytest-warnings $TEST_PATH"
else
    echo "Running all tests..."
    TEST_COMMAND="pytest-3 -v --disable-pytest-warnings /usr/local/lib/python3.11/dist-packages/middlewared/pytest"
fi

# Run the tests in the existing container
echo "Running unit tests in container '${CONTAINER_NAME}'..."
docker exec "${CONTAINER_NAME}" bash -c "
    set -e
    
    # Ensure pytest files are in the right place
    cp -a /workspace/middleware/src/middlewared/middlewared/pytest /usr/local/lib/python3.11/dist-packages/middlewared/ 2>/dev/null || true
    
    # Run the tests
    echo 'Executing: $TEST_COMMAND'
    $TEST_COMMAND
"

echo "Tests completed!"