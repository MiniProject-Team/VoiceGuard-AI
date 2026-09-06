import pytest
from mlops.model_registry import ModelRegistry,RegistryError
def artifact(root,name,content="model"):
 path=root/name;path.mkdir();(path/"weights.bin").write_text(content);return path
def test_register_duplicate_hash_and_promotion(tmp_path):
 registry=ModelRegistry(tmp_path/"registry.json");item=registry.register("synthetic_detector","demo","v1",artifact(tmp_path,"v1"),{"test_metrics":{"f1":.5}});assert item["status"]=="CANDIDATE" and registry.validate_hash(item["model_id"])
 with pytest.raises(RegistryError):registry.register("synthetic_detector","demo","v1",tmp_path/"v1",{})
 assert registry.promote(item["model_id"],{})["status"]=="STAGING"
 with pytest.raises(RegistryError):registry.promote(item["model_id"],{"tests":False})
def test_invalid_hash_and_rollback(tmp_path):
 registry=ModelRegistry(tmp_path/"registry.json");a=registry.register("synthetic_detector","demo","v1",artifact(tmp_path,"v1"),{});registry.promote(a["model_id"],{});registry.promote(a["model_id"],{"all":True});b=registry.register("synthetic_detector","demo","v2",artifact(tmp_path,"v2","new"),{});registry.promote(b["model_id"],{});registry.promote(b["model_id"],{"all":True});assert registry.rollback("synthetic_detector")["model_id"]==a["model_id"];(tmp_path/"v1/weights.bin").write_text("tampered");assert not registry.validate_hash(a["model_id"])
 with pytest.raises(RegistryError):registry.register("x","x","v1",tmp_path/"missing",{})
