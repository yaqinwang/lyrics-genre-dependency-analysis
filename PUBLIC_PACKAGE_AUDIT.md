# Final public-package audit

Status: PASS. The public derived dataset reproduces reported statistics and final figures. No push or publication was performed.

- All 561 rows and every retained value match the frozen original. The public hash is pinned in the loader and manifest.
- `code/reproduce.py` completed, covering descriptives, ANOVA/eta-squared, Bonferroni/Cohen's d, Welch/Games–Howell, Pearson/BH across 16 tests, HC3 M0/M1 and diagnostic interactions, primary-artist CR1, PCA, and final figures.
- All 35 statistical/reference CSV comparisons have zero numeric differences. An entirely null internal-review field was omitted from the cluster summary. All nine reported anchors exactly match frozen v1.1 outputs.
- Final figures 2–5 are byte-identical to rerenders. Initial staging Figure 4 used a superseded image; staging was corrected to the approved terminology revision. No statistical code changed to resolve it.
- Public file bytes and decompressed workbook members were scanned for local paths and internal review content. The upload allowlist contains derived features, publication inventory/tables, code, final figures and sanitized verification records; no raw or parsed lyrics, excluded model code/results, or obsolete-version results presented as current.
- The canonical dataset and research files are unchanged. A system Finder metadata difference outside staging is recorded locally.
- Upload only `PUBLIC_FILE_MANIFEST.json`'s allowlist. Local-only audit, protected snapshot, private provenance, `LOCAL_` files, caches, diagnostics and temporary rerenders are git-ignored.

Detailed comparisons are in `REPRODUCTION_VERIFICATION.json`; column removals are in `data/dataset_manifest.json`. Public provenance paths are repository-relative. Citation details and the authors' choice of release license remain to be supplied; no license was inferred. A new pip installation was not tested. Raw feature extraction was not rerun and this package does not reconstruct the copyrighted lyric corpus.
