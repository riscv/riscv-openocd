#!/bin/bash

CHECKOUT_DIR=`pwd`/tools/riscv-openocd-ci/work/riscv-isa-sim
INSTALL_DIR=`pwd`/tools/riscv-openocd-ci/work/install

# Fail on first error.
set -e

# Echo commands.
set -o xtrace

# Checkout Spike.
mkdir -p "$CHECKOUT_DIR"
cd "$CHECKOUT_DIR"
git clone --depth=1 --recursive https://github.com/riscv/riscv-isa-sim.git .

# Show revision info
git --no-pager log --no-walk --pretty=short

# Build Spike
mkdir build
cd build
bash ../configure --prefix=$INSTALL_DIR
make clean  # safety
make -j`nproc`
make install

# Check that Spike runs
$INSTALL_DIR/bin/spike --help
