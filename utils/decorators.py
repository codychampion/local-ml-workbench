"""
Pipeline Decorators - No-op Flow and Task Decorators
=====================================================
Provides no-op @flow and @task decorators for pipeline consistency.
Previously used Prefect; these maintain the pattern without dependency.
"""

from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)


def flow(*args, **kwargs) -> Callable[[F], F]:
    """No-op flow decorator (Prefect removed)."""
    def decorator(fn: F) -> F:
        return fn
    return decorator if not args or callable(args[0]) else decorator


def task(*args, **kwargs) -> Callable[[F], F]:
    """No-op task decorator (Prefect removed)."""
    def decorator(fn: F) -> F:
        return fn
    return decorator if not args or callable(args[0]) else decorator
