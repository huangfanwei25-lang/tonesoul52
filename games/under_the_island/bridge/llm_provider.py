"""llm_provider.py — Multi-provider LLM interface for the bridge server.

Supported providers
-------------------
    anthropic   Claude models via Anthropic API
                Requires: ANTHROPIC_API_KEY  |  pip install anthropic
    gemini      Gemini models via Google GenAI SDK (google.genai, not legacy google.generativeai)
                Requires: GEMINI_API_KEY     |  pip install google-genai
    auto        Resolves at runtime (see resolve_provider)

Config resolution order (lowest → highest priority)
----------------------------------------------------
    built-in default
    BRIDGE_LLM_PROVIDER / BRIDGE_LLM_MODEL  env vars
    --provider / --model  CLI flags

Environment variables
---------------------
    BRIDGE_LLM_PROVIDER     anthropic | gemini  (used by auto)
    BRIDGE_LLM_MODEL        model name override (any provider)
    ANTHROPIC_API_KEY       required for anthropic provider
    GEMINI_API_KEY          required for gemini provider

Note on google.genai vs google.generativeai
--------------------------------------------
    This file uses google.genai (pip install google-genai), not the legacy
    google.generativeai package. google.genai is Google's current recommended
    SDK. If you have only the legacy package installed, Gemini calls will fail
    with an ImportError and return a diagnostic message.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    # gemini-2.0-flash may not be available in all accounts;
    # models/gemini-flash-lite-latest is the confirmed working alias
    "gemini": "models/gemini-flash-lite-latest",
}

VALID_PROVIDERS = frozenset({"anthropic", "gemini"})


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------

def resolve_provider(requested: str) -> str:
    """Resolve 'auto' to a concrete provider name.

    Priority for auto:
      1. BRIDGE_LLM_PROVIDER env var
      2. ANTHROPIC_API_KEY present → anthropic
      3. GEMINI_API_KEY present → gemini
      4. fallback → anthropic
    """
    if requested != "auto":
        return requested.lower().strip()

    env = os.environ.get("BRIDGE_LLM_PROVIDER", "").lower().strip()
    if env in VALID_PROVIDERS:
        return env

    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    return "anthropic"


def resolve_model(provider: str, requested_model: str | None) -> str:
    """Resolve model name.

    Priority:
      1. --model CLI flag (requested_model)
      2. BRIDGE_LLM_MODEL env var
      3. DEFAULT_MODELS[provider]
    """
    if requested_model:
        return requested_model
    env = os.environ.get("BRIDGE_LLM_MODEL", "").strip()
    if env:
        return env
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["anthropic"])


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def diagnostics(provider: str, model: str) -> dict:
    """Return a structured diagnostic dict without making any API call."""
    anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    gemini_key = bool(os.environ.get("GEMINI_API_KEY"))

    issues: list[str] = []
    if provider == "anthropic" and not anthropic_key:
        issues.append("ANTHROPIC_API_KEY not set — calls will return an error string")
    if provider == "gemini" and not gemini_key:
        issues.append("GEMINI_API_KEY not set — calls will return an error string")

    pkg_ok = _check_package(provider)
    if not pkg_ok:
        pkg_name = "anthropic" if provider == "anthropic" else "google-genai"
        issues.append(f"Package not installed: pip install {pkg_name}")

    return {
        "provider": provider,
        "model": model,
        "anthropic_key_set": anthropic_key,
        "gemini_key_set": gemini_key,
        "package_ok": pkg_ok,
        "issues": issues,
        "ready": len(issues) == 0,
        "env_vars": {
            "BRIDGE_LLM_PROVIDER": os.environ.get("BRIDGE_LLM_PROVIDER", "(not set)"),
            "BRIDGE_LLM_MODEL": os.environ.get("BRIDGE_LLM_MODEL", "(not set)"),
        },
    }


def _check_package(provider: str) -> bool:
    if provider == "anthropic":
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False
    elif provider == "gemini":
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False
    return False


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def call_llm(system: str, user_message: str, provider: str, model: str) -> str:
    """Call the configured LLM provider and return the response text.

    Returns a diagnostic error string (never raises) so the bridge keeps running
    even when API credentials are missing or a quota limit is hit.
    """
    if provider == "anthropic":
        return _call_anthropic(system, user_message, model)
    elif provider == "gemini":
        return _call_gemini(system, user_message, model)
    return f"[錯誤：未知 provider '{provider}'，請用 anthropic 或 gemini]"


def _call_anthropic(system: str, user_message: str, model: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=256,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text.strip()
    except ImportError:
        return "[錯誤：pip install anthropic]"
    except Exception as e:
        _classify_error(e, "Anthropic")
        return f"[Anthropic API 錯誤：{e}]"


def _call_gemini(system: str, user_message: str, model: str) -> str:
    try:
        from google import genai
        from google.genai import types

        client = genai.Client()
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=256,
            ),
        )
        return response.text.strip()
    except ImportError:
        return "[錯誤：pip install google-genai  (注意：不是 google-generativeai)]"
    except Exception as e:
        _classify_error(e, "Gemini")
        return f"[Gemini API 錯誤：{e}]"


def _classify_error(exc: Exception, provider_name: str) -> None:
    """Log a human-readable hint for common errors (key missing, quota, etc.)."""
    msg = str(exc).lower()
    if "api_key" in msg or "authentication" in msg or "401" in msg:
        print(f"  [{provider_name}] 認證失敗：請確認 API key 已設定且有效")
    elif "quota" in msg or "429" in msg or "rate" in msg:
        print(f"  [{provider_name}] Quota / rate limit：請稍後再試或切換帳號")
    elif "billing" in msg or "payment" in msg:
        print(f"  [{provider_name}] 帳單問題：請確認帳戶已啟用 billing")
