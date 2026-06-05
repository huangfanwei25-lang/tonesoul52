"""ToneSoul Observability Infrastructure.

Provides structured logging, token metering, action auditing,
and environment configuration for the ToneSoul system.
"""

from .action_audit import ActionAuditor
from .env_config import get_env, load_env
from .execution_honesty import (
    ExecutionEvidenceResult,
    ExecutionPromise,
    check_promise,
    reduce_promises,
)
from .logger import get_logger
from .self_claim_audit import SelfClaimAudit, audit_self_claim, reduce_self_claims
from .token_meter import TokenMeter

__ts_layer__ = "observability"
__ts_purpose__ = "Observability package: monitoring, audit, metrics, and status readout exports."

__all__ = [
    "ActionAuditor",
    "ExecutionEvidenceResult",
    "ExecutionPromise",
    "SelfClaimAudit",
    "TokenMeter",
    "audit_self_claim",
    "check_promise",
    "get_env",
    "get_logger",
    "load_env",
    "reduce_promises",
    "reduce_self_claims",
]
