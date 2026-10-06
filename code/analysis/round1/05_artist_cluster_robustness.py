from common import *
df=load();sizes=df.groupby('primary_artist').size();dist=sizes.value_counts().sort_index();G=len(sizes)
summary={'unique_primary_artists':G,'singleton_artists':int((sizes==1).sum()),'singleton_artist_percent':100*(sizes==1).mean(),'singleton_song_percent':100*(sizes==1).sum()/len(df),'median_songs_per_artist':sizes.median(),'maximum_songs_per_artist':sizes.max(),'songs':len(df)}
save('artist_cluster_summary.csv',[summary]);save('artist_cluster_sizes.csv',sizes.rename('songs').reset_index());save('artist_cluster_size_distribution.csv',[dict(songs_per_artist=int(n),artists=int(c),songs=int(n*c)) for n,c in dist.items()])
print('CLUSTER_SUMMARY '+json.dumps({k:(float(v) if v is not None else None) for k,v in summary.items()}),flush=True)
s,c,r,l=models(df,'cluster')
for name,data in [('cluster_models.csv',s),('cluster_coefficients.csv',c),('cluster_rap_contrasts.csv',r),('cluster_genre_slopes.csv',l)]:save(name,data)
# Refit HC3 in this stage so its comparisons never rely on historical results.
hs,hc,hr,hl=models(df,'HC3');comp=c.merge(hc[hc.model=='M1'],on=['outcome','model','term'],suffixes=('_cluster','_HC3'));comp['significance_changed']=(comp.p_cluster<.05)!=(comp.p_HC3<.05);save('cluster_vs_HC3_coefficients.csv',comp)
assert np.allclose(comp.coefficient_cluster,comp.coefficient_HC3,rtol=0,atol=1e-14)
manifest('05_artist_cluster_robustness',{'cluster_definition':'exact frozen primary_artist string, no alias merging, no singleton exclusion','correction':'CR1 covariance factor G/(G-1)*(N-1)/(N-k); t/F inference with G-1 df; statsmodels use_correction=True, df_correction=True, use_t=True','models':'Main adjusted MDD/MHD M1 only; same OLS estimates as HC3, alternative covariance','limitations':'Clusters use exact public v1.1 primary_artist strings without alias merging.'})
