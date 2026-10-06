from common import *
df=load();r=pd.DataFrame(index=MEASURES,columns=MEASURES,dtype=float);p=r.copy();cross=[]
for a in MEASURES:
 for b in MEASURES:
  if a==b:r.loc[a,b]=1;p.loc[a,b]=np.nan
  else:r.loc[a,b],p.loc[a,b]=stats.pearsonr(df[a],df[b])
for a in MEASURES[:4]:
 for b in MEASURES[4:]:
  result=stats.pearsonr(df[a],df[b]);ci=result.confidence_interval(.95)
  cross.append(dict(lexical=a,syntactic=b,N=len(df),r=result.statistic,p_raw=result.pvalue,ci95_lower=ci.low,ci95_upper=ci.high))
c=pd.DataFrame(cross);c['p_BH_FDR']=multipletests(c.p_raw,method='fdr_bh')[1];c['significant_raw']=c.p_raw<.05;c['significant_FDR']=c.p_BH_FDR<.05
save('pearson_r_matrix.csv',r,index=True);save('pearson_p_matrix.csv',p,index=True);save('cross_domain_correlations.csv',c)
manifest('03_correlations',{'tests':'two-sided Pearson, no deletion; diagonal p is undefined and blank','primary':'16 cross-domain raw p values','sensitivity':'BH FDR across exactly the 16 cross-domain p values','CI':'Fisher z 95%','scope':'pooled song-level association; not proof of independence or causation'})
