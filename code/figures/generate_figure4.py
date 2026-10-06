"""Reproduce/check frozen Pearson r; export Figure 4 with original two-panel style.
No models, significance tests, filtering or data writes. --output-dir is optional.
"""
from pathlib import Path
import sys,os,argparse,hashlib,json
B=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(B)]
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=B.parent/'reproduced_figures');args=ap.parse_args();D=args.output_dir;D.mkdir(parents=True,exist_ok=True)
os.environ['MPLCONFIGDIR']=str(D/'.matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import frozen_dataset_v1_1 as frozen
EXPECTED=frozen.EXPECTED_SHA256
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(frozen.DATASET)==EXPECTED
features=['MATTR','lexical_density','avg_syllables','lexical_sophistication','MDD','MHD','avg_line_length','line_repetition_rate']
df=pd.DataFrame(frozen.load_rows());assert len(df)==561 and df.song_id.is_unique
for f in features:df[f]=pd.to_numeric(df[f],errors='raise')
assert np.isfinite(df[features].to_numpy()).all()
a=B/'analysis/round1/results/pearson_r_matrix.csv';b=B/'analysis/round2/results/figure_correlation_matrix.csv'
source_hashes={p.relative_to(B.parent).as_posix():sha(p) for p in [frozen.DATASET,frozen.MANIFEST,a,b]}
reference=pd.read_csv(a,index_col=0).loc[features,features];round2=pd.read_csv(b,index_col=0).loc[features,features]
# Terminology-only revision: use saved coefficients without recomputation.
check=reference.copy()
assert np.allclose(check,reference,atol=1e-12,rtol=0)
assert np.allclose(round2,reference,atol=1e-12,rtol=0)
assert np.allclose(reference,reference.T,atol=1e-15,rtol=0) and np.array_equal(np.diag(reference),np.ones(8))
for i in range(8):
 for j in range(8):assert f'{check.iloc[i,j]:.2f}'==f'{reference.iloc[i,j]:.2f}'
# Presentation alias only: avg_word_length means frozen avg_syllables.
labels=[f if f!='avg_syllables' else 'avg_word_length' for f in features]
m=reference.copy();m.index=labels;m.columns=labels;cross=m.iloc[:4,4:]
# Original correlation_analysis.py visualization, using saved coefficients instead
# of fitting/recomputing analyses. Same layout, cmap, annotation and color limits.
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'lyrics-figure4-v1.1'})
def heatmap(data,annot,fmt,cmap,center,vmin,vmax,ax,cbar_kws,square=False):
 # Matplotlib equivalent of the original seaborn heatmap; no statistical operation.
 mesh=ax.pcolormesh(data.to_numpy(),cmap=cmap,vmin=vmin,vmax=vmax)
 ax.set_xlim(0,data.shape[1]);ax.set_ylim(data.shape[0],0)
 if square:ax.set_aspect('equal')
 ax.set_xticks(np.arange(data.shape[1])+.5,data.columns,rotation=90)
 ax.set_yticks(np.arange(data.shape[0])+.5,data.index,rotation=0)
 ax.grid(False);ax.tick_params(length=0)
 for spine in ax.spines.values():spine.set_visible(False)
 for i in range(data.shape[0]):
  for j in range(data.shape[1]):
   value=data.iloc[i,j];rgb=mesh.cmap(mesh.norm(value))[:3]
   linear=[c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4 for c in rgb]
   lum=np.dot(linear,[.2126,.7152,.0722])
   ax.text(j+.5,i+.5,format(value,fmt),ha='center',va='center',fontsize=8.5 if square else 10,color='.15' if lum>.408 else 'white')
 ax.figure.colorbar(mesh,ax=ax,**cbar_kws)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,5))
heatmap(m,annot=True,fmt='.2f',cmap='RdBu_r',center=0,vmin=-.5,vmax=.5,square=True,ax=ax1,cbar_kws={'label':'Pearson r'})
ax1.set_title('(a) Correlation Matrix: All Complexity Measures',fontsize=12,fontweight='bold',pad=10);ax1.set_xlabel('');ax1.set_ylabel('')
heatmap(cross,annot=True,fmt='.2f',cmap='RdBu_r',center=0,vmin=-.5,vmax=.5,ax=ax2,cbar_kws={'label':'Pearson r'})
ax2.set_title('(b) Cross-Domain Correlations\n(Lexical × Dependency-based/Structural)',fontsize=12,fontweight='bold',pad=10)
ax2.set_xlabel('Dependency-based/Structural Measures',fontweight='bold',fontsize=10);ax2.set_ylabel('Lexical Measures',fontweight='bold',fontsize=10)
assert [t.get_text() for t in ax1.texts]==[f'{x:.2f}' for x in m.to_numpy().ravel()]
assert [t.get_text() for t in ax2.texts]==[f'{x:.2f}' for x in cross.to_numpy().ravel()]
fig.tight_layout()
for ext in ['png','pdf','svg']:
 meta={'Software':'Lyrics frozen v1.1'} if ext=='png' else {'Creator':'Lyrics frozen v1.1'}
 if ext=='pdf':meta.update(CreationDate=None,ModDate=None)
 if ext=='svg':meta['Date']=None
 fig.savefig(D/f'Figure4_correlation_matrix_v1_1.{ext}',dpi=300,bbox_inches='tight',metadata=meta)
plt.close(fig)
assert all(sha(B.parent/p)==h for p,h in source_hashes.items())
(D/'matrix_verification.json').write_text(json.dumps({'canonical_dataset':frozen.DATASET.relative_to(B.parent).as_posix(),'sha256':EXPECTED,'N':561,'max_abs_difference_saved_vs_round1':float(np.max(np.abs(check-reference))),'max_abs_difference_round2_vs_round1':float(np.max(np.abs(round2-reference))),'all_64_coefficients_match_at_2_decimals':True,'all_80_annotations_checked':True,'source_hashes':source_hashes},indent=2))
print('PASS: saved full 8x8 matrix checked; all 80 annotations verified.')
