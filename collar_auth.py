"""Shared-password gate for Collar Journey — verify against a hash only, never plaintext."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets

import streamlit as st

_PBKDF2_ITERATIONS = 260_000
_HASH_PREFIX = "pbkdf2_sha256$"


def hash_password(plaintext: str, *, iterations: int = _PBKDF2_ITERATIONS) -> str:
    """Return a storable hash for COLLAR_PASSWORD_HASH (run scripts/hash_collar_password.py)."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plaintext.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"{_HASH_PREFIX}{salt}${digest.hex()}"


def verify_password(plaintext: str, stored_hash: str) -> bool:
    if not plaintext or not stored_hash or not stored_hash.startswith(_HASH_PREFIX):
        return False
    try:
        body = stored_hash[len(_HASH_PREFIX) :]
        salt, expected_hex = body.split("$", 1)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            plaintext.encode("utf-8"),
            salt.encode("utf-8"),
            _PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(digest.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def configured_password_hash() -> str | None:
    env_val = os.environ.get("COLLAR_PASSWORD_HASH", "").strip()
    if env_val:
        return env_val
    try:
        val = st.secrets.get("COLLAR_PASSWORD_HASH", "")
        if val:
            return str(val).strip()
    except Exception:
        pass
    return None


def password_gate(app_name: str = "Collar Journey") -> None:
    """Block the app until the shared password is verified."""
    stored = configured_password_hash()
    if not stored:
        st.warning(
            "Password protection is **off** locally — set `COLLAR_PASSWORD_HASH` "
            "in your environment or `.streamlit/secrets.toml` before deploying."
        )
        return

    if st.session_state.get("_collar_authenticated"):
        return

    st.markdown(
        f"""
<div style="max-width:420px;margin:3rem auto 0;padding:0 1rem;">
  <h2 style="margin-bottom:0.25rem;">{app_name}</h2>
  <p style="color:#666;margin-bottom:1.25rem;">Enter the shared password to continue.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.form("collar_password_gate", clear_on_submit=False):
        attempt = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Unlock", type="primary", use_container_width=True)
    if submitted:
        if verify_password(attempt, stored):
            st.session_state["_collar_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()
