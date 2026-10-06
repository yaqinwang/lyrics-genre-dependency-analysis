"""Round 2 uses the frozen v1.1 input and no historical analysis data."""
from pathlib import Path
import sys,os,json,hashlib,platform
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent;ROUND1=BASE.parent/'round1'
sys.path[:0]=[str(BASE/'vendor'),str(ROUND1/'vendor'),str(BASE.parent.parent)]
os.environ['MPLCONFIGDIR']=str(BASE/'diagnostics/.matplotlib')
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
RESULTS=BASE/'results';FIGURES=BASE/'figures';DIAG=BASE/'diagnostics'
PCS=[f'PC{i}' for i in range(1,9)]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'lyrics-round2-v1','axes.titleweight':'semibold'})
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load():
 df=pd.DataFrame(frozen_dataset.load_rows())
 for f in MEASURES:df[f]=pd.to_numeric(df[f],errors='raise')
 assert len(df)==561 and df.song_id.is_unique and np.isfinite(df[MEASURES].to_numpy()).all()
 assert df.groupby('genre').size().to_dict()==dict(zip(GENRES,[79,79,79,85,80,80,79]))
 df.genre=pd.Categorical(df.genre,categories=GENRES,ordered=True)
 df['centered_avg_line_length']=df.avg_line_length-df.avg_line_length.mean()
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
