"""Final Figure 5: approved Version 1 labeled centroids; never fit PCA."""
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
GENRES=['pop','rock','gospel','r&b','rap','country','reggae'];DISPLAY=['Pop','Rock','Gospel','R&B','Rap','Country','Reggae'];COLORS=['#0072B2','#B87900','#007D5A','#9C4D85','#C44900','#008B9A','#6B6338'];MARKERS=['o','s','^','v','P','X','h']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'lyrics-round2-v1','axes.titleweight':'semibold'})
# Read saved scores and centroids; changes below affect appearance only.
fig,ax=plt.subplots(figsize=(9.2,6.6))
for g,label,color,marker in zip(GENRES,DISPLAY,COLORS,MARKERS):
 t=s[s.genre==g];cent=c[c.genre==g].iloc[0]
 points=ax.scatter(t.PC1,t.PC2,s=27,alpha=.80,c=color,marker=marker,edgecolors='#262626',linewidths=.35,label=f'{label} (n={len(t)})')
 assert np.array_equal(points.get_offsets(),t[['PC1','PC2']].to_numpy())
 ax.scatter(cent.PC1,cent.PC2,s=130,c=color,marker='D',edgecolors='black',linewidths=.9,zorder=5)
ax.axhline(0,color='.75',lw=.7,zorder=0);ax.axvline(0,color='.75',lw=.7,zorder=0)
ax.set(xlabel=f"PC1 ({float(var[0]['variance_explained_percent']):.1f}%)",ylabel=f"PC2 ({float(var[1]['variance_explained_percent']):.1f}%)")
ax.set_aspect('equal',adjustable='datalim');ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False,title='Genre')
fig.text(.12,.015,'Diamonds indicate genre centroids.',fontsize=9)
fig.tight_layout(rect=(0,.04,1,1))
assert len(ax.collections)==14 and not ax.patches
# Match the reviewed Version 1 rendering, including fixed label offsets.
fig.canvas.draw()
legend=ax.get_legend()
for handle in legend.legend_handles:
 handle.set_alpha(1.)
legend.get_title().set_fontweight('semibold')
for centroid in ax.collections[1::2]:
 centroid.set_sizes([80]);centroid.set_linewidths([.65]);centroid.set_edgecolors('#262626')
OFFSETS=[(10,-70),(-65,42),(-75,-38),(65,-27),(55,0),(65,42),(-10,65)]
annotations=[]
for genre,label,color,offset in zip(GENRES,DISPLAY,COLORS,OFFSETS):
 row=c[c.genre==genre].iloc[0]
 annotations.append(ax.annotate(label,xy=(row.PC1,row.PC2),
  xytext=offset,textcoords='offset points',ha='center',va='center',
  fontsize=9,fontweight='medium',color='#202020',zorder=9,
  bbox=dict(boxstyle='round,pad=.22',facecolor='white',edgecolor=color,linewidth=.6,alpha=.96),
  arrowprops=dict(arrowstyle='-',color='#454545',lw=.65,
   shrinkA=3,shrinkB=5,connectionstyle='arc3,rad=0')))
fig.texts[0].set_text('Labeled markers indicate genre centroids.')
fig.canvas.draw()
renderer=fig.canvas.get_renderer()
boxes=[a.get_bbox_patch().get_window_extent(renderer).expanded(1.06,1.12) for a in annotations]
for i,box in enumerate(boxes):
 assert all(not box.overlaps(other) for other in boxes[i+1:]),'Centroid text labels overlap'
 assert ax.bbox.contains(box.x0,box.y0) and ax.bbox.contains(box.x1,box.y1)
for i,genre in enumerate(GENRES):
 t=s[s.genre==genre];cent=c[c.genre==genre].iloc[0]
 assert np.array_equal(ax.collections[2*i].get_offsets(),t[['PC1','PC2']].to_numpy())
 assert np.array_equal(ax.collections[2*i+1].get_offsets(),[[cent.PC1,cent.PC2]])
for ext in ['png','pdf','svg']:
 meta={'Software':'Lyrics frozen v1.1 centroid-label preview'} if ext=='png' else {'Creator':'Lyrics frozen v1.1 centroid-label preview'}
 if ext=='pdf':meta.update(CreationDate=None,ModDate=None)
 if ext=='svg':meta['Date']=None
 fig.savefig(D/f'Figure5_PCA_v1_1.{ext}',dpi=300,bbox_inches='tight',metadata=meta)
plt.close(fig)
