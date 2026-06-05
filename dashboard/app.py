"""Streamlit DevOps Monitoring Dashboard."""

import os
import time

import pandas as pd
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "dev-secret-key")
AUTH_HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(
    page_title="DevOps Monitor",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ DevOps Monitoring Dashboard")

# ── Session state init ────────────────────────────────────────────────────────
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = []
if "mem_history" not in st.session_state:
    st.session_state.mem_history = []

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_metrics, tab_servers = st.tabs(["📊 Metrics", "🌐 Servers"])


# ── Tab 1: Metrics ────────────────────────────────────────────────────────────
with tab_metrics:
    @st.cache_data(ttl=2)
    def fetch_metrics() -> dict:
        """Fetch current metrics from the API."""
        try:
            resp = requests.get(f"{API_BASE}/metrics", timeout=3)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}

    placeholder = st.empty()

    with placeholder.container():
        data = fetch_metrics()

        if not data:
            st.error("⚠️ Cannot reach the API at " + API_BASE)
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("🔥 CPU", f"{data.get('cpu_percent', 0):.1f}%")
            col2.metric("🧠 Memory", f"{data.get('memory_percent', 0):.1f}%",
                        f"{data.get('memory_used_gb', 0):.1f} / {data.get('memory_total_gb', 0):.1f} GB")
            col3.metric("💾 Disk", f"{data.get('disk_percent', 0):.1f}%")

            # Accumulate history (max 60 points)
            st.session_state.cpu_history.append(data.get("cpu_percent", 0))
            st.session_state.mem_history.append(data.get("memory_percent", 0))
            if len(st.session_state.cpu_history) > 60:
                st.session_state.cpu_history.pop(0)
                st.session_state.mem_history.pop(0)

            chart_data = pd.DataFrame({
                "CPU %": st.session_state.cpu_history,
                "Memory %": st.session_state.mem_history,
            })
            st.subheader("Live History (last 60s)")
            st.line_chart(chart_data)

    time.sleep(2)
    st.rerun()


# ── Tab 2: Servers ────────────────────────────────────────────────────────────
with tab_servers:

    @st.cache_data(ttl=5)
    def fetch_servers() -> list:
        """Fetch the list of registered servers."""
        try:
            resp = requests.get(f"{API_BASE}/servers", timeout=3)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    st.subheader("Registered Servers")
    server_list = fetch_servers()

    if server_list:
        df = pd.DataFrame(server_list)

        def color_status(val: str) -> str:
            colors = {"UP": "background-color: #14532d; color: #86efac",
                      "DEGRADED": "background-color: #78350f; color: #fcd34d",
                      "DOWN": "background-color: #7f1d1d; color: #fca5a5"}
            return colors.get(val, "")

        styled = df.style.applymap(color_status, subset=["status"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.info("No servers registered yet.")

    st.divider()

    # Register a new server
    st.subheader("Register a Server")
    with st.form("register_form"):
        name = st.text_input("Name", placeholder="prod-web-01")
        host = st.text_input("Host", placeholder="192.168.1.10")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8000)
        submitted = st.form_submit_button("➕ Register")

        if submitted:
            if not name or not host:
                st.error("Name and host are required.")
            else:
                try:
                    resp = requests.post(
                        f"{API_BASE}/servers",
                        json={"name": name, "host": host, "port": int(port)},
                        headers=AUTH_HEADERS,
                        timeout=3,
                    )
                    if resp.status_code == 201:
                        st.success(f"✅ Server '{name}' registered!")
                        fetch_servers.clear()
                    elif resp.status_code == 403:
                        st.error("❌ Invalid API key.")
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.divider()

    # Trigger health check
    if server_list:
        st.subheader("Trigger Health Check")
        options = {f"{s['name']} ({s['host']}:{s['port']})": s["id"] for s in server_list}
        selected_label = st.selectbox("Select server", list(options.keys()))
        if st.button("🔍 Check now"):
            selected_id = options[selected_label]
            try:
                resp = requests.post(f"{API_BASE}/servers/{selected_id}/check", timeout=3)
                if resp.status_code == 200:
                    st.success(resp.json().get("message", "Check triggered."))
                    fetch_servers.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
