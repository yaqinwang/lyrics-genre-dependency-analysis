from common import *
df=load();rows=[]
for f in MEASURES:
 for g in GENRES:
  x=df.loc[df.genre==g,f];n=len(x);sd=x.std(ddof=1);half=stats.t.ppf(.975,n-1)*sd/np.sqrt(n)
  rows.append(dict(feature=f,genre=g,N=n,mean=x.mean(),sample_SD=sd,median=x.median(),Q1=x.quantile(.25),Q3=x.quantile(.75),IQR=x.quantile(.75)-x.quantile(.25),minimum=x.min(),maximum=x.max(),mean_CI95_lower=x.mean()-half,mean_CI95_upper=x.mean()+half))
r=pd.DataFrame(rows);save('descriptives_full.csv',r)
wide=pd.DataFrame({'genre':GENRES,'N':[sum(df.genre==g) for g in GENRES]})
for f in MEASURES:
 t=r[r.feature==f].set_index('genre');wide[f]=[f"{t.loc[g,'mean']:.3f} ({t.loc[g,'sample_SD']:.3f})" for g in GENRES]
save('descriptives_manuscript_mean_SD.csv',wide)
manifest('01_descriptives',{'SD':'sample, ddof=1','IQR':'linear-interpolated 75th minus 25th percentiles','mean_CI':'two-sided Student t, n-1 df, song-level independence; not artist-cluster adjusted','units':'density fraction; sophistication and repetition percent; avg_syllables syllables/token'})
