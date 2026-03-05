import threading
from contextlib import contextmanager

_thread_locals = threading.local()

def set_sync_enabled(enabled: bool):
    """设置当前线程是否允许同步到 Neo4j"""
    _thread_locals.neo4j_sync_enabled = enabled

def is_sync_enabled() -> bool:
    """检查当前线程是否允许同步到 Neo4j (默认为 True)"""
    return getattr(_thread_locals, 'neo4j_sync_enabled', True)

@contextmanager
def disable_neo4j_sync():
    """上下文管理器：临时禁用 Neo4j 同步"""
    previous_state = is_sync_enabled()
    try:
        set_sync_enabled(False)
        yield
    finally:
        set_sync_enabled(previous_state)
