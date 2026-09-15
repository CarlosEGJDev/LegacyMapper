"""CLI package: argument parsing, command routing and the execution/result model.

Introduced in V4.2-R1 to keep parsing, routing and the analysis implementation
in separate modules (see docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md).
`legacy_documenter/main.py` remains the process entry point and still owns the
analysis implementation itself; this package only decides how the command line
is spelled and which existing capability a command routes to.
"""
