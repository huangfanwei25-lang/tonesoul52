"""Aegis Shield — Memory integrity layer for ToneSoul.

Three defenses against the dark forest:

1. Hash Chain       — every trace links to the previous via SHA-256.
                      Tampering any historical entry breaks the chain.
2. Agent Signing    — every commit() is Ed25519-signed by the writing agent.
                      Impersonation is detectable.
3. Content Filter   — basic prompt injection / poisoning pattern detection
                      before anything enters governance memory.

Usage:
    from tonesoul.aegis_shield import AegisShield
    shield = AegisShield.load_or_create()
    shield.verify_chain(store)      # check integrity
    shield.sign_trace(trace_dict)   # sign before commit
    shield.validate_content(text)   # filter before write

Key storage (Redis):
    ts:aegis:chain_head    — latest hash in the chain
    ts:aegis:pubkeys       — HASH of agent_id → hex public key
    ts:aegis:violations    — LIST of detected integrity violations

Key storage (File fallback):
    .aegis/chain_head.txt
    .aegis/keys/{agent_id}.pub
    .aegis/keys/{agent_id}.key  (private, gitignored)
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_AEGIS_DIR = _REPO_ROOT / ".aegis"
_KEYS_DIR = _AEGIS_DIR / "keys"

# Prompt injection / poisoning patterns (defensive, not exhaustive)
_AGENT_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def _validate_agent_id(agent_id: str) -> str:
    """Sanitize agent_id to prevent path traversal attacks."""
    if not agent_id or not _AGENT_ID_RE.match(agent_id):
        raise ValueError(f"Invalid agent_id: must match [a-zA-Z0-9_-]+, got {agent_id!r}")
    return agent_id


_POISON_PATTERNS: List[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.I),
    re.compile(r"disregard\s+(all\s+)?prior\s+(context|instructions?)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"<\s*system\s*>", re.I),
    re.compile(r"\\x[0-9a-f]{2}", re.I),  # hex escape smuggling
    re.compile(r"IMPORTANT:\s*override", re.I),
    re.compile(r"forget\s+(everything|all|your)", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
    re.compile(r"act\s+as\s+if\s+you\s+(are|were)", re.I),
    re.compile(r"pretend\s+(that\s+)?you", re.I),
    re.compile(r"do\s+not\s+follow\s+(the\s+)?(rules|instructions|guidelines)", re.I),
]

# Max field lengths to prevent memory bloat
_MAX_FIELD_LENGTHS: Dict[str, int] = {
    "session_id": 128,
    "agent": 64,
    "timestamp": 64,
    "topics": 50,  # max items
    "key_decisions": 20,
    "tension_events": 50,
    "vow_events": 20,
}


# ---------------------------------------------------------------------------
# Hash chain
# ---------------------------------------------------------------------------


def compute_hash(data: str, prev_hash: str = "") -> str:
    """SHA-256 of content + previous hash → chain link."""
    payload = f"{prev_hash}|{data}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_chain_entry(trace_dict: Dict[str, Any], prev_hash: str) -> Dict[str, Any]:
    """Add chain metadata to a trace dict before storage."""
    hashable = {k: v for k, v in trace_dict.items() if k not in ("_chain", "_signature")}
    content = json.dumps(hashable, sort_keys=True, ensure_ascii=False)
    entry_hash = compute_hash(content, prev_hash)
    trace_dict["_chain"] = {
        "prev_hash": prev_hash,
        "hash": entry_hash,
        "timestamp": time.time(),
    }
    return trace_dict


def verify_chain(traces: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Walk the chain, return (valid, list_of_errors)."""
    errors: List[str] = []
    expected_prev = ""

    for i, trace in enumerate(traces):
        chain = trace.get("_chain")
        if chain is None:
            # Legacy entry without chain — skip but note
            continue

        if chain.get("prev_hash", "") != expected_prev:
            errors.append(
                f"Entry {i}: prev_hash mismatch. "
                f"Expected {expected_prev[:16]}…, got {chain.get('prev_hash', '')[:16]}…"
            )

        # Recompute hash to verify content integrity
        # Exclude both _chain and _signature — signature is added after hashing
        trace_copy = {k: v for k, v in trace.items() if k not in ("_chain", "_signature")}
        content = json.dumps(trace_copy, sort_keys=True, ensure_ascii=False)
        recomputed = compute_hash(content, chain.get("prev_hash", ""))
        if recomputed != chain.get("hash", ""):
            errors.append(f"Entry {i}: content hash mismatch — trace was tampered.")

        expected_prev = chain.get("hash", "")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Agent identity (Ed25519)
# ---------------------------------------------------------------------------


