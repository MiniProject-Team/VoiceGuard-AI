from __future__ import annotations
import numpy as np
from scipy.stats import ks_2samp
def population_stability_index(reference,recent,bins=10)->float:
 ref=np.asarray(reference,float);cur=np.asarray(recent,float);edges=np.unique(np.quantile(ref,np.linspace(0,1,bins+1)));edges[0]=-np.inf;edges[-1]=np.inf;r=np.histogram(ref,edges)[0]/len(ref);c=np.histogram(cur,edges)[0]/len(cur);r=np.clip(r,1e-6,None);c=np.clip(c,1e-6,None);return float(np.sum((c-r)*np.log(c/r)))
def detect_drift(reference,recent,minimum_samples=100,possible_ks=.15,significant_ks=.30,possible_psi=.10,significant_psi=.25)->dict:
 if len(reference)<minimum_samples or len(recent)<minimum_samples:return {"state":"INSUFFICIENT_DATA","reference_count":len(reference),"recent_count":len(recent)}
 ks,p=ks_2samp(reference,recent);psi=population_stability_index(reference,recent);state="SIGNIFICANT_DRIFT" if ks>=significant_ks or psi>=significant_psi else "POSSIBLE_DRIFT" if ks>=possible_ks or psi>=possible_psi else "NO_DRIFT";return {"state":state,"ks_statistic":float(ks),"ks_pvalue":float(p),"psi":psi,"reference_mean":float(np.mean(reference)),"recent_mean":float(np.mean(recent)),"reference_std":float(np.std(reference)),"recent_std":float(np.std(recent))}
