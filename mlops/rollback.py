from .model_registry import ModelRegistry
def rollback(registry_path,model_type):return ModelRegistry(registry_path).rollback(model_type)
