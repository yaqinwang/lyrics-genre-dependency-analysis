"""Run approved analyses and final plot procedures from the repository."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
from frozen_dataset_v1_1 import verified_path
verified_path()
for stage in ['analysis/round1/01_descriptives.py','analysis/round1/02_anova_posthoc.py','analysis/round1/03_correlations.py','analysis/round1/04_line_length_robustness.py','analysis/round1/05_artist_cluster_robustness.py','analysis/round1/06_verify_s2_panels.py','analysis/round2/01_pca.py','figures/generate_figures2_3.py','figures/generate_figure4.py','figures/generate_figure5.py','verify_anchors.py']:
 subprocess.run([sys.executable,'-B',str(ROOT/stage)],check=True,cwd=ROOT.parent)
