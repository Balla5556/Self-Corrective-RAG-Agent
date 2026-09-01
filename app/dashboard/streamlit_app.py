from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from app.observability.audit import AuditLedger

st.set_page_config(page_title="Sentinel Gateway Ops", page_icon="🛡️", layout="wide")
st.title("🛡️ Sentinel Gateway Operations")
st.caption(
    "Privacy-preserving audit events — raw prompt and response content is intentionally unavailable."
)
ledger = AuditLedger(os.getenv("SENTINEL_DATABASE_PATH", "./data/sentinel.db"))
events = ledger.recent()
if not events:
    st.info("No requests recorded yet. Send a request to the gateway, then refresh this page.")
    st.stop()
data = pd.DataFrame(events)
allowed = int((data.decision == "allowed").sum())
blocked = int((data.decision == "blocked").sum())
redactions = int(data.pii_count.sum())
cost = float(data.estimated_cost_usd.sum())
columns = st.columns(4)
columns[0].metric("Allowed", allowed)
columns[1].metric("Blocked", blocked)
columns[2].metric("PII values redacted", redactions)
columns[3].metric("Estimated cost", f"${cost:.4f}")
st.subheader("Policy decisions")
st.bar_chart(data.decision.value_counts())
st.subheader("Recent audit events")
st.dataframe(data, use_container_width=True, hide_index=True)
