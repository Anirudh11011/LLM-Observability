import streamlit as st
import os
import pandas as pd
import altair as alt

st.set_page_config(page_title="LLM Observability Dashboard", layout="wide")

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))

# --- Custom CSS for yellow-accented tables and teal card styling ---
st.html("""
<style>
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d3b3e 0%, #112240 100%);
    border: 1px solid #10c3c9;
    border-radius: 12px;
    padding: 16px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #10c3c9;
    border-radius: 8px;
}
thead tr th {
    background-color: #f5c842 !important;
    color: #0a1628 !important;
}
</style>
""")

st.markdown("## LLM Observability Dashboard")
st.markdown("---")


@st.cache_data
def load_total_records():
    return conn.query(
        "SELECT COUNT(*) AS TOTAL_RECORDS FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES"
    )


@st.cache_data
def load_avg_token_by_lang():
    return conn.query("""
        SELECT LANG, ROUND(AVG(TOKEN_USAGE), 2) AS AVG_TOKEN_USAGE
        FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGES
        GROUP BY LANG
        ORDER BY AVG_TOKEN_USAGE DESC
    """)


@st.cache_data
def load_label_averages():
    return conn.query("""
        SELECT
            ROUND(AVG(SPAM), 4) AS AVG_SPAM,
            ROUND(AVG(QUALITY), 4) AS AVG_QUALITY,
            ROUND(AVG(TOXICITY), 4) AS AVG_TOXICITY,
            ROUND(AVG(PII), 4) AS AVG_PII
        FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_MESSAGE_LABELS
    """)


with st.spinner("Loading data..."):
    total_df = load_total_records()
    token_lang_df = load_avg_token_by_lang()
    labels_df = load_label_averages()

# --- KPI Row ---
total_records = int(total_df["TOTAL_RECORDS"].iloc[0])

with st.container(horizontal=True):
    st.metric("Total Records", f"{total_records:,}", border=True)
    st.metric("Languages Tracked", str(len(token_lang_df)), border=True)
    st.metric("Avg Spam Score", f"{labels_df['AVG_SPAM'].iloc[0] * 100:.2f}%", border=True)
    st.metric("Avg Quality Score", f"{labels_df['AVG_QUALITY'].iloc[0] * 100:.2f}%", border=True)

st.markdown("---")

# --- Average Token Usage by Language ---
st.markdown("### Average Token Usage by Language")

col1, col2 = st.columns([2, 3])

with col1:
    st.dataframe(token_lang_df, hide_index=True, use_container_width=True)

with col2:
    chart_df = token_lang_df.copy()
    chart_df["AVG_TOKEN_USAGE"] = chart_df["AVG_TOKEN_USAGE"].astype(float)
    lang_order = chart_df["LANG"].tolist()
    token_bar = alt.Chart(chart_df).mark_bar(cornerRadiusEnd=6).encode(
        y=alt.Y("LANG:N", sort=lang_order, title="Language"),
        x=alt.X("AVG_TOKEN_USAGE:Q", title="Avg Token Usage"),
        color=alt.Color("AVG_TOKEN_USAGE:Q", scale=alt.Scale(
            range=["#234a23","#2ded2d"]
        ), legend=None),
        tooltip=["LANG", "AVG_TOKEN_USAGE"]
    ).properties(height=600)
    text = token_bar.mark_text(align="left", dx=4, color="#e6f1f").encode(
        text=alt.Text("AVG_TOKEN_USAGE:Q", format=".1f")
    )
    st.altair_chart(token_bar + text, use_container_width=True)

st.markdown("---")

# --- Message Label Averages ---
st.markdown("### Chat Governance")

label_cols = st.columns(4, border=True)
metrics = [
    ("Avg Spam", labels_df["AVG_SPAM"].iloc[0] * 100),
    ("Avg Quality", labels_df["AVG_QUALITY"].iloc[0] * 100),
    ("Avg Toxicity", labels_df["AVG_TOXICITY"].iloc[0] * 100),
    ("Avg PII", labels_df["AVG_PII"].iloc[0] * 100),
]

for col, (name, val) in zip(label_cols, metrics):
    with col:
        st.metric(name, f"{val:.2f}%")

