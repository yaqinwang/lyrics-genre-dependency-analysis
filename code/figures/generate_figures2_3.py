# Focused reproduction of the approved Figure 2 plotting code.
# Reads the verified frozen v1.1 dataset; writes only ./regenerated/.
"""Round 2 uses the frozen v1.1 input and no historical analysis data."""
from pathlib import Path
import sys,os,json,hashlib,platform
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1]/'analysis/round2';ROUND1=BASE.parent/'round1'
sys.path[:0]=[str(BASE/'vendor'),str(ROUND1/'vendor'),str(BASE.parent.parent)]
OUTPUT=Path(__file__).resolve().parents[2]/'reproduced_figures'
OUTPUT.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR']=str(OUTPUT/'.matplotlib')
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import patsy
import frozen_dataset_v1_1 as frozen_dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
GENRES=['pop','rock','gospel','r&b','rap','country','reggae']
DISPLAY=['Pop','Rock','Gospel','R&B','Rap','Country','Reggae']
COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00','#56B4E9','#6B6338']
MEASURES=['MATTR','lexical_density','avg_syllables','lexical_sophistication','MDD','MHD','avg_line_length','line_repetition_rate']
LABELS=['MATTR','Lexical density','Average syllables','Lexical sophistication (%)','MDD','MHD','Average line length','Line repetition (%)']
RESULTS=OUTPUT/'results';FIGURES=OUTPUT;DIAG=OUTPUT/'diagnostics'
PCS=[f'PC{i}' for i in range(1,9)]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'lyrics-round2-v1','axes.titleweight':'semibold'})
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load():
 df=pd.DataFrame(frozen_dataset.load_rows())
 for f in MEASURES:df[f]=pd.to_numeric(df[f],errors='raise')
 assert len(df)==561 and df.song_id.is_unique and np.isfinite(df[MEASURES].to_numpy()).all()
 assert df.groupby('genre').size().to_dict()==dict(zip(GENRES,[79,79,79,85,80,80,79]))
 df.genre=pd.Categorical(df.genre,categories=GENRES,ordered=True)
 # No model fitting or analysis; plotting only.
 for p in [RESULTS,FIGURES,DIAG]:p.mkdir(exist_ok=True)
 return df

def save(name,data,index=False):
 frame=data if isinstance(data,pd.DataFrame) else pd.DataFrame(data)
 frame.to_csv(RESULTS/name,index=index,float_format='%.17g')
def environment():
 import importlib.metadata as md
 return {'input':frozen_dataset.DATASET.relative_to(frozen_dataset.BASE.parent).as_posix(),'input_sha256':frozen_dataset.EXPECTED_SHA256,'python':platform.python_version(),'packages':{x:md.version(x) for x in ['numpy','pandas','scipy','statsmodels','matplotlib','patsy','scikit-learn','joblib','threadpoolctl']}}
def manifest(stage,notes):
 frozen_dataset.verified_path()
 obj=dict(**environment(),completed_utc=datetime.now(timezone.utc).isoformat(),stage=stage,notes=notes,script_hashes={p.name:digest(p) for p in BASE.glob('*.py')})
 (RESULTS/(stage+'_manifest.json')).write_text(json.dumps(obj,indent=2)+'\n')
 print(stage+' complete',flush=True)
def export(fig,stem,diagnostic=False):
 folder=DIAG if diagnostic else FIGURES
 for ext in ['png','pdf','svg']:
  meta={'Creator':'Lyrics frozen v1.1 / Statistical Analysis Round 2'} if ext!='png' else {'Software':'Lyrics frozen v1.1 / Statistical Analysis Round 2'}
  if ext=='pdf':meta.update(CreationDate=None,ModDate=None)
  if ext=='svg':meta['Date']=None
  fig.savefig(folder/(stem+'.'+ext),dpi=300,bbox_inches='tight',metadata=meta)
 plt.close(fig)
def mdtable(frame):
 def fmt(x):return f'{x:.6g}' if isinstance(x,(float,np.floating)) else str(x).replace('|','/').replace('\n',' ')
 return '| '+' | '.join(map(str,frame.columns))+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(x) for x in row)+' |' for row in frame.itertuples(index=False,name=None))

# Same boxplot workflow as approved 03_descriptive_figures.py; visual-only edits.
df=load()
checks=[]
for stem,features,labels,titles in [
 ('Figure2_lexical_final_style',MEASURES[:4],LABELS[:4],['MATTR','Lexical density','Average word length (syllables)','Lexical sophistication']),
 ('Figure3_dependency_structural_final_style',MEASURES[4:],LABELS[4:],['Mean dependency distance (MDD)','Mean hierarchical distance (MHD)','Average line length','Line repetition rate'])]:
 fig,axes=plt.subplots(2,2,figsize=(11.3,7.5))
 for j,(f,label,ax) in enumerate(zip(features,labels,axes.flat)):
  values=[df.loc[df.genre==g,f].to_numpy() for g in GENRES]
  bp=ax.boxplot(values,patch_artist=True,tick_labels=DISPLAY,widths=.58,showfliers=True,whis=1.5,medianprops={'color':'black','linewidth':1.25},flierprops={'marker':'o','markersize':3,'markeredgecolor':'.35','alpha':.55})
  for patch,color in zip(bp['boxes'],COLORS):patch.set_facecolor(color);patch.set_alpha(.65)
  ax.set_ylabel(label);ax.set_title(f'({chr(97+j)}) {label}',loc='left');ax.grid(axis='y',alpha=.15);ax.tick_params(axis='x',labelsize=9)
  # Capture all plotted coordinates and scales before formatting.
  before=[(line.get_xdata().copy(),line.get_ydata().copy()) for line in ax.lines]
  limits=(ax.get_xlim(),ax.get_ylim());ticks=(ax.get_xticks().copy(),ax.get_yticks().copy())
  ax.set_title(f'({chr(97+j)}) {titles[j]}',loc='left')
  assert all(np.array_equal(x,line.get_xdata()) and np.array_equal(y,line.get_ydata()) for (x,y),line in zip(before,ax.lines))
  assert limits==(ax.get_xlim(),ax.get_ylim())
  assert np.array_equal(ticks[0],ax.get_xticks()) and np.array_equal(ticks[1],ax.get_yticks())
  assert [t.get_text() for t in ax.get_xticklabels()]==DISPLAY
  checks.append(dict(feature=f,coordinates_unchanged=True,limits=limits,panel_title=ax.get_title(loc='left')))
 # No overall title; unchanged sample note. Reclaim the former title space.
 fig.text(.08,.015,'N = 561; genre n = 79 / 79 / 79 / 85 / 80 / 80 / 79. Boxes: IQR; line: median; whiskers: 1.5 × IQR; points: outliers.',fontsize=9)
 fig.tight_layout(rect=(0,.045,1,1));export(fig,stem)
(OUTPUT/'visual_format_checks.json').write_text(json.dumps({'dataset_sha256':frozen_dataset.EXPECTED_SHA256,'checks':checks},indent=2))
