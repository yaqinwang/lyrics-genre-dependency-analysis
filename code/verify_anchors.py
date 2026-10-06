"""Verify manuscript anchors from freshly generated statistical output."""
from pathlib import Path
import csv,json
from collections import Counter
from frozen_dataset_v1_1 import load_rows
B=Path(__file__).resolve().parent
rows=load_rows();assert len(rows)==561
assert Counter(r['genre'] for r in rows)==dict(zip(['pop','rock','gospel','r&b','rap','country','reggae'],[79,79,79,85,80,80,79]))
def read(p):return list(csv.DictReader(p.open()))
pca=read(B/'analysis/round2/results/pca_variance.csv')
m=read(B/'analysis/round1/results/hc3_models.csv')
c=read(B/'analysis/round1/results/cross_domain_correlations.csv')
checks={}
def check(k,v,target,tol):
 assert abs(v-target)<=tol,(k,v,target)
 checks[k]={'actual':v,'target':target,'tolerance':tol,'passed':True}
for k,v,t in [('PC1',float(pca[0]['variance_explained_percent']),33.68294),('PC2',float(pca[1]['variance_explained_percent']),23.35301),('PC1 + PC2',float(pca[1]['cumulative_percent']),57.03596)]:check(k,v,t,0.00001)
for outcome,target,itarget in [('MDD',.00564,.00129),('MHD',.00132,.69370)]:
 check(outcome+' M1 genre p',float(next(r for r in m if r['outcome']==outcome and r['model']=='M1')['genre_p']),target,.00001)
 check(outcome+' interaction p',float(next(r for r in m if r['outcome']==outcome and r['model']=='interaction')['interaction_p']),itarget,.00001)
for f,target in [('MDD',-.0270),('line_repetition_rate',-.4127)]:check('MATTR / '+f,float(next(r for r in c if r['lexical']=='MATTR' and r['syntactic']==f)['r']),target,.00005)
(B.parent/'anchor_verification.json').write_text(json.dumps({'N':len(rows),'genre_counts':Counter(r['genre'] for r in rows),'checks':checks},indent=2)+'\n')
print('PASS: all manuscript anchors')
