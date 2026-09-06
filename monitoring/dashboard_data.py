def safe_monitoring_summary(metrics,model_versions,drift_state="INSUFFICIENT_DATA"):
 return {**metrics.summary(),"model_versions":model_versions,"drift_state":drift_state}
