import csv,json
from collections import Counter
from phase12_common import *
from threat_intel.taxonomy import AttackFamily
def load(name,default):
 p=OUT/name;return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
def main():
 data=rows();bench=load("benchmark_summary.json",{});unseen=load("unseen_generators.json",{});replay=load("replay_results.json",{});channel=load("channel_shift.json",{});unc=load("uncertainty_summary.json",{})
 trends=f"""# Phase 12 threat trends

- Events analyzed: {len(data)}
- Risk levels: UNKNOWN (risk labels are not present in the Phase 3 prediction file)
- Attack-family labels: {dict(Counter(x['attack_family'] for x in data))}
- Channels: {dict(Counter(x['channel_type'] for x in data))}
- Languages: {dict(Counter(x['language'] for x in data))}
- Uncertainty: {unc.get('counts','NOT TESTED')}
- Detector disagreement observations: 4 Phase 6 rows; **INSUFFICIENT DATA**.

These are privacy-safe demo observations, not evidence of a live campaign or real-world identity.
""";OUT.mkdir(parents=True,exist_ok=True);(OUT/"threat_trends.md").write_text(trends,encoding="utf-8")
 review="""# Model review

Status: **MODEL_REVIEW_RECOMMENDED**

The current Phase 3 debug model missed both synthetic examples in its three-sample test set (FNR 1.0). Every research subgroup is below the configured minimum of 20. Unseen-generator and replay performance are not measurable because required labels/data are unavailable. Phase 9 benign channel simulations also contain only three samples each.

Recommended future collection: consented Hindi and other target-language genuine/synthetic speech; telephone and VoIP samples; independently sourced new generator families; benign controlled replay and re-recording samples; balanced noisy genuine samples. Keep these datasets versioned, pseudonymous, legally sourced, and separate by generator/source to prevent leakage. Do not retrain or deploy automatically.
""";(OUT/"model_review.md").write_text(review,encoding="utf-8")
 report=f"""# Phase 12 defensive threat report

## 1. Current threat taxonomy
{', '.join(x.value for x in AttackFamily)}. These labels are analytical hypotheses, not perfect attribution.

## 2. Evaluation datasets
Only the three-sample Phase 3 debug test set and prior benign Phase 9 channel simulations are available. Generator, replay, and useful language metadata are unavailable.

## 3. Known-generator performance
**INSUFFICIENT DATA.** Aggregate clean metrics are retained in `benchmark.csv`; generator identity is UNKNOWN.

## 4. Unseen-generator performance
**NOT TESTED.** {unseen.get('note','No result available')}

## 5. Replay performance
**NOT TESTED.** {replay.get('note','No result available')}

## 6. Channel robustness
Benign simulated conditions were evaluated previously, but every condition has 3 samples and is **INSUFFICIENT DATA**.

## 7. Detector disagreement
Four pseudonymous Phase 6 observations were exported. The synthetic detector leaned real while the speaker verifier reported mismatch under its calibrated threshold; this requires review and is not proof of attack. The high-fake/high-match clone pattern remains a HIGH-priority rule but was not observed.

## 8. Uncertainty
{unc.get('counts','NOT TESTED')}. Probability distance and entropy are proxy measures, not guaranteed certainty.

## 9. High-risk failure modes
The only measurable synthetic group had FNR 1.0 (2/2 missed), but is far below minimum sample size. High-FPR ranking is unavailable at reliable group size. Unseen generators, replay, language, and channel-by-attack results are not established.

## 10. Recommendations
Keep Phase 3 as the default and the optional ensemble disabled. Collect consented, balanced, versioned datasets for new generators, replay, channels, and target languages; run offline evaluation; require human approval for policy changes, retraining, and deployment.

No offensive cloning, bypass optimization, attack automation, raw audio, embeddings, transcripts, phone numbers, or identities are included.
""";(OUT/"threat_report.md").write_text(report,encoding="utf-8")
 dashboard={"sample_count":len(data),"data_status":"INSUFFICIENT DATA","attack_families":dict(Counter(x["attack_family"] for x in data)),"channels":dict(Counter(x["channel_type"] for x in data)),"languages":dict(Counter(x["language"] for x in data)),"uncertainty":unc.get("counts",{}),"unseen_generator":"NOT TESTED","replay":"NOT TESTED","automatic_policy_change":False,"raw_audio_included":False};write("dashboard_summary.json",dashboard);print(OUT/"threat_report.md")
if __name__=="__main__":main()
