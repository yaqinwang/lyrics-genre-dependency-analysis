"""Figure 5 note-only revision; export saved scores and centroids, never fit PCA."""
from pathlib import Path
import sys,os,csv,json,hashlib,shutil,copy,posixpath,subprocess
from zipfile import ZipFile
B=Path(__file__).resolve().parents[1];R=B/'analysis/round2';D=B.parent/'reproduced_figures';D.mkdir(exist_ok=True)
sys.path.insert(0,str(B))
os.environ['MPLCONFIGDIR']=str(D/'.matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import frozen_dataset_v1_1 as frozen
rows=frozen.load_rows();assert len(rows)==561
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
load=list(csv.DictReader((R/'results/pca_loadings.csv').open()));var=list(csv.DictReader((R/'results/pca_variance.csv').open()))
labels=['MATTR','Lexical density','Average word length','Lexical sophistication','MDD','MHD','Average line length','Line repetition rate']
expected=[[.262080,.434049],[.106377,.698145],[.047105,.814753],[.382689,.578379],[.776273,-.320329],[.830146,-.063107],[.922274,-.256941],[-.573099,-.157532]]
s=pd.read_csv(R/'results/pca_song_scores.csv');c=pd.read_csv(R/'results/pca_genre_centroids.csv');assert len(s)==561 and len(c)==7
assert set(s.song_id)=={r['song_id'] for r in rows}
GENRES=['pop','rock','gospel','r&b','rap','country','reggae'];DISPLAY=['Pop','Rock','Gospel','R&B','Rap','Country','Reggae'];COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00','#56B4E9','#6B6338']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'lyrics-round2-v1','axes.titleweight':'semibold'})
# The approved 01_pca.py scatter/centroid plotting procedure, reading frozen scores.
fig,ax=plt.subplots(figsize=(9.2,6.6))
for g,label,color in zip(GENRES,DISPLAY,COLORS):
 t=s[s.genre==g];cent=c[c.genre==g].iloc[0]
 points=ax.scatter(t.PC1,t.PC2,s=19,alpha=.48,c=color,edgecolors='none',label=f'{label} (n={len(t)})')
 assert np.array_equal(points.get_offsets(),t[['PC1','PC2']].to_numpy())
 ax.scatter(cent.PC1,cent.PC2,s=130,c=color,marker='D',edgecolors='black',linewidths=.9,zorder=5)
ax.axhline(0,color='.75',lw=.7,zorder=0);ax.axvline(0,color='.75',lw=.7,zorder=0)
ax.set(xlabel=f"PC1 ({float(var[0]['variance_explained_percent']):.1f}%)",ylabel=f"PC2 ({float(var[1]['variance_explained_percent']):.1f}%)")
ax.set_aspect('equal',adjustable='datalim');ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False,title='Genre')
fig.text(.12,.015,'Diamonds indicate genre centroids.',fontsize=9)
fig.tight_layout(rect=(0,.04,1,1))
assert len(ax.collections)==14 and not ax.patches
for ext in ['png','pdf','svg']:
 meta={'Software':'Lyrics frozen v1.1'} if ext=='png' else {'Creator':'Lyrics frozen v1.1'}
 if ext=='pdf':meta.update(CreationDate=None,ModDate=None)
 if ext=='svg':meta['Date']=None
 fig.savefig(D/f'Figure5_PCA_v1_1.{ext}',dpi=300,bbox_inches='tight',metadata=meta)
plt.close(fig)
