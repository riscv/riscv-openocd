
from glob import glob
import logging
from logging import info, error
import os
import re
import shutil
import sys

KNOWN_RESULTS = ["pass", "fail", "not_applicable", "exception"]


def info_box(msg):
    """Display an emphasized message - print an ASCII box around it. """
    box = " +==" + ("=" * len(msg)) + "==+"
    info("")
    info(box)
    info(" |  " + msg + "  |")
    info(box)
    info("")


def parse_args():
    """Process command-line arguments. """
    import argparse
    parser = argparse.ArgumentParser("Process logs from riscv-tests/debug")
    parser.add_argument("--log-dir", required=True, help="Directory where logs from RISC-V debug tests are stored")
    parser.add_argument("--output-dir", required=True, help="Directory where put post-processed logs")
    return parser.parse_args()


def process_test_logs(log_dir, output_dir):
    """Process all logs from the testing. """

    assert os.path.isdir(log_dir)
    os.makedirs(output_dir, exist_ok=True)

    # process log files
    file_pattern = os.path.join(log_dir, "*.log")
    log_files = sorted(glob(file_pattern))

    if not len(log_files):
        # Did not find any *.log.
        # Either the tests did not start at all or a wrong log directory was specified.
        raise RuntimeError("No log files (*.log) in directory {}".format(log_dir))

    tests = []
    for lf in log_files:
        target, result = process_one_log(lf)
        copy_one_log(lf, result, output_dir)
        tests += [{"log": lf, "target": target, "result": result}]

    return tests


def process_one_log(log_file):
    """Parse a single log file, extract required pieces from it. """
    assert os.path.isfile(log_file)
    target = None
    result = None
    # Find target name and the test result in the log file
    for line in open(log_file, "r"):
        target_match = re.match(r"^Target: (\S+)$", line)
        if target_match is not None:
            target = target_match.group(1)
        result_match = re.match(r"^Result: (\S+)$", line)
        if result_match is not None:
            result = result_match.group(1)
            if result not in KNOWN_RESULTS:
                msg = ("Unknown test result '{}' in file {}. Expected one of: {}"
                       .format(result, log_file, KNOWN_RESULTS))
                raise RuntimeError(msg)

    if target is None:
        raise RuntimeError("Could not find target name in log file {}".format(log_file))
    if result is None:
        raise RuntimeError("Could not find test result in log file {}".format(log_file))

    return target, result


def copy_one_log(log_file, result, output_dir):
    """Copy the log to a sub-folder based on the result. """
    target_dir = os.path.join(output_dir, result)
    os.makedirs(target_dir, exist_ok=True)
    assert os.path.isdir(target_dir)
    shutil.copy2(log_file, target_dir)


def print_aggregated_results(tests):
    """Print the tests grouped by the result. Print also pass/fail/... counts."""

    def _filter_tests(tests, target=None, result=None):
        tests_out = tests
        if target is not None:
            tests_out = filter(lambda t: t["target"] == target, tests_out)
        if result is not None:
            tests_out = filter(lambda t: t["result"] == result, tests_out)
        return list(tests_out)

    # Print lists of passed/failed/... tests
    outcomes = {
        "Passed tests": "pass",
        "Not applicable tests": "not_applicable",
        "Failed tests": "fail",
        "Tests ended with exception": "exception",
    }
    for caption, result in outcomes.items():
        info_box(caption)
        tests_filtered = _filter_tests(tests, result=result)
        for t in tests_filtered:
            name = os.path.splitext(os.path.basename(t["log"]))[0]
            info(name)
        if not tests_filtered:
            info("(none)")

    target_names = sorted(set([t["target"] for t in tests]))

    # Print summary - passed/failed/... counts, for each target and total

    info_box("Summary")

    def _print_row(target, total, num_pass, num_na, num_fail, num_exc):
        info("{:<25} {:<10} {:<10} {:<10} {:<10} {:<10}".format(target, total, num_pass, num_na, num_fail, num_exc))

    _print_row("Target", "# tests", "Pass", "Not_appl.", "Fail", "Exception")
    _print_row("-----", "-----", "-----", "-----", "-----", "-----")
    sum_pass = sum_na = sum_fail = sum_exc = 0
    for tn in target_names:
        t_pass = len(_filter_tests(tests, target=tn, result="pass"))
        t_na = len(_filter_tests(tests, target=tn, result="not_applicable"))
        t_fail = len(_filter_tests(tests, target=tn, result="fail"))
        t_exc = len(_filter_tests(tests, target=tn, result="exception"))
        t_sum = len(_filter_tests(tests, target=tn))
        assert t_sum == t_pass + t_na + t_fail + t_exc  # self-check
        _print_row(tn, t_sum, t_pass, t_na, t_fail, t_exc)
        sum_pass += t_pass
        sum_na += t_na
        sum_fail += t_fail
        sum_exc += t_exc
    assert len(tests) == sum_pass + sum_na + sum_fail + sum_exc  # self-check
    _print_row("-----", "-----", "-----", "-----", "-----", "-----")
    _print_row("All targets:", len(tests), sum_pass, sum_na, sum_fail, sum_exc)
    _print_row("-----", "-----", "-----", "-----", "-----", "-----")

    any_failed = (sum_fail + sum_exc) > 0
    return any_failed


def main():
    args = parse_args()

    # Use absolute paths.
    args.log_dir = os.path.abspath(args.log_dir)
    args.output_dir = os.path.abspath(args.output_dir)

    # Process the log files and print results.
    tests = process_test_logs(args.log_dir, args.output_dir)
    any_failed = print_aggregated_results(tests)

    # The overall exit code.
    exit_code = 1 if any_failed else 0
    if any_failed:
        error("Encountered failed test(s). Exiting with non-zero code.")
    else:
        info("Success - no failed tests encountered.")
    return exit_code


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