def _ensure_keys_dir() -> Path:
    _KEYS_DIR.mkdir(parents=True, exist_ok=True)
    # Ensure .aegis/keys/ is gitignored (private keys live here)
    gitignore = _AEGIS_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("keys/*.key\n", encoding="utf-8")
    return _KEYS_DIR


def generate_agent_keys(agent_id: str) -> Tuple[str, str]:
    """Generate Ed25519 keypair for an agent. Returns (public_hex, private_hex)."""
    _validate_agent_id(agent_id)
    from nacl.signing import SigningKey

    sk = SigningKey.generate()
    vk = sk.verify_key

    keys_dir = _ensure_keys_dir()
    (keys_dir / f"{agent_id}.key").write_text(sk.encode().hex(), encoding="utf-8")
    (keys_dir / f"{agent_id}.pub").write_text(vk.encode().hex(), encoding="utf-8")

    return vk.encode().hex(), sk.encode().hex()


def load_signing_key(agent_id: str) -> Optional[Any]:
    """Load private key for signing. Returns SigningKey or None."""
    _validate_agent_id(agent_id)
    key_file = _KEYS_DIR / f"{agent_id}.key"
    if not key_file.exists():
        return None
    try:
        from nacl.signing import SigningKey

        hex_key = key_file.read_text(encoding="utf-8").strip()
        return SigningKey(bytes.fromhex(hex_key))
    except Exception:
        return None


def load_verify_key(agent_id: str) -> Optional[Any]:
    """Load public key for verification. Returns VerifyKey or None."""
    _validate_agent_id(agent_id)
    pub_file = _KEYS_DIR / f"{agent_id}.pub"
    if not pub_file.exists():
        return None
    try:
        from nacl.signing import VerifyKey

        hex_key = pub_file.read_text(encoding="utf-8").strip()
        return VerifyKey(bytes.fromhex(hex_key))
    except Exception:
        return None


