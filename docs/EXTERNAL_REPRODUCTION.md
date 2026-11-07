# Independent reproduction: hand-off instructions

Status: **not yet performed by an independent external researcher**. This file is an execution protocol, not a certificate or endorsement. The separate standard-library checker was written and run by the same assistant that revised the manuscript.

1. Obtain the tested source commit from `publication.json` or the manuscript's code-availability section. Record the full 40-character identifier; do not assume the moving `main` branch is the tested commit.
2. On a separate machine, clone `https://github.com/giantfor/fpor-selection-audit` and check out that identifier. Use `git -c core.autocrlf=false clone ...`; the release also disables Git newline conversion.
3. Create a new Python 3.11 environment, without system site packages: `python -m venv .venv`. Activate it. Install `python -m pip install -r code/requirements-lock.txt`.
4. Run `python code/reproduce_release.py ../external_reproduction_report`. This checks the manifest before regeneration, runs the analysis and replay scripts, and compares the released numerical CSV/JSON hashes. The final output must say `REPRODUCTION True`. Keep all logs, including failures. Do not update expected hashes to conceal a mismatch.
5. Independently inspect Table 7 with `python code/verify_paired_independent.py`. It reconstructs all 81 configurations from integer event counts, verifies complete pairing, obtains the Student quantile without SciPy, and checks the printed table. This is not a separate simulation of committee generation.
6. Verify that the manuscript maps the equal-initialization obstruction and two-level exposure example to separate scenarios. Check the evolved-score 0.10 row includes zero. Examine the source assumptions rather than accepting numerical agreement as implementation equivalence.
7. Complete `EXTERNAL_REPRODUCTION_RECORD.json` with the actual operator, date, machine/OS, commit, commands, logs, deviations and conclusion. Supply the resulting report to the authors. Do not mark independence merely because a new environment or second program was used.

Expected numerical results include 4,000 stochastic trajectories, 1,080 score populations, 6,480 placement evaluations, 3,240 population pairs and 81 paired configurations. The replay checks cover 53,400 stochastic transitions and 1,400 empty-family terminations. Inspect the released reports for exact expected totals.

Platform limitation: the original release is tested on Windows/Python 3.11. Floating-point implementations and MILP tie choices may differ on another OS. A failed byte comparison is not automatically a mathematical error; preserve it, report the affected files, and investigate numerical/semantic differences. Do not describe a mismatching cross-platform run as a successful exact reproduction.

This protocol does not test an original FPoR implementation, networked PBFT, or a security-preserving recovery policy. Such evidence requires different experiments.
