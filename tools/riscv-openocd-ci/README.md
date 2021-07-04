# CI for riscv-openocd

This directory contains a set of scripts that automatically
run [riscv-tests/debug](https://github.com/riscv/riscv-tests/tree/master/debug)
against riscv-openocd.

The scripts are intended to be called automatically by Github
Actions as a means of testing & continuous integration for riscv-openocd.

The scripts perform these actions:

- Build OpenOCD from source
- Checkout and build Spike (RISC-V ISA simulator) from source
- Download a pre-built RISC-V toolchain
- Use these components together to run
  [riscv-tests/debug](https://github.com/riscv/riscv-tests/tree/master/debug)
- Process the test results
- Collect code coverage for OpenOCD

See [.github/workflows](../../.github/workflows) for an example of how this is
used in practice.
