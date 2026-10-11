# Supplementary Table S2. Robustness analyses of genre-related variation under artist clustering and line-length adjustment

## Panel A. Genre-only effects across eight measures

| Measure | ANOVA F | ANOVA p | CR1 F | CR1 p |
| --- | --- | --- | --- | --- |
| MATTR | 16.397 | < .001 | 14.964 | < .001 |
| Lexical density | 4.316 | < .001 | 4.028 | < .001 |
| Average syllables per word | 5.081 | < .001 | 4.341 | < .001 |
| Lexical sophistication | 18.754 | < .001 | 13.424 | < .001 |
| MDD | 11.641 | < .001 | 12.884 | < .001 |
| MHD | 15.709 | < .001 | 9.591 | < .001 |
| Average line length | 20.274 | < .001 | 11.925 | < .001 |
| Line repetition rate | 12.426 | < .001 | 13.352 | < .001 |

## Panel B. Genre models before and after line-length adjustment

| Outcome | Model | Estimator | R² | Genre F | df | Genre p | Line-length β | 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MDD | M0 | HC3 | 0.112 | 15.123 | (6, 554) | < .001 | — | — |
| MDD | M0 | CR1 | 0.112 | 12.884 | (6, 230) | < .001 | — | — |
| MDD | M1 | HC3 | 0.646 | 3.081 | (6, 553) | .0056 | 0.104 | [0.083, 0.124] |
| MDD | M1 | CR1 | 0.646 | 3.494 | (6, 230) | .0025 | 0.104 | [0.086, 0.122] |
| MHD | M0 | HC3 | 0.145 | 16.870 | (6, 554) | < .001 | — | — |
| MHD | M0 | CR1 | 0.145 | 9.591 | (6, 230) | < .001 | — | — |
| MHD | M1 | HC3 | 0.629 | 3.690 | (6, 553) | .0013 | 0.073 | [0.063, 0.083] |
| MHD | M1 | CR1 | 0.629 | 3.920 | (6, 230) | < .001 | 0.073 | [0.064, 0.082] |

## Panel C. Diagnostic genre × line-length interactions

| Outcome | HC3 interaction F | df | p | R² |
| --- | --- | --- | --- | --- |
| MDD | 3.702 | (6, 547) | .0013 | 0.676 |
| MHD | 0.646 | (6, 547) | .6937 | 0.640 |

## Panel D. Adjusted Rap contrasts from M1

| Outcome | Contrast | Difference | HC3 Bonferroni simultaneous 95% CI | HC3 p Bonf. | CR1 Bonferroni simultaneous 95% CI | CR1 p Bonf. |
| --- | --- | --- | --- | --- | --- | --- |
| MDD | Rap − Pop | -0.091 | [-0.1826, 0.0010] | .0541 | [-0.1770, -0.0046] | .0329 |
| MDD | Rap − Rock | -0.024 | [-0.1340, 0.0862] | 1.0000 | [-0.1210, 0.0732] | 1.0000 |
| MDD | Rap − Gospel | -0.008 | [-0.0958, 0.0805] | 1.0000 | [-0.0856, 0.0703] | 1.0000 |
| MDD | Rap − R&B | -0.065 | [-0.1696, 0.0393] | .5959 | [-0.1681, 0.0378] | .5619 |
| MDD | Rap − Country | -0.033 | [-0.1137, 0.0480] | 1.0000 | [-0.1069, 0.0412] | 1.0000 |
| MDD | Rap − Reggae | -0.004 | [-0.1281, 0.1195] | 1.0000 | [-0.0932, 0.0845] | 1.0000 |
| MHD | Rap − Pop | 0.070 | [0.0126, 0.1270] | .0078 | [0.0163, 0.1234] | .0037 |
| MHD | Rap − Rock | 0.026 | [-0.0469, 0.0991] | 1.0000 | [-0.0418, 0.0940] | 1.0000 |
| MHD | Rap − Gospel | 0.036 | [-0.0249, 0.0973] | .7055 | [-0.0180, 0.0903] | .4612 |
| MHD | Rap − R&B | 0.038 | [-0.0202, 0.0966] | .5016 | [-0.0217, 0.0981] | .5440 |
| MHD | Rap − Country | 0.037 | [-0.0233, 0.0983] | .6177 | [-0.0258, 0.1008] | .6964 |
| MHD | Rap − Reggae | -0.010 | [-0.0799, 0.0596] | 1.0000 | [-0.0744, 0.0540] | 1.0000 |

Note. N = 561 songs; G = 231 primary-artist clusters. Panel A: classical ANOVA df = (6, 554); CR1 df = (6, 230).

M0 includes genre only. M1 adds average line length centered at its sample mean (8.175 tokens per line). HC3 denotes heteroskedasticity-consistent covariance; t/F inference uses residual degrees of freedom. CR1 denotes primary-artist-clustered covariance with correction G/(G−1) × (N−1)/(N−k), where k is the number of fitted coefficients; t/F inference uses G−1 degrees of freedom. R² depends on the OLS fit and is identical across covariance estimators for the same model.

MDD = mean dependency distance; MHD = mean hierarchical distance; MATTR = moving-average type–token ratio.

In Panel D, differences are Rap minus the comparison genre; confidence intervals are Bonferroni-compatible simultaneous intervals with familywise coverage of at least 95% across six Rap contrasts separately for each outcome and estimator. Each interval is estimate ± t(1−.05/(2×6), df) × SE (HC3 df = 553; CR1 df = 230). The p-values retain the original Bonferroni adjustment across the same six contrasts. Panel B retains pointwise 95% confidence intervals.

Panel C models are diagnostic and do not replace M1. Omnibus genre significance does not imply significance of every individual contrast. Artist clustering adjusts inference for within-artist dependence; it does not control artist-specific, year, or songwriter-level confounding. No additional correction across omnibus tests was applied; alpha = .05. Dashes indicate predictors absent from M0.
