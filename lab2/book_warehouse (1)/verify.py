import pkgutil, inspect, importlib, warehouse
from dataclasses import is_dataclass
from typing import get_type_hints, get_origin

def is_class(obj): return inspect.isclass(obj)

def iter_classes():
    for _, modname, _ in pkgutil.walk_packages(warehouse.__path__, warehouse.__name__ + "."):
        m = importlib.import_module(modname)
        for name, obj in inspect.getmembers(m, is_class):
            if obj.__module__.startswith("warehouse"):
                yield obj

def count_fields(cls):
    anns = get_type_hints(cls, include_extras=False)
    return len(anns)

def count_methods(cls):
    return len([n for n, v in cls.__dict__.items() if callable(v) and not n.startswith("__")])

def count_associations(cls):
    cnt = 0
    anns = get_type_hints(cls, include_extras=False)
    for t in anns.values():
        target = get_origin(t) or t
        if getattr(target, "__module__", "").startswith("warehouse") and target is not cls:
            cnt += 1
    for n, v in cls.__dict__.items():
        if callable(v):
            try:
                hints = get_type_hints(v, include_extras=False)
            except Exception:
                continue
            for t in hints.values():
                target = get_origin(t) or t
                if getattr(target, "__module__", "").startswith("warehouse"):
                    cnt += 1
    return cnt

classes = list(iter_classes())
domain_classes = [c for c in classes if not issubclass(c, BaseException)]
total_fields = sum(count_fields(c) for c in domain_classes)
total_methods = sum(count_methods(c) for c in domain_classes)
total_assocs = sum(count_associations(c) for c in domain_classes)

print({
    "domain_classes": len(domain_classes),
    "total_fields": total_fields,
    "total_methods": total_methods,
    "associations_estimate": total_assocs
})
