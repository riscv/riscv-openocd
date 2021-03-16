#!/bin/bash

# Toolchain builds provided by Embecosm (buildbot.embecosm.com)
# TOOLCHAIN_URL="https://buildbot.embecosm.com/job/riscv32-gcc-ubuntu1804"
# TOOLCHAIN_URL+="/25/artifact/riscv32-embecosm-gcc-ubuntu1804-20201108.tar.gz"
# TOOLCHAIN_PREFIX=riscv32-unknown-elf-

# Toolchain builds from "The xPack Project"
# (https://xpack.github.io/riscv-none-embed-gcc/)
TOOLCHAIN_URL="https://github.com/xpack-dev-tools/riscv-none-embed-gcc-xpack/"
TOOLCHAIN_URL+="releases/download/v10.1.0-1.1/"
TOOLCHAIN_URL+="xpack-riscv-none-embed-gcc-10.1.0-1.1-linux-x64.tar.gz"
TOOLCHAIN_PREFIX=riscv-none-embed-

ARCHIVE_NAME=${TOOLCHAIN_URL##*/}
DOWNLOAD_DIR=`pwd`/tools/riscv-openocd-ci/work
INSTALL_DIR=`pwd`/tools/riscv-openocd-ci/work/install

# Fail on first error.
set -e

# Echo commands.
set -o xtrace

# Download the toolchain.
# Use a pre-built toolchain binaries provided by Embecosm: https://buildbot.embecosm.com/
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"
wget --progress dot:mega "$TOOLCHAIN_URL"

# Extract
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
tar xvf "$DOWNLOAD_DIR/$ARCHIVE_NAME" --strip-components=1

cd "$INSTALL_DIR/bin"

# Make symlinks so that the tools are accessible as riscv64-unknown-elf-*
if [ "$TOOLCHAIN_PREFIX" != "riscv64-unknown-elf-" ]; then
    find . -name "$TOOLCHAIN_PREFIX*" | while read F; do
        ln -s $F $(echo $F | sed -e "s/$TOOLCHAIN_PREFIX/riscv64-unknown-elf-/");
    done
fi

# Check that the compiler and debugger can run, show versions
./riscv64-unknown-elf-gcc --version
./riscv64-unknown-elf-gdb --version

