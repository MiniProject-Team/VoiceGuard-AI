def operational_alerts(summary,config):
 alerts=[];latency=summary["latency"]["p95_ms"];rate=summary["error_rate"]
 if latency is not None and latency>=config["latency"]["critical_ms"]:alerts.append({"type":"OPERATIONAL","severity":"CRITICAL","code":"LATENCY_HIGH"})
 elif latency is not None and latency>=config["latency"]["warning_ms"]:alerts.append({"type":"OPERATIONAL","severity":"WARNING","code":"LATENCY_ELEVATED"})
 if rate>=config["errors"]["critical_rate"]:alerts.append({"type":"OPERATIONAL","severity":"CRITICAL","code":"ERROR_RATE_HIGH"})
 elif rate>=config["errors"]["warning_rate"]:alerts.append({"type":"OPERATIONAL","severity":"WARNING","code":"ERROR_RATE_ELEVATED"})
 return alerts
