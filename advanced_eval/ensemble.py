class DetectorEnsemble:
    def __init__(self,strategy="mean_probability",weights=None):self.strategy=strategy;self.weights=weights or {};self.detectors={}
    def add_detector(self,name,detector,weight=1.):self.detectors[name]=detector;self.weights[name]=weight
    def predict(self,sample):
        if not self.detectors:raise ValueError("No detectors configured")
        scores={name:float(detector(sample)) for name,detector in self.detectors.items()};values=list(scores.values())
        if self.strategy=="maximum_risk":combined=max(values)
        elif self.strategy=="majority_voting":combined=sum(v>=.5 for v in values)/len(values)
        elif self.strategy=="weighted_mean":combined=sum(scores[n]*self.weights.get(n,1) for n in scores)/sum(self.weights.get(n,1) for n in scores)
        elif self.strategy=="mean_probability":combined=sum(values)/len(values)
        else:raise ValueError("Unknown ensemble strategy")
        return {"probability":combined,"detectors":scores,"strategy":self.strategy}
