import json
from monitoring.metrics import MetricsCollector
from monitoring.alerts import operational_alerts
from monitoring.logging import JsonFormatter
import logging
def test_metrics_distribution_and_alerts():
 m=MetricsCollector();m.record(latency=2,risk=80,level="CRITICAL",synthetic=.9,speaker=.8,alert=True);m.error("phase3");summary=m.summary();assert summary["latency"]["average_ms"]==2000 and summary["risk_distribution"]["CRITICAL"]==1 and summary["error_rate"]==1;alerts=operational_alerts(summary,{"latency":{"warning_ms":1500,"critical_ms":3000},"errors":{"warning_rate":.05,"critical_rate":.15}});assert any(x["type"]=="OPERATIONAL" for x in alerts)
def test_json_logging_redacts():
 record=logging.LogRecord("x",logging.INFO,"",0,"contact user@example.com",(),None);value=json.loads(JsonFormatter().format(record));assert "example.com" not in value["message"]
