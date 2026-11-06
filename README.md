# FPoR selection audit — Version 3 research artifact

Author: Djarot Hindarto, Informatika, Fakultas Teknologi Komunikasi dan Informatika, Universitas Nasional.

This artifact studies compatibility of committee-selection rules under explicitly stated interpretations of FPoR. It is **not the original authors' prototype**, a full PBFT implementation, or evidence of a permanent deployed-protocol liveness failure. Code and writing were prepared with generative-AI assistance and require human scientific review.

## Reproduce

Tested environment: Python 3.11.5, NumPy 1.26.4, SciPy 1.16.2 (bundled HiGHS), Matplotlib 3.10.6. Solver tie choices can change with solver versions. Run from the repository root:

```sh
python -m pip install -r code/requirements.txt
python code/run_analysis.py
python code/extended_analysis.py
python code/verify_artifacts.py
python code/probabilistic_analysis.py
python code/verify_probabilistic.py
python code/render_probabilistic_results.py
```

The analyses create their output directories automatically. No credentials or external datasets are required. For a faster audit of the checked-in traces, run only the two `verify_*.py` scripts. Scripts exit nonzero if an assertion fails. Run Python normally, without `-O`, so assertions remain enabled.

## Experiment families

| Family | Design | Interpretation |
|---|---|---|
| Exact baseline | n=16, four selection laws, k=4/6/8 | Exhaustive subset composition and equality |
| Grouped enumeration | 60 configurations, n up to 256, coordinate correlation -1/0/1 | Exact combinatorial masses in floating-point arithmetic |
| Solver trajectories | 200 runs, 20-round horizon, four policies | Witness generation; counts are not deployment probabilities |
| Probabilistic trajectories | 4,000 runs, 200 per configuration | Explicit conditional-uniform sampler, pointwise Wilson intervals |
| Score sensitivity | 216 independent populations, 500 accepted samples each | Continuous, lognormal, and reward/penalty-evolved scores; k=log2(n), n/8, n/4 |
| Adversarial placements | Requested fractions .10/.25/.40, high-weight or random identities | 1,296 population-level evaluations; composition, not attack success |
| Quorum witness | Two conflicting 3-of-4 signer sets above the fault bound | Certificate abstraction only; no PBFT message execution |

## Sampler and uncertainty

Uniform independent priorities generate a uniform subset of eligible identities. Rejection conditions this law on the two global-average thresholds. After 4,096 unsuccessful proposals, a grouped exact sampler enumerates at most 100,000 type-count vectors when practical, with multiplicities `product(comb(group_size, selected_count))`. This preserves the same law. The MILP solver never substitutes its committee for a stochastic draw. Remaining sampling exhaustion is censored and is not classified as infeasibility merely because sampling failed. The saved run used the exact fallback 149 times and had no sampling-censored trajectories.

Each stochastic run is initialized from NumPy `SeedSequence([20261106,n,initialization_id,policy_id,replicate])`; every sequence is saved. A uniform proposer is selected separately. The primary estimand is empty-family termination within 20 successful rounds under this audit model. Wilson intervals are pointwise and approximate, not simultaneous guarantees. Zero observations do not establish zero risk.

Sensitivity population seeds are `SeedSequence([73219,n,k,distribution_id,replicate])`. Random-score coordinates are independent. Evolved scores come from 200 exogenous cycles with uniform committees, positive rewards, and a declared synthetic penalty mechanism; they are not FPoR execution histories. Adversarial placement for snapshot evaluation is separate from identities used to generate penalties. Full population arrays are saved. Replicates, sample counts, and censoring are in `results/probabilistic_verification.json`.

Per-population composition estimates have Wilson intervals. Aggregate intervals use eight independent population estimates and a Student-t approximation. Committees reused across placements are paired, not independent. Empirical Jain and proportionality values are labeled plug-in diagnostics, not unbiased estimates. The independent fixed acceptance batch has 2,048 proposals.

## Solver and test oracles

`extended_analysis.solve` uses binary variables with a fixed committee size, eligibility bounds, and two score-sum constraints. SciPy `milp` settings are `time_limit=10` seconds and `mip_rel_gap=0`. Status 2 is infeasible, 0 is an optimum, other statuses are unresolved. All returned solutions are checked against the inequalities at 1e-6 tolerance. Deterministic empty-family scalar checks use 1e-8 tolerance. No network timing is simulated.

Independent checks include individual-subset enumeration versus grouped formulas, small-state enumeration versus MILP, a uniform-sampler distributional smoke test, grouped-sampler marginal comparisons, and replay of every saved stochastic committee. Replay validates 53,400 successful transitions and 1,400 empty-family terminations. The earlier witness traces have an additional 3,335 checked transitions.

## Files and boundaries

- `code/`: scripts and pinned dependencies.
- `results/`: CSV/JSON outputs, trajectory identities, score arrays, and verification reports.
- `figures/`: generated vector figures.
- `docs/`: primary-specification mapping and response to the six review issues.
- `SHA256SUMS.json`: SHA-256 hashes for the released files.

The original FPoR source is Zhang and Huang, ICT Express 9(1), 45–50 (2023), DOI [10.1016/j.icte.2022.11.007](https://doi.org/10.1016/j.icte.2022.11.007). PBFT is a distinct protocol; see [Castro and Liskov, OSDI 1999](https://www.usenix.org/conference/osdi-99/presentation/practical-byzantine-fault-tolerance). Publisher PDFs and private review attachments are not redistributed here.

Public availability and a pinned commit support auditability; they do not by themselves establish correctness, novelty, security, or journal acceptance. No archival DOI has been minted. License terms for third-party dependencies remain their own; a separate license for this research code has not yet been assigned by the author.
