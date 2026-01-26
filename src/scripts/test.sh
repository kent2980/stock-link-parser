#!/bin/bash

# 引数を受け取る
# 引数がない場合は、デフォルト値を設定
if [ $# -eq 0 ]; then
    echo "No arguments supplied. Using default values."
    # デフォルト値
    TEST_PATH=""
else
    TEST_PATH=tests/$1/
fi

# Step 1: Run ruff linting
echo "Running ruff linting..."
uv run ruff check . --exit-zero

# Step 2: Run ruff formatting check
echo "Running ruff formatting check..."
uv run ruff format --check . || true

# Step 3: Run pytest with coverage using uv
echo "Running tests with coverage..."
uv run coverage run -m pytest $TEST_PATH

# Step 4: Generate HTML coverage report using uv
echo "Generating HTML coverage report..."
uv run coverage html

# Step 5: Report the coverage summary using uv
echo "Coverage summary:"
uv run coverage report -m

# Step 6: Open the HTML report in the default web browser
# The report is generated in the 'htmlcov' directory
# if [ -f htmlcov/index.html ]; then
    # open htmlcov/index.html  # macOS
    # xdg-open htmlcov/index.html  # Linux
    # start htmlcov/index.html  # Windows
# else
    # echo "Coverage report not found."
# fi
