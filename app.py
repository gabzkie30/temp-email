import json
import os
import random
import re
import string
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

# Optional auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    def st_autorefresh(*args, **kwargs):
        return None

# ----------------------------
# Custom CSS Styling
# ----------------------------
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom card styling */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Header styling */
    .app-header {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 0;
    }
    
    /* Email display card */
    .email-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .email-label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .email-value {
        font-size: 1.5rem;
        font-weight: 600;
        word-break: break-all;
        font-family: 'Courier New', monospace;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Message cards */
    .message-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .message-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateX(4px);
    }
    
    .message-unread {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .message-from {
        font-weight: 600;
        color: #1f2937;
        font-size: 1rem;
    }
    
    .message-date {
        color: #6b7280;
        font-size: 0.85rem;
    }
    
    .message-subject {
        font-size: 1.1rem;
        color: #374151;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-new {
        background: #10b981;
        color: white;
    }
    
    .badge-provider {
        background: #667eea;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        padding: 0.5rem 1.5rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Search box */
    .search-box {
        background: white;
        border-radius: 10px;
        padding: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background: #10b981;
    }
    
    .status-offline {
        background: #ef4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #6b7280;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------
# Provider Interfaces
# ----------------------------

class TempMailProvider:
    name: str = "base"

    def generate_email(self) -> Tuple[str, Dict[str, Any]]:
        raise NotImplementedError

    def list_messages(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def read_message(self, state: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        raise NotImplementedError


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
        out = []
        for m in data:
            out.append({
                "id": str(m.get("id")),
                "from": m.get("from", ""),
                "subject": m.get("subject", ""),
                "date": m.get("date", ""),
            })
        out.sort(key=lambda x: x.get("date", ""), reverse=True)
        return out

    def read_message(self, state: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        login, domain = state["login"], state["domain"]
        detail = self._get({"action": "readMessage", "login": login, "domain": domain, "id": msg_id})
        return {
            "id": str(detail.get("id")),
            "from": detail.get("from", ""),
            "subject": detail.get("subject", ""),
            "date": detail.get("date", ""),
            "textBody": detail.get("textBody") or "",
            "htmlBody": detail.get("htmlBody") or "",
            "attachments": detail.get("attachments") or [],
        }


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
        data = self._get("/domains?page=1")
        members = data.get("hydra:member", [])
        if not members:
            raise RuntimeError("Mail.tm returned no domains.")
        return members[0].get("domain")

    def _create_account_and_token(self) -> Tuple[str, str]:
        domain = self._get_domain()
        address = f"{self._rand_local_part()}@{domain}"
        password = self._rand_local_part(14)
        self._post("/accounts", {"address": address, "password": password})
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
            sender = m.get("from", {})
            sender_str = sender.get("address") or sender.get("name") or ""
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
# Helpers
# ----------------------------

PROVIDERS: Dict[str, TempMailProvider] = {
    "Mail.tm": MailTmProvider(),
    "1secmail": OneSecMailProvider(),
}

def init_state():
    ss = st.session_state
    ss.setdefault("provider_name", "Mail.tm")
    ss.setdefault("provider_state", {})
    ss.setdefault("email", None)
    ss.setdefault("cached_messages", [])
    ss.setdefault("last_fetch_ts", 0.0)
    ss.setdefault("refresh_counter", 0)
    ss.setdefault("read_messages", set())
    ss.setdefault("search_query", "")
    ss.setdefault("connection_status", "online")
    ss.setdefault("email_created_at", None)

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
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return s

def time_ago(s: str) -> str:
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return s
    
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"

def copy_button_html(text: str, button_id: str = "copy-btn") -> str:
    safe_text = text.replace("'", "\\'")
    unique_id = f"{button_id}_{hash(text) % 10000}"
    return f"""
    <div style="margin-top: 8px;">
        <button id="{unique_id}" style="
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            width: 100%;
        " onmouseover="
            if(!this.classList.contains('copied')) {{
                this.style.background = '#667eea';
                this.style.color = 'white';
            }}
        " onmouseout="
            if(!this.classList.contains('copied')) {{
                this.style.background = 'white';
                this.style.color = '#667eea';
            }}
        ">
            📋 Copy Email
        </button>
    </div>
    <script>
        (function() {{
            const btn = document.getElementById('{unique_id}');
            if(btn) {{
                btn.addEventListener('click', function() {{
                    const textToCopy = '{safe_text}';
                    
                    // Try modern clipboard API first
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(textToCopy).then(() => {{
                            btn.innerHTML = '✓ Copied!';
                            btn.style.background = '#10b981';
                            btn.style.borderColor = '#10b981';
                            btn.style.color = 'white';
                            btn.classList.add('copied');
                            
                            setTimeout(() => {{
                                btn.innerHTML = '📋 Copy Email';
                                btn.style.background = 'white';
                                btn.style.borderColor = '#667eea';
                                btn.style.color = '#667eea';
                                btn.classList.remove('copied');
                            }}, 2000);
                        }}).catch(err => {{
                            console.error('Clipboard error:', err);
                            fallbackCopy(textToCopy);
                        }});
                    }} else {{
                        fallbackCopy(textToCopy);
                    }}
                }});
            }}
            
            function fallbackCopy(text) {{
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {{
                    document.execCommand('copy');
                    const btn = document.getElementById('{unique_id}');
                    btn.innerHTML = '✓ Copied!';
                    btn.style.background = '#10b981';
                    btn.style.borderColor = '#10b981';
                    btn.style.color = 'white';
                    btn.classList.add('copied');
                    
                    setTimeout(() => {{
                        btn.innerHTML = '📋 Copy Email';
                        btn.style.background = 'white';
                        btn.style.borderColor = '#667eea';
                        btn.style.color = '#667eea';
                        btn.classList.remove('copied');
                    }}, 2000);
                }} catch (err) {{
                    alert('Copy failed. Please copy manually: ' + text);
                }}
                
                document.body.removeChild(textArea);
            }}
        }})();
    </script>
    """

def pick_provider(name: str) -> TempMailProvider:
    return PROVIDERS.get(name, PROVIDERS["Mail.tm"])

def filter_messages(messages: List[Dict], query: str) -> List[Dict]:
    if not query:
        return messages
    query = query.lower()
    return [
        m for m in messages
        if query in m.get("from", "").lower()
        or query in m.get("subject", "").lower()
    ]

# ----------------------------
# UI Components
# ----------------------------

def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📮 Temp Mail Pro</div>
        <div class="app-subtitle">
            Secure, disposable email addresses for testing and privacy
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stats():
    msgs = st.session_state.get("cached_messages", [])
    unread = len([m for m in msgs if m.get("id") not in st.session_state.get("read_messages", set())])
    
    created_at = st.session_state.get("email_created_at")
    if created_at:
        lifetime = datetime.now() - created_at
        lifetime_str = f"{lifetime.seconds // 60}m"
    else:
        lifetime_str = "N/A"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(msgs)}</div>
            <div class="stat-label">Total Messages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{unread}</div>
            <div class="stat-label">Unread</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.get('provider_name', 'N/A')}</div>
            <div class="stat-label">Provider</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{lifetime_str}</div>
            <div class="stat-label">Lifetime</div>
        </div>
        """, unsafe_allow_html=True)

def render_email_display():
    email = st.session_state.get("email")
    if not email:
        return
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class="email-display">
            <div class="email-label">Your Temporary Email Address</div>
            <div class="email-value">{email}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.components.v1.html(copy_button_html(email), height=60)

def render_message_card(msg: Dict, provider: TempMailProvider, state: Dict):
    msg_id = str(msg.get("id"))
    is_unread = msg_id not in st.session_state.get("read_messages", set())
    
    subj = msg.get("subject") or "(no subject)"
    sender = msg.get("from") or "(unknown)"
    date_str = msg.get("date", "")
    
    card_class = "message-card message-unread" if is_unread else "message-card"
    
    with st.expander(f"{'🆕 ' if is_unread else ''}**{subj}**", expanded=False):
        # Mark as read when expanded
        if is_unread:
            st.session_state["read_messages"].add(msg_id)
        
        col_info, col_time = st.columns([3, 1])
        with col_info:
            st.markdown(f"**From:** {sender}")
        with col_time:
            st.caption(f"🕐 {time_ago(date_str)}")
        
        st.divider()
        
        with st.spinner("Loading message..."):
            try:
                d = provider.read_message(state, msg_id)
            except Exception as e:
                st.error(f"❌ Failed to load message: {e}")
                return
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📄 Text", "🌐 HTML", "📎 Details"])
        
        with tab1:
            text_body = d.get("textBody") or ""
            if text_body.strip():
                st.text_area("Message Content", text_body, height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("No text content available")
        
        with tab2:
            html_body = d.get("htmlBody") or ""
            if html_body.strip():
                st.code(html_body, language="html", line_numbers=True)
            else:
                st.info("No HTML content available")
        
        with tab3:
            st.markdown(f"""
            **Message ID:** `{d.get('id', 'N/A')}`  
            **From:** {d.get('from', 'N/A')}  
            **Subject:** {d.get('subject', 'N/A')}  
            **Date:** {human_time(d.get('date', ''))}
            """)
            
            atts = d.get("attachments") or []
            if atts:
                st.markdown("**Attachments:**")
                for a in atts:
                    name = a.get("filename") or a.get("name") or "(attachment)"
                    size = a.get("size", "Unknown size")
                    st.markdown(f"📎 {name} ({size})")
            else:
                st.caption("No attachments")

# ----------------------------
# Main App
# ----------------------------

st.set_page_config(
    page_title="📮 Temp Mail Pro",
    page_icon="📮",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()
init_state()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Provider selection
    st.markdown("**Email Provider**")
    chosen = st.selectbox(
        "Service",
        options=list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(st.session_state["provider_name"]),
        label_visibility="collapsed"
    )
    
    if chosen != st.session_state["provider_name"]:
        st.session_state["provider_name"] = chosen
        st.session_state["provider_state"] = {}
        st.session_state["email"] = None
        st.session_state["cached_messages"] = []
        st.session_state["last_fetch_ts"] = 0.0
        st.session_state["read_messages"] = set()
        st.rerun()
    
    st.divider()
    
    # Auto-refresh settings
    st.markdown("**Auto-Refresh**")
    auto = st.toggle("Enable auto-refresh", value=False)
    if auto:
        interval = st.slider("Refresh interval (seconds)", 5, 60, 15)
        st_autorefresh(interval=interval * 1000, key="auto_refresh")
    
    st.divider()
    
    # Connection status
    status = st.session_state.get("connection_status", "online")
    status_color = "status-online" if status == "online" else "status-offline"
    st.markdown(f"""
    <div style="padding: 1rem; background: #f3f4f6; border-radius: 8px;">
        <span class="status-indicator {status_color}"></span>
        <span style="font-weight: 600;">Status: {status.title()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Info
    st.markdown("""
    ### ℹ️ About
    
    **Temp Mail Pro** provides disposable email addresses for:
    - Testing applications
    - Avoiding spam
    - Protecting privacy
    - Quick sign-ups
    
    ⚠️ **Note:** Messages are public and temporary. Never use for sensitive data.
    """)
    
    st.caption("Made with ❤️ using Streamlit")

# Main content
provider = pick_provider(st.session_state["provider_name"])

render_header()

# Action buttons
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    if st.button("✨ Generate New Email", type="primary", use_container_width=True):
        with st.spinner("🔄 Creating your mailbox..."):
            try:
                email, state = provider.generate_email()
                st.session_state["email"] = email
                st.session_state["provider_state"] = state
                st.session_state["cached_messages"] = []
                st.session_state["last_fetch_ts"] = 0.0
                st.session_state["read_messages"] = set()
                st.session_state["email_created_at"] = datetime.now()
                st.success("✅ Email address created successfully!")
                time.sleep(0.5)
                st.rerun()
            except requests.HTTPError as e:
                if provider.name == "1secmail" and e.response and e.response.status_code == 403:
                    st.warning("⚠️ 1secmail unavailable. Switching to Mail.tm...")
                    backup = PROVIDERS["Mail.tm"]
                    try:
                        email, state = backup.generate_email()
                        st.session_state["provider_name"] = backup.name
                        st.session_state["email"] = email
                        st.session_state["provider_state"] = state
                        st.session_state["email_created_at"] = datetime.now()
                        st.success("✅ Switched to Mail.tm successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e2:
                        st.error(f"❌ Fallback failed: {e2}")
                else:
                    st.error(f"❌ API error: {e}")
            except Exception as e:
                st.error(f"❌ Failed to generate email: {e}")
                st.session_state["connection_status"] = "offline"

with col2:
    if st.button("🔄 Refresh Inbox", use_container_width=True):
        st.session_state["refresh_counter"] += 1
        st.session_state["last_fetch_ts"] = 0.0
        st.rerun()

with col3:
    if st.session_state.get("email"):
        last_refresh = st.session_state.get("last_fetch_ts", 0)
        if last_refresh > 0:
            seconds_ago = int(time.time() - last_refresh)
            st.caption(f"🕐 Last updated: {seconds_ago}s ago")

st.markdown("<br>", unsafe_allow_html=True)

# Email display and stats
if st.session_state.get("email"):
    render_email_display()
    st.markdown("<br>", unsafe_allow_html=True)
    render_stats()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search box
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📥 Inbox")
    
    search = st.text_input(
        "🔍 Search messages",
        placeholder="Search by sender or subject...",
        label_visibility="collapsed"
    )
    st.session_state["search_query"] = search
    
    # Fetch messages
    allow = throttle(2.0)
    if allow:
        with st.spinner("📬 Checking for new messages..."):
            try:
                msgs = provider.list_messages(st.session_state["provider_state"])
                st.session_state["cached_messages"] = msgs
                st.session_state["connection_status"] = "online"
            except Exception as e:
                st.error(f"❌ Error fetching messages: {e}")
                st.session_state["connection_status"] = "offline"
                msgs = st.session_state.get("cached_messages", [])
    else:
        msgs = st.session_state.get("cached_messages", [])
    
    # Filter messages
    filtered_msgs = filter_messages(msgs, st.session_state.get("search_query", ""))
    
    # Display messages
    if not filtered_msgs:
        if st.session_state.get("search_query"):
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No matching messages</h3>
                <p>Try a different search term</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3>No messages yet</h3>
                <p>Send an email to your temporary address and it will appear here</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption(f"Showing {len(filtered_msgs)} message(s)")
        for msg in filtered_msgs:
            render_message_card(msg, provider, st.session_state["provider_state"])
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Empty state - no email generated yet
    st.markdown("""
    <div class="custom-card">
        <div class="empty-state">
            <div class="empty-state-icon">📮</div>
            <h2>Get Started</h2>
            <p style="font-size: 1.1rem; margin-bottom: 2rem;">
                Click "Generate New Email" above to create your temporary email address
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <h3>🚀 Instant Setup</h3>
            <p>Generate disposable email addresses in seconds without any registration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <h3>🔒 Privacy First</h3>
            <p>Protect your real email from spam and unwanted subscriptions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <h3>⚡ Real-time Updates</h3>
            <p>Receive and read messages instantly with auto-refresh support</p>
        </div>
        """, unsafe_allow_html=True)