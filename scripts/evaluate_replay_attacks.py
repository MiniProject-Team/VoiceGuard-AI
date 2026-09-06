import argparse,json
from phase12_common import *
from advanced_eval.replay import evaluate_replay
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",default=ROOT/"configs/advanced_evaluation.yaml");a=p.parse_args();c=config(a.config);result={"conditions":evaluate_replay(rows(),c["evaluation"]["minimum_group_samples"]),"note":"No labelled replay dataset is available; controlled replay performance is NOT TESTED."};write("replay_results.json",result);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
