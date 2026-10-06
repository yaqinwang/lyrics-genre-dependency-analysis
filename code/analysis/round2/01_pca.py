from common import *
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

df=load();X=df[MEASURES].to_numpy();scaler=StandardScaler();Z=scaler.fit_transform(X)
pca=PCA(n_components=8,svd_solver='full',whiten=False).fit(Z)
# Deterministic orientation: largest-absolute coefficient positive for each PC.
coeff=pca.components_.copy();sign=np.sign(coeff[np.arange(8),np.argmax(abs(coeff),axis=1)]);coeff*=sign[:,None]
scores=(Z-pca.mean_)@coeff.T;eig=pca.explained_variance_;loadings=coeff.T*np.sqrt(eig)
save('pca_scaling.csv',{'feature':MEASURES,'mean':scaler.mean_,'scaling_SD_ddof0':scaler.scale_,'sample_SD_ddof1':X.std(axis=0,ddof=1),'standardized_mean':Z.mean(axis=0),'standardized_SD_ddof0':Z.std(axis=0,ddof=0)})
save('pca_variance.csv',{'PC':PCS,'eigenvalue_sample_covariance':eig,'variance_explained_fraction':pca.explained_variance_ratio_,'variance_explained_percent':pca.explained_variance_ratio_*100,'cumulative_percent':np.cumsum(pca.explained_variance_ratio_)*100,'sign_multiplier_from_sklearn':sign})
for name,values in [('pca_component_coefficients.csv',coeff.T),('pca_loadings.csv',loadings)]:
 t=pd.DataFrame(values,columns=PCS);t.insert(0,'feature',MEASURES);save(name,t)
s=pd.concat([df[['song_id','file_id','genre','primary_artist']].reset_index(drop=True),pd.DataFrame(scores,columns=PCS)],axis=1);save('pca_song_scores.csv',s)
c=s.groupby('genre',observed=True)[PCS].mean().reset_index();c.insert(1,'N',[sum(df.genre==g) for g in GENRES]);save('pca_genre_centroids.csv',c)
summary=[]
for g in GENRES:
 for pc in PCS:
  v=s.loc[s.genre==g,pc];summary.append(dict(genre=g,PC=pc,N=len(v),mean=v.mean(),sample_SD=v.std(ddof=1),minimum=v.min(),q05=v.quantile(.05),q25=v.quantile(.25),median=v.median(),q75=v.quantile(.75),q95=v.quantile(.95),maximum=v.max()))
save('pca_genre_score_distributions.csv',summary)
# Numerical validation against separate eigen-decomposition, reconstruction and repeat fit.
vals,vecs=np.linalg.eigh(np.cov(Z,rowvar=False));assert np.allclose(vals[::-1],eig,rtol=1e-12,atol=1e-14)
assert np.allclose(scores@coeff+pca.mean_,Z,rtol=1e-12,atol=1e-12)
assert np.allclose(coeff@coeff.T,np.eye(8),atol=1e-12)
assert np.allclose(np.cov(scores,rowvar=False),np.diag(eig),atol=1e-12)
assert np.isclose(eig.sum(),8*561/560)
second=PCA(n_components=8,svd_solver='full',whiten=False).fit(Z);assert np.array_equal(second.components_,pca.components_)
# This convention is sqrt(N/(N-1)) times the feature-PC Pearson correlation.
actual=np.corrcoef(Z.T,scores.T)[:8,8:];assert np.allclose(loadings,actual*np.sqrt(561/560),atol=1e-12)
save('pca_validation.csv',[dict(check=x,passed=True) for x in ['independent covariance eigensystem','reconstruction with all PCs','orthonormal coefficients','diagonal score covariance','ddof convention eigenvalue sum','identical repeated deterministic fit','documented loading convention']])
fig,ax=plt.subplots(figsize=(9.2,6.6))
for g,label,color in zip(GENRES,DISPLAY,COLORS):
 t=s[s.genre==g];cent=c[c.genre==g].iloc[0]
 ax.scatter(t.PC1,t.PC2,s=19,alpha=.48,c=color,edgecolors='none',label=f'{label} (n={len(t)})')
 ax.scatter(cent.PC1,cent.PC2,s=130,c=color,marker='D',edgecolors='black',linewidths=.9,zorder=5)
ax.axhline(0,color='.75',lw=.7,zorder=0);ax.axvline(0,color='.75',lw=.7,zorder=0)
ax.set(xlabel=f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)',ylabel=f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)',title='Song-level PCA: individual songs and genre centroids')
ax.set_aspect('equal',adjustable='datalim');ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False,title='Genre')
fig.text(.12,.015,'Diamonds = genre means. Descriptive projection; no confidence ellipses or separation tests.',fontsize=9)
fig.tight_layout(rect=(0,.04,1,1));export(fig,'figure4_pca')
manifest('01_pca',{'N':561,'features':MEASURES,'scaling':'StandardScaler population SD ddof=0','PCA':'full deterministic SVD, 8 components, no whitening','eigenvalue':'sample covariance denominator N-1','loadings':'component coefficient * sqrt(eigenvalue); retained historical convention, not exactly Pearson correlations under population scaling','orientation':'largest absolute coefficient positive per PC','plot':'all 561 songs + 7 means; no ellipses, no inferential cluster tests','validation':'all seven numerical checks passed'})