def sign_trace(trace_dict: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
    """Sign a trace with the agent's Ed25519 private key.

    If the agent already has a registered public key but no private key
    on this machine, signing is refused to prevent impersonation.
    """
    sk = load_signing_key(agent_id)
    if sk is None:
        existing_pub = load_verify_key(agent_id)
        if existing_pub is not None:
            # Public key exists but no private key — possible impersonation
            trace_dict["_signature"] = {
                "agent": agent_id,
                "error": "pubkey_exists_no_private_key",
            }
            return trace_dict
        # Genuinely new agent — auto-generate keys
        generate_agent_keys(agent_id)
        sk = load_signing_key(agent_id)
    if sk is None:
        trace_dict["_signature"] = {"agent": agent_id, "error": "no_key"}
        return trace_dict

    # Sign the content (excluding existing signature)
    content = json.dumps(
        {k: v for k, v in trace_dict.items() if k not in ("_signature", "_chain")},
        sort_keys=True,
        ensure_ascii=False,
    )
    signed = sk.sign(content.encode("utf-8"))

    trace_dict["_signature"] = {
        "agent": agent_id,
        "sig": signed.signature.hex(),
        "pubkey": sk.verify_key.encode().hex(),
    }
    return trace_dict


def verify_signature(trace_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify a trace's Ed25519 signature. Returns (valid, reason)."""
    sig_info = trace_dict.get("_signature")
    if sig_info is None:
        return False, "no signature"
    if "error" in sig_info:
        return False, f"signing error: {sig_info['error']}"

    agent_id = sig_info.get("agent", "")
    sig_hex = sig_info.get("sig", "")
    pubkey_hex = sig_info.get("pubkey", "")

    if not all([agent_id, sig_hex, pubkey_hex]):
        return False, "incomplete signature fields"

    try:
        from nacl.signing import VerifyKey

        vk = VerifyKey(bytes.fromhex(pubkey_hex))
        content = json.dumps(
            {k: v for k, v in trace_dict.items() if k not in ("_signature", "_chain")},
            sort_keys=True,
            ensure_ascii=False,
        )
        vk.verify(content.encode("utf-8"), bytes.fromhex(sig_hex))

        # Cross-check: does stored pubkey match this agent's known key?
        known_vk = load_verify_key(agent_id)
        if known_vk is not None and known_vk.encode().hex() != pubkey_hex:
            return False, f"pubkey mismatch — possible impersonation of {agent_id}"

        return True, "valid"
    except Exception as e:
        return False, f"verification failed: {e}"


# ---------------------------------------------------------------------------
# Content filter (prompt injection / poisoning detection)
# ---------------------------------------------------------------------------


@dataclass
class ContentCheck:
    """Result of content validation."""

    clean: bool = True
    violations: List[str] = field(default_factory=list)
    severity: str = "safe"  # safe / warning / blocked


def validate_content(trace_dict: Dict[str, Any]) -> ContentCheck:
    """Scan a trace dict for injection patterns and structural anomalies."""
    result = ContentCheck()

    # Flatten all string values for pattern matching
    all_text = _extract_text(trace_dict)

    # Pattern matching
    for pattern in _POISON_PATTERNS:
        match = pattern.search(all_text)
        if match:
            result.violations.append(f"injection pattern: '{match.group()}'")
            result.clean = False

    # Field length limits (prevent memory bloat attacks)
    for field_name, max_len in _MAX_FIELD_LENGTHS.items():
        value = trace_dict.get(field_name)
        if isinstance(value, str) and len(value) > max_len:
            result.violations.append(f"field '{field_name}' exceeds max length {max_len}")
            result.clean = False
        elif isinstance(value, list) and len(value) > max_len:
            result.violations.append(f"field '{field_name}' has {len(value)} items (max {max_len})")
            result.clean = False

    # Anomaly: excessively long text in any single field
    for key, value in trace_dict.items():
        if isinstance(value, str) and len(value) > 10000:
            result.violations.append(f"field '{key}' is {len(value)} chars — suspicious")
            result.clean = False

    # Set severity
    if not result.clean:
        result.severity = "blocked" if len(result.violations) >= 2 else "warning"

    return result


def _extract_text(obj: Any, depth: int = 0) -> str:
    """Recursively extract all string values from a nested structure."""
    if depth > 10:
        return ""
    if isinstance(obj, str):
        return obj + " "
    if isinstance(obj, dict):
        return " ".join(_extract_text(v, depth + 1) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(_extract_text(v, depth + 1) for v in obj)
    return ""


# ---------------------------------------------------------------------------
# Integrated shield: wraps all three defenses
# ---------------------------------------------------------------------------


class AegisShield:
    """Unified defense layer — call before and after every memory write."""

    def __init__(self, chain_head: str = "") -> None:
        self.chain_head = chain_head

    @classmethod
    def load(cls, store=None) -> AegisShield:
        """Load chain head from store or file."""
        chain_head = ""

        if store is not None and store.is_redis:
            raw = store._r.get("ts:aegis:chain_head")
            if raw:
                chain_head = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        else:
            head_file = _AEGIS_DIR / "chain_head.txt"
            if head_file.exists():
                chain_head = head_file.read_text(encoding="utf-8").strip()

        return cls(chain_head=chain_head)

    def save(self, store=None) -> None:
        """Persist chain head."""
        if store is not None and store.is_redis:
            store._r.set("ts:aegis:chain_head", self.chain_head)
        else:
            _AEGIS_DIR.mkdir(parents=True, exist_ok=True)
            (_AEGIS_DIR / "chain_head.txt").write_text(self.chain_head, encoding="utf-8")

    def protect_trace(
        self,
        trace_dict: Dict[str, Any],
        agent_id: str,
    ) -> Tuple[Dict[str, Any], ContentCheck]:
        """Full protection pipeline: filter → sign → chain.

        Returns (protected_trace, content_check).
        """
        # 1. Content filter
        check = validate_content(trace_dict)
        if check.severity == "blocked":
            return trace_dict, check

        # 2. Sign
        trace_dict = sign_trace(trace_dict, agent_id)

        # 3. Chain
        trace_dict = build_chain_entry(trace_dict, self.chain_head)
        self.chain_head = trace_dict["_chain"]["hash"]

        return trace_dict, check

    def verify_trace(self, trace_dict: Dict[str, Any]) -> List[str]:
        """Verify a single trace: signature + content."""
        issues: List[str] = []

        # Signature check
        sig_valid, reason = verify_signature(trace_dict)
        if not sig_valid:
            issues.append(f"signature: {reason}")

        # Content check
        check = validate_content(trace_dict)
        if not check.clean:
            issues.extend(check.violations)

        return issues

    def audit(self, store) -> Dict[str, Any]:
        """Full audit: verify entire chain + all signatures."""
        traces = store.get_traces(n=10000)

        chain_valid, chain_errors = verify_chain(traces)
        sig_results = []
        for i, t in enumerate(traces):
            valid, reason = verify_signature(t)
            if not valid:
                sig_results.append({"entry": i, "reason": reason})

        return {
            "total_traces": len(traces),
            "chain_valid": chain_valid,
            "chain_errors": chain_errors,
            "signature_failures": sig_results,
            "integrity": "intact" if (chain_valid and not sig_results) else "compromised",
        }
