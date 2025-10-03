# app.py
import json
import os
import random
import string
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

# Optional auto-refresh: if the package isn't installed, we no-op.
try:
    from streamlit_autorefresh import st_autorefresh  # type: ignore
except Exception:
    def st_autorefresh(*args, **kwargs):
        return None

# ----------------------------
# Provider Interfaces
# ----------------------------

class TempMailProvider:
    name: str = "base"

    def generate_email(self) -> Tuple[str, Dict[str, Any]]:
        """Return (email_address, provider_state_dict)."""
        raise NotImplementedError

    def list_messages(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return a normalized list of messages: [{id, from, subject, date}, ...]"""
        raise NotImplementedError

    def read_message(self, state: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Return message details with keys: id, from, subject, date, textBody, htmlBody, attachments?"""
        raise NotImplementedError


# ---------- 1. 1secmail ----------
class OneSecMailProvider(TempMailProvider):
    name = "1secmail"
    API_BASE = "https://www.1secmail.com/api/v1/"

    def _get(self, params: Dict[str, Any], retries: int = 1, timeout: int = 10) -> Any:
        for attempt in range(retries + 1):
            resp = requests.get(self.API_BASE, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2)) + attempt
                time.sleep(wait)
                continue
            if resp.status_code == 403:
                # Surface the 403 so caller can decide to fallback
                resp.raise_for_status()
            resp.raise_for_status()
            return resp.json()

    def generate_email(self) -> Tuple[str, Dict[str, Any]]:
        data = self._get({"action": "genRandomMailbox", "count": 1})
        if not isinstance(data, list) or not data:
            raise RuntimeError("1secmail did not return a mailbox.")
        email = data[0]
        login, domain = email.split("@", 1)
        return email, {"login": login, "domain": domain}

    def list_messages(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        login, domain = state["login"], state["domain"]
        data = self._get({"action": "getMessages", "login": login, "domain": domain})
        if not isinstance(data, list):
            return []
        # Normalize
        out = []
        for m in data:
            out.append({
                "id": str(m.get("id")),
                "from": m.get("from", ""),
                "subject": m.get("subject", ""),
                "date": m.get("date", ""),  # "YYYY-MM-DD HH:MM:SS"
            })
        # newest first
        out.sort(key=lambda x: x.get("date", ""), reverse=True)
        return out

    def read_message(self, state: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        login, domain = state["login"], state["domain"]
        detail = self._get({"action": "readMessage", "login": login, "domain": domain, "id": msg_id})
        # Normalize keys to match UI expectations
        return {
            "id": str(detail.get("id")),
            "from": detail.get("from", ""),
            "subject": detail.get("subject", ""),
            "date": detail.get("date", ""),
            "textBody": detail.get("textBody") or "",
            "htmlBody": detail.get("htmlBody") or "",
            "attachments": detail.get("attachments") or [],
        }


# ---------- 2. Mail.tm ----------
class MailTmProvider(TempMailProvider):
    name = "Mail.tm"
    API_BASE = "https://api.mail.tm"

    def _get(self, path: str, token: Optional[str] = None, timeout: int = 15) -> Any:
        headers = {"Accept": "application/ld+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(self.API_BASE + path, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: Dict[str, Any], token: Optional[str] = None, timeout: int = 15) -> Any:
        headers = {"Accept": "application/ld+json", "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.post(self.API_BASE + path, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _rand_local_part(self, n: int = 10) -> str:
        alphabet = string.ascii_lowercase + string.digits
        return "".join(random.choice(alphabet) for _ in range(n))

    def _get_domain(self) -> str:
        # Pick first available domain
        data = self._get("/domains?page=1")
        members = data.get("hydra:member", [])
        if not members:
            raise RuntimeError("Mail.tm returned no domains.")
        return members[0].get("domain")

    def _create_account_and_token(self) -> Tuple[str, str]:
        domain = self._get_domain()
        address = f"{self._rand_local_part()}@{domain}"
        password = self._rand_local_part(14)
        # Create account
        self._post("/accounts", {"address": address, "password": password})
        # Get token
        tok = self._post("/token", {"address": address, "password": password})
        token = tok.get("token")
        if not token:
            raise RuntimeError("Mail.tm did not return a token.")
        return address, token

    def generate_email(self) -> Tuple[str, Dict[str, Any]]:
        address, token = self._create_account_and_token()
        return address, {"token": token, "address": address}

    def list_messages(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        token = state["token"]
        data = self._get("/messages", token=token)
        members = data.get("hydra:member", [])
        out = []
        for m in members:
            sender = m.get("from", {})  # {"name":..., "address":...}
            sender_str = sender.get("address") or sender.get("name") or ""
            # receivedAt like "2025-10-03T05:12:34.000+00:00"
            out.append({
                "id": m.get("id"),
                "from": sender_str,
                "subject": m.get("subject") or "",
                "date": m.get("receivedAt") or "",
            })
        out.sort(key=lambda x: x.get("date", ""), reverse=True)
        return out

    def read_message(self, state: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        token = state["token"]
        d = self._get(f"/messages/{msg_id}", token=token)
        sender = d.get("from", {})
        return {
            "id": d.get("id"),
            "from": sender.get("address") or sender.get("name") or "",
            "subject": d.get("subject") or "",
            "date": d.get("receivedAt") or "",
            "textBody": d.get("text") or "",
            "htmlBody": d.get("html") or "",
            "attachments": d.get("attachments") or [],
        }


# ----------------------------
# Helpers & UI plumbing
# ----------------------------

def init_state():
    ss = st.session_state
    ss.setdefault("provider_name", "Mail.tm")  # default to Mail.tm to avoid 403 issues
    ss.setdefault("provider_state", {})        # token/login/domain etc
    ss.setdefault("email", None)
    ss.setdefault("cached_messages", [])
    ss.setdefault("last_fetch_ts", 0.0)
    ss.setdefault("refresh_counter", 0)

def throttle(seconds: float = 2.0) -> bool:
    now = time.time()
    last = st.session_state.get("last_fetch_ts", 0.0)
    if now - last >= seconds:
        st.session_state["last_fetch_ts"] = now
        return True
    return False

def human_time(s: str) -> str:
    if not s:
        return ""
    # Try 1secmail format
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        pass
    # Try ISO (Mail.tm)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return s

def copy_to_clipboard_button(text: str, label: str = "Copy email"):
    safe_text = json.dumps(text)
    html = f"""
    <button
      style="padding:0.45rem 0.75rem;border-radius:8px;border:1px solid #DDD;cursor:pointer"
      onclick="navigator.clipboard.writeText({safe_text}).then(()=>{{this.innerText='Copied!'; setTimeout(()=>this.innerText='{label}',1100);}})">
      {label}
    </button>
    """
    st.components.v1.html(html, height=42)

PROVIDERS: Dict[str, TempMailProvider] = {
    "Mail.tm": MailTmProvider(),
    "1secmail": OneSecMailProvider(),
}

def pick_provider(name: str) -> TempMailProvider:
    return PROVIDERS.get(name, PROVIDERS["Mail.tm"])

def show_message_detail(provider: TempMailProvider, state: Dict[str, Any], meta: Dict[str, Any]):
    subj = meta.get("subject") or "(no subject)"
    sender = meta.get("from") or "(unknown)"
    when = human_time(meta.get("date", ""))
    msg_id = str(meta.get("id"))

    with st.expander(f"✉️  {subj} — {sender} • {when}"):
        with st.spinner("Opening…"):
            try:
                d = provider.read_message(state, msg_id)
            except requests.HTTPError as e:
                st.error(f"Failed to load message: {e}")
                return
            except requests.RequestException as e:
                st.error(f"Network error: {e}")
                return

        st.write(f"**From:** {d.get('from','')}")
        st.write(f"**Subject:** {d.get('subject','')}")
        st.write(f"**Date:** {human_time(d.get('date',''))}")

        text_body = d.get("textBody") or ""
        html_body = d.get("htmlBody") or ""
        if text_body.strip():
            st.markdown("**Body (text):**")
            st.text(text_body)
        elif html_body.strip():
            st.markdown("**Body (HTML, raw):**")
            st.code(html_body, language="html")
        else:
            st.info("No body content found.")

        atts = d.get("attachments") or []
        if atts:
            st.markdown("**Attachments:**")
            for a in atts:
                name = a.get("filename") or a.get("name") or "(attachment)"
                st.write(f"• {name}")

# ----------------------------
# Streamlit App
# ----------------------------
st.set_page_config(page_title="📮 Temp Mail", page_icon="📮", layout="centered")
init_state()

st.title("📮 Temporary Email — Streamlit")
st.caption("Generate a burner email and read incoming messages. Supports Mail.tm (default) and 1secmail.")

# Sidebar: provider choice
with st.sidebar:
    st.subheader("Provider")
    chosen = st.selectbox("Service", options=list(PROVIDERS.keys()), index=list(PROVIDERS.keys()).index(st.session_state["provider_name"]))
    if chosen != st.session_state["provider_name"]:
        st.session_state["provider_name"] = chosen
        st.session_state["provider_state"] = {}
        st.session_state["email"] = None
        st.session_state["cached_messages"] = []
        st.session_state["last_fetch_ts"] = 0.0

provider = pick_provider(st.session_state["provider_name"])

# Top controls
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    if st.button("✨ Generate new address", type="primary"):
        with st.spinner("Creating mailbox…"):
            try:
                email, state = provider.generate_email()
                st.session_state["email"] = email
                st.session_state["provider_state"] = state
                st.session_state["cached_messages"] = []
                st.session_state["last_fetch_ts"] = 0.0
            except requests.HTTPError as e:
                # If 1secmail throws 403, auto-fallback to Mail.tm
                if provider.name == "1secmail" and e.response is not None and e.response.status_code == 403:
                    st.warning("1secmail returned 403. Falling back to Mail.tm automatically.")
                    backup = PROVIDERS["Mail.tm"]
                    try:
                        email, state = backup.generate_email()
                        st.session_state["provider_name"] = backup.name
                        st.session_state["email"] = email
                        st.session_state["provider_state"] = state
                    except Exception as e2:
                        st.error(f"Fallback also failed: {e2}")
                else:
                    st.error(f"API error: {e}")
            except Exception as e:
                st.error(f"Failed to generate email: {e}")

with c2:
    if st.button("🔄 Refresh inbox"):
        st.session_state["refresh_counter"] += 1
        st.session_state["last_fetch_ts"] = 0.0

with c3:
    auto = st.toggle("Auto-refresh", value=False, help="Poll the inbox periodically")
    interval = st.slider("Every (seconds)", 3, 30, 8, disabled=not auto)
    if auto:
        st_autorefresh(interval=interval * 1000, key="auto_refresh_tick")

st.divider()

if not st.session_state["email"]:
    st.info("Click **Generate new address** to get started.")
    st.stop()

st.subheader("Current address")
col_a, col_b = st.columns([5, 1])
with col_a:
    st.text_input("Your temporary email", value=st.session_state["email"], disabled=True, label_visibility="collapsed")
with col_b:
    copy_to_clipboard_button(st.session_state["email"])

# Inbox
allow = throttle(2.0)
if allow:
    with st.spinner("Checking for new mail…"):
        try:
            msgs = provider.list_messages(st.session_state["provider_state"])
            st.session_state["cached_messages"] = msgs
        except requests.HTTPError as e:
            st.error(f"Inbox error: {e}")
            msgs = st.session_state.get("cached_messages", [])
        except requests.RequestException as e:
            st.error(f"Network error: {e}")
            msgs = st.session_state.get("cached_messages", [])
else:
    msgs = st.session_state.get("cached_messages", [])

st.subheader("Inbox")
if not msgs:
    st.write("📭 No messages yet. Send an email here and refresh.")
else:
    summary = [
        {
            "ID": m.get("id"),
            "From": m.get("from", ""),
            "Subject": m.get("subject", ""),
            "Received": human_time(m.get("date", "")),
        }
        for m in msgs
    ]
    st.dataframe(summary, use_container_width=True, hide_index=True)
    for m in msgs:
        show_message_detail(provider, st.session_state["provider_state"], m)

st.caption(
    "Note: Disposable inboxes are public/ephemeral and may be rate-limited or purged. "
    "Don’t use them for anything sensitive."
)
