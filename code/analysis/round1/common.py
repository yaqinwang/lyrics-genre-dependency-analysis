"""Round 1 methods; frozen-input verification is mandatory for every entry point."""
from pathlib import Path
import sys,os,json,hashlib,platform,itertools
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
sys.path[:0]=[str(BASE/'vendor'),str(BASE.parent.parent)]
os.environ['MPLCONFIGDIR']=str(BASE/'diagnostics/.matplotlib')
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.multitest import multipletests
import patsy
import frozen_dataset_v1_1 as frozen_dataset
GENRES=['pop','rock','gospel','r&b','rap','country','reggae']
MEASURES=['MATTR','lexical_density','avg_syllables','lexical_sophistication','MDD','MHD','avg_line_length','line_repetition_rate']
RESULTS=BASE/'results';DIAG=BASE/'diagnostics'
def load():
    # load_rows verifies manifest + pinned SHA and parses those same verified bytes.
    df=pd.DataFrame(frozen_dataset.load_rows())
    for c in MEASURES+['token_count']:df[c]=pd.to_numeric(df[c],errors='raise')
    assert len(df)==561 and df['song_id'].is_unique
    assert df.groupby('genre').size().to_dict()==dict(zip(GENRES,[79,79,79,85,80,80,79]))
    assert np.isfinite(df[MEASURES].to_numpy()).all()
    assert df['primary_artist'].str.strip().ne('').all()
    df['genre']=pd.Categorical(df['genre'],categories=GENRES,ordered=True)
    df['centered_avg_line_length']=df.avg_line_length-df.avg_line_length.mean()
    RESULTS.mkdir(exist_ok=True);DIAG.mkdir(exist_ok=True)
    return df

def save(name,data,index=False):
    p=RESULTS/name
    frame=data if isinstance(data,pd.DataFrame) else pd.DataFrame(data)
    frame.to_csv(p,index=index,float_format='%.17g')
    return p

