"""
Decorators for automatic audit logging.

Provides decorators to automatically log function calls with minimal code changes.
"""

import functools
import time
from typing import Optional, Callable, Any

import structlog

from audit.audit_logger import AuditLogger
from audit.models import EventType, Operation

logger = structlog.get_logger(__name__)


def audit_log(
    event_type: EventType,
    operation: Operation,
    resource_type: str,
    resource_id_param: str = "resource_id",
    user_id_param: Optional[str] = "user_id",
    capture_result: bool = True,
    capture_args: bool = False,
):
    """
    Decorator to automatically audit log function calls.

    Args:
        event_type: Type of audit event
        operation: Operation being performed
        resource_type: Type of resource being operated on
        resource_id_param: Name of parameter containing resource ID
        user_id_param: Name of parameter containing user ID (optional)
        capture_result: Whether to capture function return value in after_state
        capture_args: Whether to capture function arguments in metadata

    Example:
        >>> @audit_log(
        ...     event_type=EventType.LCA_CALCULATION,
        ...     operation=Operation.CALCULATE,
        ...     resource_type="Project",
        ...     resource_id_param="project_id"
        ... )
        ... def calculate_carbon(project_id: str, materials: List[dict]):
        ...     # function implementation
        ...     return {"total_carbon": 1500.5}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            audit = AuditLogger()
            start_time = time.time()

            # Extract resource_id and user_id from arguments
            resource_id = kwargs.get(resource_id_param, "unknown")
            user_id = kwargs.get(user_id_param) if user_id_param else None

            # Capture arguments if requested
            metadata = {}
            if capture_args:
                metadata["args"] = str(args) if args else None
                metadata["kwargs"] = {k: str(v) for k, v in kwargs.items()}
                metadata["function_name"] = func.__name__

            success = True
            error_message = None
            after_state = None

            try:
                result = func(*args, **kwargs)

                # Capture result if requested
                if capture_result:
                    if isinstance(result, dict):
                        after_state = result
                    else:
                        after_state = {"result": str(result)}

                return result

            except Exception as e:
                success = False
                error_message = str(e)
                logger.error(
                    "audit_decorated_function_failed",
                    function=func.__name__,
                    error=error_message,
                )
                raise

            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Log the audit event
                try:
                    audit.log_event(
                        event_type=event_type,
                        operation=operation,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        user_id=user_id,
                        after_state=after_state,
                        metadata=metadata,
                        success=success,
                        error_message=error_message,
                        duration_ms=duration_ms,
                    )
                except Exception as audit_error:
                    # Don't let audit failures break the application
                    logger.error(
                        "audit_logging_failed",
                        function=func.__name__,
                        error=str(audit_error),
                    )

        return wrapper

    return decorator


def audit_context(
    event_type: EventType,
    operation: Operation,
    resource_type: str,
    resource_id: str,
    user_id: Optional[str] = None,
):
    """
    Context manager for audit logging.

    Useful for logging complex operations or code blocks.

    Args:
        event_type: Type of audit event
        operation: Operation being performed
        resource_type: Type of resource being operated on
        resource_id: Resource identifier
        user_id: Optional user identifier

    Example:
        >>> with audit_context(
        ...     event_type=EventType.DATA_CHANGE,
        ...     operation=Operation.UPDATE,
        ...     resource_type="Material",
        ...     resource_id="mat-123"
        ... ):
        ...     # perform updates
        ...     update_material_data(...)
    """

    class AuditContext:
        def __init__(self):
            self.audit = AuditLogger()
            self.start_time = None
            self.success = True
            self.error_message = None
            self.before_state = None
            self.after_state = None
            self.metadata = {}

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration_ms = (time.time() - self.start_time) * 1000

            if exc_type is not None:
                self.success = False
                self.error_message = str(exc_val)

            try:
                self.audit.log_event(
                    event_type=event_type,
                    operation=operation,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    before_state=self.before_state,
                    after_state=self.after_state,
                    metadata=self.metadata,
                    success=self.success,
                    error_message=self.error_message,
                    duration_ms=duration_ms,
                )
            except Exception as audit_error:
                logger.error(
                    "audit_context_logging_failed",
                    error=str(audit_error),
                )

            # Don't suppress the original exception
            return False

    return AuditContext()


class AuditBatch:
    """
    Batch multiple audit events for more efficient logging.

    Useful when performing bulk operations.

    Example:
        >>> batch = AuditBatch()
        >>> for material in materials:
        ...     batch.add_event(
        ...         event_type=EventType.DATA_CHANGE,
        ...         operation=Operation.CREATE,
        ...         resource_type="Material",
        ...         resource_id=material.id
        ...     )
        >>> batch.commit()
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.events = []

    def add_event(
        self,
        event_type: EventType,
        operation: Operation,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        metadata: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        """Add an event to the batch."""
        self.events.append(
            {
                "event_type": event_type,
                "operation": operation,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "before_state": before_state,
                "after_state": after_state,
                "metadata": metadata,
                "success": success,
                "error_message": error_message,
            }
        )

    def commit(self):
        """Commit all events in the batch."""
        for event_data in self.events:
            try:
                self.audit.log_event(**event_data)
            except Exception as e:
                logger.error(
                    "batch_event_logging_failed",
                    error=str(e),
                    event_data=event_data,
                )

        count = len(self.events)
        self.events.clear()

        logger.info("audit_batch_committed", event_count=count)

    def __len__(self):
        return len(self.events)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        return False
