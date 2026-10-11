# Song lyrics: reproducibility package

This repository supports a quantitative study of lexical, dependency-based, and structural variation across 561 English song lyrics in seven Grammy-based genres: Pop (79), Rock (79), Gospel (79), R&B (85), Rap (80), Country (80), and Reggae (79).

Fresh verification passed: every reported numerical anchor matches frozen v1.1 exactly, all 35 statistical/reference CSV comparisons have zero numeric differences, and all four final PNGs are byte-identical to fresh rerenders.

## Contents

- `data/`: `final_analysis_dataset_public.csv`, the public derived dataset for reproducing the reported analyses; publication-facing song inventory and dataset integrity manifest.
- `code/analysis/round1/`: approved descriptives, one-way ANOVA/eta-squared, Bonferroni pairwise tests/pooled-SD Cohen's d, Welch/Games–Howell, Pearson/BH (16 cross-domain tests), HC3 M0/M1 and interaction models, and primary-artist CR1 models. `common.py` provides the exact shared statistical functions.
- `code/analysis/round2/`: approved standardized PCA; selected approved output CSVs provide plot reference checks. Running analyses regenerates their outputs in the corresponding `results/` directories.
- `code/features/`: unchanged frozen feature-function provenance and parser settings; these are not corpus-build entry points.
- `code/figures/`: portable copies of final manuscript plot procedures.
- `supplementary/`: [S1 Excel workbook](supplementary/Supplementary_Table_S1.xlsx) and approved v1.1 RC2 [S2 Excel workbook](supplementary/Supplementary_Table_S2.xlsx). S2 retains all four panels; Panel D uses Bonferroni-compatible simultaneous 95% confidence intervals, while Panel B retains pointwise 95% intervals.
- `figures/`: approved current PNG figures 2–5. Generated figures go to `reproduced_figures/`.
- `REPRODUCTION_VERIFICATION.json` and `anchor_verification.json`: fresh execution checks and exact comparisons against frozen v1.1 values.
- `PUBLIC_PROVENANCE.json`, `PUBLIC_FILE_MANIFEST.json`, `PUBLIC_SAFETY_CHECK.json`, and `PUBLIC_PACKAGE_AUDIT.md`: public provenance, upload allowlist, and final safety audit, using repository-relative file paths.

## Data availability and integrity

Raw lyric texts and parsed full lyric texts are not redistributed because of copyright restrictions. The package supplies the publication corpus inventory; all eight derived song-level measures reside in `final_analysis_dataset_public.csv`, projected from the canonical frozen v1.1 dataset. This package does not reconstruct the copyrighted corpus.

Canonical original frozen v1.1 dataset SHA-256: `7b1bf2f3df4a90b64af5cfa31c01944762c14fcf434fbf00218367c4b9db1f26`.

Public dataset SHA-256: `8bd4009cd2c2f6136e2b99ebb21cd496399b9b899a553f2acec0b78aeba9f963`.

The public dataset removes only 11 internal provenance/review columns, including raw-file checksums. It preserves all 561 rows in their original order and every retained cell value, including song IDs, titles, genre, artist fields, token count, and all eight measures. The exact removed columns are recorded in `data/dataset_manifest.json`. The canonical original is unchanged. The two hashes identify different files; the staging loader verifies the public dataset against its own pinned hash and manifest before every analysis.

## Software environment

Final execution manifests establish Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, SciPy 1.16.2, statsmodels 0.14.5, scikit-learn 1.7.2, matplotlib 3.10.6 and patsy 1.0.1. Final vendor metadata establishes joblib 1.5.2 and threadpoolctl 3.6.0. Frozen feature-build provenance establishes pronouncing 0.2.0, cmudict 1.1.1, Stanford CoreNLP 4.5.9 and Java 21.0.6. Python requirements are pinned only where local evidence establishes a version; parser/Java are needed only for separately held text processing.

## Reproduce analyses and figures

Run from this repository root:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -B code/reproduce.py
```

The runner executes Round 1 scripts 01–05 in order, then Round 2 PCA, final plot procedures for figures 2–5, and manuscript anchor checks. It uses only repository paths. Packaging verification used Python 3.12.14 and existing read-only dependency libraries at the evidenced versions; a new pip installation was not tested. Statistical outputs retain the approved algorithms; source scripts are preserved outside this package. S1 is supplied as a publication table; S2 is supplied as the approved RC2 presentation table. Its HC3 models and adjusted artist-clustered models correspond to Round 1 scripts 04 and 05; Panel A also includes the verified supplementary genre-only artist-clustered results for all eight measures. These supplementary results and the simultaneous intervals were verified separately before publication; this release update does not rerun or alter statistical outputs. Exact original orchestration/reviewer scripts depending on private manuscript files are excluded.

## Feature extraction

`final_lexical_metrics.py` implements the approved retained-token syllable floor and imports unchanged `lexical_metrics.py`, which supplies MATTR (window 50), lexical density, CMU-first syllable counting with heuristic fallback, and lexical sophistication (outside the first 5,000 COCA rows). Use the final wrapper for average word length; the older helper's standalone averaging function predates the approved floor. `syntactic_metrics.py` supplies song-level MDD and MHD from sentence-level dependency measures, average line length, and repetition rate. The frozen build records authenticate all three modules by hash. `parser.properties` records the CoreNLP settings. Raw preprocessing, parser output conversion, and archival candidate builds are deliberately not executed or included as runnable release steps.

The external COCA reference list came from [COCA-WordFrequency](https://github.com/brucewlee/COCA-WordFrequency). Obtain it independently and verify SHA-256 `2040bed6fed190942f0b3d4fb96877d4a9837a7ece8172da51c24920c52a71d8`. The third-party CSV is not redistributed; redistribution permission has not been established. Feature functions require independently held, correctly preprocessed CoNLL inputs. They were not rerun during packaging.

## AI-assisted workflow

Generative AI assisted coding and debugging, data-processing workflows, statistical checking, and language editing. Final code and outputs were executed and verified by the authors. Fresh public-data reproduction checks are recorded in this repository.

## Citation

Paper citation: forthcoming / manuscript under revision.

## Public upload scope

Only files listed in `PUBLIC_FILE_MANIFEST.json` are intended for public upload. The local audit, protected snapshot, private provenance report and files prefixed `LOCAL_` are explicitly git-ignored. Temporary rerenders, diagnostics, caches and system metadata are also ignored. `PUBLIC_PROVENANCE.json` contains repository-relative paths only. An entirely null historical review flag was omitted from the public artist-cluster summary, with all analytical values preserved.

The original Figure 4 staging PNG was superseded; it was corrected to the approved Dependency-based/Structural terminology revision. Figures 2–5 now reproduce byte-for-byte. Citation details and the authors' choice of release license remain to be supplied; no license was inferred.