def manifest(stage,notes=None):
    import importlib.metadata as md
    frozen_dataset.verified_path()
    result={'stage':stage,'completed_utc':datetime.now(timezone.utc).isoformat(),'input':frozen_dataset.DATASET.relative_to(frozen_dataset.BASE.parent).as_posix(),'input_sha256':frozen_dataset.EXPECTED_SHA256,'verified_loader':'frozen_dataset.load_rows (manifest + pinned hash)','python':platform.python_version(),'packages':{n:md.version(n) for n in ['numpy','pandas','scipy','statsmodels','matplotlib','patsy']},'script_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob('*.py')},'notes':notes}
    (RESULTS/(stage+'_manifest.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'stage':stage,'status':'complete','input_sha256':frozen_dataset.EXPECTED_SHA256}),flush=True)

def anova_and_pairs(df,features):
    omnibus=[];pairs=[];gh=[]
    for feature in features:
        groups=[df.loc[df.genre==g,feature].to_numpy() for g in GENRES]
        n=sum(map(len,groups));grand=np.concatenate(groups).mean()
        ssb=sum(len(x)*(x.mean()-grand)**2 for x in groups);ssw=sum(np.sum((x-x.mean())**2) for x in groups)
        f,p=stats.f_oneway(*groups);w=anova_oneway(groups,use_var='unequal',welch_correction=True)
        assert np.isclose(f,(ssb/6)/(ssw/(n-7)),rtol=1e-12)
        omnibus.append(dict(feature=feature,N=n,F=f,df_between=6,df_within=n-7,p=p,eta_squared=ssb/(ssb+ssw),SS_between=ssb,SS_within=ssw,welch_F=w.statistic,welch_df_between=w.df_num,welch_df_within=w.df_denom,welch_p=w.pvalue))
        for (i,a),(j,b) in itertools.combinations(enumerate(GENRES),2):
            x,y=groups[i],groups[j];nx,ny=len(x),len(y);vx,vy=x.var(ddof=1),y.var(ddof=1);diff=x.mean()-y.mean()
            t,praw=stats.ttest_ind(x,y,equal_var=True);pooled=np.sqrt(((nx-1)*vx+(ny-1)*vy)/(nx+ny-2))
            pairs.append(dict(feature=feature,group1=a,group2=b,n1=nx,n2=ny,mean1=x.mean(),mean2=y.mean(),mean_difference=diff,t=t,df=nx+ny-2,p_raw=praw,p_bonferroni=min(21*praw,1.),cohens_d=diff/pooled,significant_bonferroni=21*praw<.05))
            se=np.sqrt(vx/nx+vy/ny);dof=(vx/nx+vy/ny)**2/((vx/nx)**2/(nx-1)+(vy/ny)**2/(ny-1));q=np.sqrt(2)*abs(diff)/se
            pgh=stats.studentized_range.sf(q,7,dof);crit=stats.studentized_range.ppf(.95,7,dof)*se/np.sqrt(2)
            gh.append(dict(feature=feature,group1=a,group2=b,n1=nx,n2=ny,mean1=x.mean(),mean2=y.mean(),mean_difference=diff,q=q,df=dof,p_games_howell=pgh,ci95_lower=diff-crit,ci95_upper=diff+crit,significant_games_howell=pgh<.05))
    return pd.DataFrame(omnibus),pd.DataFrame(pairs),pd.DataFrame(gh)

def models(df,cov_type):
    summaries=[];coefficients=[];contrasts=[];slopes=[]
    for outcome in ['MDD','MHD']:
        for name,formula in [('M0',f'{outcome} ~ C(genre)'),('M1',f'{outcome} ~ C(genre) + centered_avg_line_length'),('interaction',f'{outcome} ~ C(genre) * centered_avg_line_length')]:
            if cov_type=='cluster' and name!='M1':continue
            fit=smf.ols(formula,data=df)
            if cov_type=='HC3':res=fit.fit(cov_type='HC3',use_t=True)
            else:res=fit.fit(cov_type='cluster',cov_kwds={'groups':df.primary_artist,'use_correction':True,'df_correction':True},use_t=True)
            names=list(res.params.index);ci=res.conf_int()
            for term in names:coefficients.append(dict(outcome=outcome,model=name,covariance=cov_type,term=term,coefficient=res.params[term],SE=res.bse[term],ci95_lower=ci.loc[term,0],ci95_upper=ci.loc[term,1],t=res.tvalues[term],p=res.pvalues[term],inference_df=getattr(res,'df_resid_inference',res.df_resid)))
            genre=[i for i,t in enumerate(names) if t.startswith('C(genre)') and ':' not in t]
            test=res.f_test(np.eye(len(names))[genre])
            row=dict(outcome=outcome,model=name,covariance=cov_type,N=int(res.nobs),R_squared=res.rsquared,adjusted_R_squared=res.rsquared_adj,genre_F=float(test.fvalue),genre_df_num=float(test.df_num),genre_df_denom=float(test.df_denom),genre_p=float(test.pvalue),centered_at=df.avg_line_length.mean(),genre_test_interpretation='at grand mean line length' if name=='interaction' else 'common genre effects')
            if name=='interaction':
                inds=[i for i,t in enumerate(names) if ':' in t];it=res.f_test(np.eye(len(names))[inds]);row.update(interaction_F=float(it.fvalue),interaction_df_num=float(it.df_num),interaction_df_denom=float(it.df_denom),interaction_p=float(it.pvalue))
            if cov_type=='cluster':
                G=df.primary_artist.nunique();k=len(names);row.update(clusters=G,finite_cluster_covariance_multiplier=G/(G-1)*(len(df)-1)/(len(df)-k),cluster_inference_df=G-1)
            summaries.append(row)
            def design(genre,length=0.):
                return np.asarray(patsy.build_design_matrices([res.model.data.design_info],pd.DataFrame({'genre':[genre],'centered_avg_line_length':[length]}))[0])[0]
            for genre_other in GENRES:
                if genre_other=='rap':continue
                c=design('rap')-design(genre_other);test=res.t_test(c);bounds=np.asarray(test.conf_int()).ravel()
                contrasts.append(dict(outcome=outcome,model=name,covariance=cov_type,contrast='rap - '+genre_other,estimate=float(np.asarray(test.effect).item()),SE=float(np.asarray(test.sd).item()),ci95_lower=bounds[0],ci95_upper=bounds[1],p=float(np.asarray(test.pvalue).item()),p_bonferroni_six=min(1.,6*float(np.asarray(test.pvalue).item()))))
            if name in ['M1','interaction']:
                for g in GENRES:
                    test=res.t_test(design(g,1.)-design(g,0.));bounds=np.asarray(test.conf_int()).ravel()
                    slopes.append(dict(outcome=outcome,model=name,covariance=cov_type,genre=g,slope=float(np.asarray(test.effect).item()),SE=float(np.asarray(test.sd).item()),ci95_lower=bounds[0],ci95_upper=bounds[1],p=float(np.asarray(test.pvalue).item())))
    return [pd.DataFrame(x) for x in [summaries,coefficients,contrasts,slopes]]
