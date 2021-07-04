#!/bin/bash

CHECKOUT_DIR=`pwd`/tools/riscv-openocd-ci/work/riscv-tests

# Fail on first error.
set -e

# Echo commands.
set -o xtrace

# Checkout riscv-tests.
mkdir -p "$CHECKOUT_DIR"
cd "$CHECKOUT_DIR"
git clone --depth=1 --recursive https://github.com/riscv/riscv-tests .

# Show revision info
git --no-pager log --no-walk --pretty=short

# Run the debug tests.
# Do not stop even on a failed test.
# Use slightly more jobs than CPUs. Observed that this still speeds up the testing.
cd debug
JOBS=$(($(nproc) + 2))

# Temporary: Run the testing 10 times to have higher chance of catching intermittent failures
for i in {1..5}; do
	make -k -j$JOBS all || true
done