# Horizontal bar chart of label averages (against 100% scale)
labels_chart_df = pd.DataFrame({
    "Label": ["Spam", "Quality", "Toxicity", "PII"],
    "Average (%)": [
        labels_df["AVG_SPAM"].iloc[0] * 100,
        labels_df["AVG_QUALITY"].iloc[0] * 100,
        labels_df["AVG_TOXICITY"].iloc[0] * 100,
        labels_df["AVG_PII"].iloc[0] * 100,
    ]
})

labels_bar = alt.Chart(labels_chart_df).mark_bar(cornerRadiusEnd=8, size=28).encode(
    y=alt.Y("Label:N", title=None, sort=["Spam", "Quality", "Toxicity", "PII"]),
    x=alt.X("Average (%):Q", scale=alt.Scale(domain=[0, 100]), title="Score (%)"),
    color=alt.Color("Label:N", scale=alt.Scale(
        domain=["Spam", "Quality", "Toxicity", "PII"],
        range=["#f5c842", "#10c3c9", "#ff6b6b", "#a78bfa"]
    ), legend=None),
    tooltip=["Label", alt.Tooltip("Average (%):Q", format=".2f")]
).properties(height=220)

labels_text = labels_bar.mark_text(align="left", dx=4, color="#e6f1ff", fontSize=13).encode(
    text=alt.Text("Average (%):Q", format=".2f")
)

st.altair_chart(labels_bar + labels_text, use_container_width=True)

# --- Conversation Tree ---
st.markdown("### Conversation Tree")


@st.cache_data
def load_conversation_stats():
    return conn.query("""
        SELECT
            COUNT(*) AS TOTAL_ROOT_CONVERSATIONS,
            ROUND(AVG(CONVERSATION_LENGTH), 2) AS AVG_CONVERSATION_LENGTH,
            ROUND(AVG(CONVERSATION_DEPTH), 2) AS AVG_CONVERSATION_DEPTH,
            MAX(CONVERSATION_LENGTH) AS MAX_CONVERSATION_LENGTH,
            MAX(CONVERSATION_DEPTH) AS MAX_CONVERSATION_DEPTH
        FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_CONVERSATIONS
    """)


@st.cache_data
def load_max_length_conversation():
    return conn.query("""
        SELECT CONVERSATION_ID, CONVERSATION_LENGTH
        FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_CONVERSATIONS
        ORDER BY CONVERSATION_LENGTH DESC
        LIMIT 1
    """)


@st.cache_data
def load_max_depth_conversation():
    return conn.query("""
        SELECT CONVERSATION_ID, CONVERSATION_DEPTH
        FROM AI_OBSERVABILITY_DB.TRANSFORM.FACT_CONVERSATIONS
        ORDER BY CONVERSATION_DEPTH DESC
        LIMIT 1
    """)


with st.spinner("Loading conversation data..."):
    conv_stats_df = load_conversation_stats()
    max_len_df = load_max_length_conversation()
    max_depth_df = load_max_depth_conversation()

with st.container(horizontal=True):
    st.metric("Total Root Conversations", f"{int(conv_stats_df['TOTAL_ROOT_CONVERSATIONS'].iloc[0]):,}", border=True)
    st.metric("Avg Conversation Length", f"{conv_stats_df['AVG_CONVERSATION_LENGTH'].iloc[0]}", border=True)
    st.metric("Avg Conversation Depth", f"{conv_stats_df['AVG_CONVERSATION_DEPTH'].iloc[0]}", border=True)

st.markdown("#### Highest Conversation Length & Depth")

col_a, col_b = st.columns(2, border=True)

with col_a:
    st.markdown("**Longest Conversation**")
    st.metric("Length", int(max_len_df["CONVERSATION_LENGTH"].iloc[0]))
    st.code(f"ID: {max_len_df['CONVERSATION_ID'].iloc[0]}", language=None)

with col_b:
    st.markdown("**Deepest Conversation**")
    st.metric("Depth", int(max_depth_df["CONVERSATION_DEPTH"].iloc[0]))
    st.code(f"ID: {max_depth_df['CONVERSATION_ID'].iloc[0]}", language=None)

# --- Refresh button ---
st.markdown("---")
if st.button("Refresh Data"):
    load_total_records.clear()
    load_avg_token_by_lang.clear()
    load_label_averages.clear()
    load_conversation_stats.clear()
    load_max_length_conversation.clear()
    load_max_depth_conversation.clear()
    st.rerun()
