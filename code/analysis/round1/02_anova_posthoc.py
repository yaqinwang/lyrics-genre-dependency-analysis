from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
df=load();o,p,g=anova_and_pairs(df,MEASURES)
save('anova_omnibus.csv',o);save('bonferroni_pairwise.csv',p);save('games_howell_pairwise.csv',g)
c=p.merge(g,on=['feature','group1','group2'],suffixes=('_primary','_sensitivity'));c['decision_differs']=c.significant_bonferroni!=c.significant_games_howell;save('anova_sensitivity_pair_comparison.csv',c)
variance=[];residuals=[];qq=[]
fig,axes=plt.subplots(4,2,figsize=(12,15));fig2,axes2=plt.subplots(4,2,figsize=(12,15))
for f,ax,bx in zip(MEASURES,axes.flat,axes2.flat):
 fit=smf.ols(f'{f} ~ C(genre)',data=df).fit();res=np.asarray(fit.resid);groups=[df.loc[df.genre==x,f].to_numpy() for x in GENRES]
 lev=stats.levene(*groups,center='median');variances=[x.var(ddof=1) for x in groups]
 for genre,x in zip(GENRES,groups):variance.append(dict(feature=f,genre=genre,N=len(x),sample_variance=x.var(ddof=1),sample_SD=x.std(ddof=1),skewness=stats.skew(x,bias=False),excess_kurtosis=stats.kurtosis(x,bias=False),max_min_variance_ratio=max(variances)/min(variances),brown_forsythe_F=lev.statistic,brown_forsythe_p=lev.pvalue))
 infl=fit.get_influence()
 for i,r in df.iterrows():residuals.append(dict(song_id=r.song_id,genre=r.genre,feature=f,fitted=float(fit.fittedvalues.iloc[i]),residual=res[i],studentized_residual=infl.resid_studentized_internal[i],cooks_distance=infl.cooks_distance[0][i]))
 (theory,observed),(slope,intercept,corr)=stats.probplot(res,dist='norm')
 for t,v in zip(theory,observed):qq.append(dict(feature=f,theoretical_normal_quantile=t,ordered_residual=v))
 ax.scatter(theory,observed,s=7,alpha=.65);ax.plot(theory,intercept+slope*theory,color='firebrick');ax.set(title=f,xlabel='Normal quantile',ylabel='OLS residual')
 bx.scatter(fit.fittedvalues,res,s=7,alpha=.5);bx.axhline(0,color='firebrick');bx.set(title=f,xlabel='Fitted genre mean',ylabel='Residual')
fig.tight_layout();fig.savefig(DIAG/'anova_residual_QQ.png',dpi=150);plt.close(fig)
fig2.tight_layout();fig2.savefig(DIAG/'anova_residual_fitted.png',dpi=150);plt.close(fig2)
save('variance_diagnostics.csv',variance);save('anova_residuals.csv',residuals);save('qq_coordinates.csv',qq)
manifest('02_anova_posthoc',{'primary':'classical one-way ANOVA; eta2=SSbetween/SStotal','posthoc':'21 equal-variance independent t tests per feature, two-sided; Bonferroni within feature; signed d=(mean1-mean2)/pooled sample SD','sensitivity':'Welch ANOVA with correction; Games-Howell studentized-range q=sqrt(2)*abs(diff)/sqrt(s1²/n1+s2²/n2), k=7, Welch-Satterthwaite pair df. GH p is familywise; no extra Bonferroni.','alpha':.05,'diagnostics':'Q-Q and residual/fitted plots, group skew/kurtosis/variances, median-centered Levene (Brown-Forsythe); no Shapiro screening'})
