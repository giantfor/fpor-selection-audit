# Editorial audit, 7 November 2026

## Graphical abstract

The visual uses two separate panels with no connector between the scenarios. Panel A identifies equal initialization, full membership exclusion, and global reputation thresholds. Panel B explicitly says “Separate audit scenario” and labels its two-level reputation population, n=16, k=4 and four high-score adversaries. The obstruction is conditional; composition exposure is not attack success.

The files are original deterministic vector artwork made with Matplotlib. PDF/SVG retain vectors; PNG/TIFF are 4500 × 1800 pixels at 300 dpi (2.5:1). Arial is used. PDF and TIFF are supplied separately for submission. The embedded graphical-abstract page is for the review copy; it is not a statement that every final journal PDF must contain it.

Checked against Elsevier's general guidance:
https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract

The guidance calls for a separate file, at least 1328 × 531 pixels at 300 dpi, a wide layout, readable text, and preferred PDF/TIFF/EPS/MS Office formats. The journal-specific ICT Express guide returned HTTP 403 during this check:
https://www.sciencedirect.com/journal/ict-express/publish/guide-for-authors

Therefore full compliance with current journal-specific length, article-type and submission requirements is **not verified**. Do not describe this manuscript as submission-certified. The graphical abstract does not use a generated raster image or third-party illustration.

## References and author information

The 56 cited references are retained; the 89-source catalog remains in the artifact. `code/audit_bibliography.py` checks citation coverage, author/title/year fields, source identifiers and duplicate DOIs. Its report has no structural metadata issues. This is not a fresh publisher-by-publisher full-text or Scopus audit. The compiled BibTeX log should be checked for missing-field warnings.

Author order: Djarot Hindarto; Eko Mulyanto Yuniarno; Sari Ningsih. Corresponding author and affiliations follow the information supplied by the user. Funding, competing interests and contributions retain the confirmed declarations. No author signature or final coauthor approval is fabricated.

## Statistics and evidence

Table 7 prints five decimal places to expose the negative lower endpoint for evolved scores at adversarial fraction 0.10. This display choice does not increase statistical precision. Intervals are approximate pointwise Student intervals, not simultaneous guarantees. No claim that every scenario has a positive or practically important effect is made. Coverage for sparse near-zero event proportions has not been calibrated.

The standard-library cross-check is a separate numerical implementation, not an external independent reviewer. The hand-off record remains explicitly unfilled. Original FPoR prototype equivalence, operational PBFT security and recovery safety remain unverified.
