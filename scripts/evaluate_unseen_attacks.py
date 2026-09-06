import argparse
from phase12_common import *
from advanced_eval.unseen_generators import leave_one_generator_out,cross_dataset
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",default=ROOT/"configs/advanced_evaluation.yaml");a=p.parse_args();c=config(a.config);minimum=c["evaluation"]["minimum_group_samples"];data=rows();result={"status":"MODEL_REVIEW_RECOMMENDED","note":"Generator metadata is unavailable; no retraining was performed.","leave_one_generator_out":leave_one_generator_out(data,minimum),"cross_dataset":cross_dataset(data,"UNKNOWN","UNKNOWN","UNKNOWN",minimum)};write("unseen_generators.json",result);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
