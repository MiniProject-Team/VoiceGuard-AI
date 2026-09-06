import csv
import numpy as np
from advanced_eval.benchmark import binary_metrics,grouped_metrics,write_benchmark
from advanced_eval.uncertainty import analyze_uncertainty
from advanced_eval.disagreement import disagreement_profile
from advanced_eval.ensemble import DetectorEnsemble
from advanced_eval.perturbation import safe_perturb
def test_uncertainty():assert analyze_uncertainty(.5)["level"]=="HIGH_UNCERTAINTY" and analyze_uncertainty(.99)["level"]=="LOW_UNCERTAINTY"
def test_clone_disagreement_priority():
 r=disagreement_profile(.9,.9,70);assert r["priority"]=="HIGH" and "possible cloned" in r["result"] and not r["proof_of_attack"]
def test_absent_metadata_and_minimum():assert grouped_metrics([{"label":1,"score":.2}],"generator_family",20)[0]["status"]=="INSUFFICIENT DATA"
def test_metrics_and_report(tmp_path):
 r=[{"label":1,"score":.9},{"label":0,"score":.1}];assert binary_metrics(r)["f1"]==1
 p=tmp_path/"b.csv";write_benchmark(p,[{"test":"x","condition":"clean","sample_count":2,"notes":"INSUFFICIENT DATA"}]);assert list(csv.DictReader(p.open()))[0]["test"]=="x"
def test_ensemble_and_safe_perturbation():
 e=DetectorEnsemble();e.add_detector("default_phase3",lambda _: .6);assert e.predict(None)["probability"]==.6
 x=np.ones(100,dtype=np.float32);assert safe_perturb(x,"small_gain").shape==x.shape
