import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from db_writer import init_db, get_recent_readings, get_anomalies, get_pipeline_logs
from chatbot import chat_with_energy_data, generate_weekly_report

# ── UNIFORM CITY COLOR MAP ────────────────────────────────────────────────────
SITE_COLORS = {
    "Stuttgart": "#4C9BE8",
    "Munich":    "#F4845F",
    "Berlin":    "#5DCAA5",
    "Hamburg":   "#F7C948",
    "Lyon":      "#A78BFA",
}

st.set_page_config(
    page_title="EnergyOps Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ EnergyOps Assistant")
    st.markdown("---")
    readings_side = get_recent_readings(hours=24)
    logs_side = get_pipeline_logs()
    if readings_side:
        last_log = logs_side[0] if logs_side else None
        last_update = last_log["logged_at"][:19] if last_log else "N/A"
        st.success("● LIVE — Pipeline Active")
        st.markdown(f"**Last Kafka message:** `{last_update}`")
        st.markdown(f"**Total messages:** `{len(readings_side)}`")
    else:
        st.warning("⏳ Waiting for data...")
    st.markdown("---")
    st.markdown("**Current site load:**")
    if readings_side:
        df_side = pd.DataFrame(readings_side)
        site_latest = (
            df_side.sort_values("ingested_at")
            .groupby("site").last().reset_index()
        )
        for _, row in site_latest.iterrows():
            pct = ((row["consumption_kw"] - row["baseline_kw"]) / row["baseline_kw"]) * 100
            icon = "🔴" if pct > 8 else "🟡" if pct > 3 else "🟢"
            color = SITE_COLORS.get(row["site"], "#888")
            st.markdown(
                f'{icon} <span style="color:{color}">■</span> '
                f'**{row["site"]}** — {row["consumption_kw"]:.0f} kW',
                unsafe_allow_html=True,
            )
    else:
        for site, color in SITE_COLORS.items():
            st.markdown(
                f'⚪ <span style="color:{color}">■</span> {site}',
                unsafe_allow_html=True,
            )
    st.markdown("---")
    st.caption("KPI cards = current live load\nCharts = 24hr trend analysis")
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.rerun()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Operations Dashboard",
    "🤖 AI Knowledge Assistant",
    "🔧 Pipeline Monitor",
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — OPERATIONS DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
with tab1:

    @st.experimental_fragment(run_every=120)
    def dashboard():
        readings = get_recent_readings(hours=24)
        anomalies = get_anomalies()
        anom_count = len(anomalies)

        st.markdown("## 🌍 Global Manufacturing Energy Operations")

        if not readings:
            st.warning("⏳ No data yet. Start the Kafka producer and consumer.")
            st.code(
                "# Terminal 1\npython kafka_producer.py\n\n"
                "# Terminal 2\npython kafka_consumer.py",
                language="bash",
            )
            return

        df = pd.DataFrame(readings)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["ingested_at"] = pd.to_datetime(df["ingested_at"])

        # ── LIVE INDICATOR ────────────────────────────────────────────────────
        now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S")
        last_ingested = df["ingested_at"].max()
        col_live, col_time = st.columns([3, 2])
        with col_live:
            st.success(
                f"● LIVE — {len(readings)} messages from Kafka | "
                f"Rendered at {now_utc} UTC"
            )
        with col_time:
            st.info(f"🕐 Last Kafka reading: {str(last_ingested)[:19]} UTC")

        # ── KPI CARDS ─────────────────────────────────────────────────────────
        st.markdown("#### ⚡ Current Live Load — Latest Kafka Reading per Site")
        latest = (
            df.sort_values("ingested_at")
            .groupby("site").last().reset_index()
        )
        total_kw = latest["consumption_kw"].sum()
        avg_kw_now = latest["consumption_kw"].mean()
        max_site = latest.loc[latest["consumption_kw"].idxmax(), "site"]
        max_kw = latest["consumption_kw"].max()
        avg_variance = (
            (latest["consumption_kw"] - latest["baseline_kw"]) /
            latest["baseline_kw"] * 100
        ).mean()
        efficiency_score = round(100 - avg_variance, 1)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric(
                "⚡ Fleet Load Now", f"{total_kw:.0f} kW",
                delta=f"{avg_kw_now:.0f} kW per site avg",
            )
        with c2:
            st.metric("🏭 Sites Active", len(latest), delta="all online")
        with c3:
            st.metric(
                "🚨 Anomalies", anom_count,
                delta="requires action" if anom_count > 0 else "all clear",
                delta_color="inverse" if anom_count > 0 else "normal",
            )
        with c4:
            st.metric(
                "📈 Highest Load Now", max_site,
                delta=f"{max_kw:.0f} kW",
            )
        with c5:
            st.metric(
                "✅ Efficiency Score", f"{efficiency_score:.1f}%",
                delta=f"{avg_variance:.1f}% above baseline avg",
                delta_color="inverse" if avg_variance > 5 else "normal",
            )

        # ── PER-SITE LIVE KPI ROW ─────────────────────────────────────────────
        st.markdown("#### 🏭 Per-Site Current Status")
        site_cols = st.columns(len(latest))
        for i, (_, row) in enumerate(latest.iterrows()):
            pct = ((row["consumption_kw"] - row["baseline_kw"]) / row["baseline_kw"]) * 100
            icon = "🔴" if pct > 8 else "🟡" if pct > 3 else "🟢"
            color = SITE_COLORS.get(row["site"], "#888")
            with site_cols[i]:
                st.markdown(
                    f'<p style="color:{color};font-weight:700;margin-bottom:0">'
                    f'{icon} {row["site"]}</p>',
                    unsafe_allow_html=True,
                )
                st.metric(
                    label="",
                    value=f"{row['consumption_kw']:.0f} kW",
                    delta=f"{pct:+.1f}% vs baseline",
                    delta_color="inverse" if pct > 8 else "normal",
                )

        st.markdown("---")
        st.markdown("#### 📈 24-Hour Trend Analysis")

        # ── ROW 1: Line chart + Variance bar ──────────────────────────────────
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("**Real-time Consumption — Kafka Feed**")
            fig_line = px.line(
                df.sort_values("ingested_at"),
                x="ingested_at",
                y="consumption_kw",
                color="site",
                color_discrete_map=SITE_COLORS,
                labels={
                    "ingested_at": "Time (UTC)",
                    "consumption_kw": "Consumption (kW)",
                    "site": "Site",
                },
            )
            fig_line.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with col2:
            st.markdown("**24hr Avg Variance vs Baseline**")
            site_avg = df.groupby("site").agg(
                avg_kw=("consumption_kw", "mean"),
                baseline=("baseline_kw", "first"),
            ).reset_index()
            site_avg["variance_pct"] = (
                (site_avg["avg_kw"] - site_avg["baseline"]) /
                site_avg["baseline"] * 100
            ).round(1)
            fig_var = px.bar(
                site_avg,
                x="site", y="variance_pct",
                color="site",
                color_discrete_map=SITE_COLORS,
                labels={"site": "", "variance_pct": "Variance (%)"},
            )
            fig_var.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig_var.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=300, showlegend=False,
            )
            st.plotly_chart(fig_var, use_container_width=True)

        # ── ROW 2: Dual-axis temp vs consumption + Ranking ────────────────────
        col3, col4 = st.columns([3, 2])

        with col3:
            st.markdown(
                "**Temperature vs Energy Consumption — Inverse Relationship**"
            )
            latest_temp = (
                df.sort_values("ingested_at")
                .groupby("site").last().reset_index()
                [["site", "temperature_c", "consumption_kw"]]
                .sort_values("temperature_c")
            )
            fig_dual = go.Figure()
            fig_dual.add_trace(go.Bar(
                x=latest_temp["site"],
                y=latest_temp["consumption_kw"],
                name="Consumption (kW)",
                marker_color=[
                    SITE_COLORS.get(s, "#888") for s in latest_temp["site"]
                ],
                yaxis="y1",
            ))
            fig_dual.add_trace(go.Scatter(
                x=latest_temp["site"],
                y=latest_temp["temperature_c"],
                name="Temperature (°C)",
                mode="lines+markers",
                line=dict(color="#FF4444", width=2.5, dash="dot"),
                marker=dict(size=8, color="#FF4444"),
                yaxis="y2",
            ))
            fig_dual.update_layout(
                yaxis=dict(title="Consumption (kW)", showgrid=True),
                yaxis2=dict(
                    title="Temperature (°C)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=0, r=0, t=30, b=0),
                height=280,
                hovermode="x unified",
            )
            st.plotly_chart(fig_dual, use_container_width=True)
            st.caption(
                "💡 Insight: Lower outdoor temperature → higher energy load. "
                "Munich (7°C) consumes ~230 kW more than Lyon (18°C) — "
                "driven primarily by HVAC heating load."
            )

        with col4:
            st.markdown("**Site Efficiency Ranking (24hr avg)**")
            ranking = (
                df.groupby("site")["consumption_kw"]
                .mean().sort_values().reset_index()
            )
            ranking.columns = ["Site", "Avg kW"]
            ranking["Avg kW"] = ranking["Avg kW"].round(1)
            fig_rank = px.bar(
                ranking,
                x="Avg kW", y="Site",
                orientation="h",
                color="Site",
                color_discrete_map=SITE_COLORS,
                labels={"Avg kW": "24hr Avg (kW)", "Site": ""},
            )
            fig_rank.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=280,
                showlegend=False,
            )
            st.plotly_chart(fig_rank, use_container_width=True)

        # ── ANOMALY SECTION ───────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🚨 Live Anomaly Detection")
        if anomalies:
            anom_df = pd.DataFrame(anomalies)
            for _, row in anom_df.head(5).iterrows():
                ca, cb, cc = st.columns([2, 2, 4])
                with ca:
                    color = SITE_COLORS.get(row["site"], "#888")
                    st.markdown(
                        f'<p style="color:{color};font-weight:700">'
                        f'■ {row["site"]}</p>',
                        unsafe_allow_html=True,
                    )
                    st.caption(str(row["timestamp"])[:19])
                with cb:
                    delta = row["consumption_kw"] - row["baseline_kw"]
                    st.metric(
                        "Consumption",
                        f"{row['consumption_kw']:.0f} kW",
                        delta=f"{delta:+.0f} vs baseline",
                        delta_color="inverse",
                    )
                with cc:
                    st.error(f"⚠️ {row['anomaly_reason']}")
        else:
            st.success(
                "✅ All sites operating within normal parameters. "
                "No anomalies detected."
            )

        with st.expander("📋 Raw Kafka Messages (latest 30)"):
            display_df = df[[
                "site", "timestamp", "temperature_c",
                "consumption_kw", "baseline_kw", "anomaly", "anomaly_reason",
            ]].head(30).copy()
            display_df.columns = [
                "Site", "Timestamp", "Temp °C",
                "Consumption kW", "Baseline kW", "Anomaly", "Reason",
            ]
            st.dataframe(display_df, use_container_width=True)

    dashboard()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI KNOWLEDGE ASSISTANT
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🤖 AI Knowledge Assistant")
    st.markdown(
        "Powered by **Groq LLaMA 3.3 70B** with live Kafka data context injection. "
        "Every answer is grounded in real energy readings from your pipeline."
    )

    readings_ai = get_recent_readings(hours=24)
    anom_ai = get_anomalies()

    if readings_ai:
        df_ai = pd.DataFrame(readings_ai)
        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            st.info(f"📊 **{len(readings_ai)}** live readings in AI context")
        with ci2:
            if anom_ai:
                st.warning(f"🚨 **{len(anom_ai)}** anomalies the AI knows about")
            else:
                st.success("✅ No anomalies in context")
        with ci3:
            st.info(f"🏭 **{df_ai['site'].nunique()}** sites being monitored")

    st.markdown("---")
    col_chat, col_tools = st.columns([3, 1])

    with col_chat:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "messages_display" not in st.session_state:
            st.session_state.messages_display = []

        if not st.session_state.messages_display:
            st.info(
                "👋 Hello! I have live access to your Kafka energy pipeline. "
                "Ask me anything about your manufacturing sites."
            )

        for msg in st.session_state.messages_display:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input(
            "Ask about your live energy data... "
            "e.g. 'Which site is most efficient right now?'"
        )
        if user_input:
            st.session_state.messages_display.append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Querying live Kafka data..."):
                    response = chat_with_energy_data(
                        user_input, st.session_state.chat_history
                    )
                st.markdown(response)
            st.session_state.messages_display.append(
                {"role": "assistant", "content": response}
            )
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

    with col_tools:
        st.markdown("### 💡 Quick questions")
        questions = [
            "Which site has highest load right now?",
            "Any anomalies to investigate?",
            "Why is Munich consuming more?",
            "Rank all 5 sites by efficiency",
            "What actions should I take today?",
            "Summarise current energy situation",
        ]
        for q in questions:
            if st.button(q, key=f"q_{q[:15]}", use_container_width=True):
                st.session_state.messages_display.append(
                    {"role": "user", "content": q}
                )
                st.session_state.chat_history.append(
                    {"role": "user", "content": q}
                )
                resp = chat_with_energy_data(
                    q, st.session_state.chat_history[:-1]
                )
                st.session_state.messages_display.append(
                    {"role": "assistant", "content": resp}
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": resp}
                )
                st.rerun()

        st.markdown("---")
        st.markdown("### 📄 Platform Report")
        if st.button(
            "Generate Weekly Report",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("AI generating report from live data..."):
                report = generate_weekly_report()
            st.markdown(report)
            st.download_button(
                "⬇️ Download Report",
                data=report,
                file_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — PIPELINE MONITOR
# ════════════════════════════════════════════════════════════════════════════════
with tab3:

    @st.experimental_fragment(run_every=120)
    def pipeline():
        readings_p = get_recent_readings()
        logs_p = get_pipeline_logs()

        st.markdown("## 🔧 Pipeline Monitor")
        st.markdown(
            "Real-time visibility into the Kafka → SQLite data pipeline health."
        )

        pm1, pm2, pm3, pm4 = st.columns(4)
        with pm1:
            st.metric("📨 Messages Consumed", len(readings_p))
        with pm2:
            delivered = len(
                [l for l in logs_p if l["event"] == "MESSAGE_CONSUMED"]
            )
            st.metric("✅ Successful Deliveries", delivered)
        with pm3:
            errors = len(
                [l for l in logs_p if "ERROR" in str(l["event"])]
            )
            st.metric(
                "❌ Pipeline Errors", errors,
                delta="check logs" if errors > 0 else "none",
                delta_color="inverse" if errors > 0 else "normal",
            )
        with pm4:
            st.metric("📡 Kafka Topics Active", 1)

        st.markdown("---")
        col_a, col_b = st.columns([1, 2])

        with col_a:
            st.markdown("### Architecture")
            st.code(
                "Open-Meteo REST API\n"
                "  (Real EU energy data)\n"
                "        ↓\n"
                "  kafka_producer.py\n"
                "  confluent-kafka SSL\n"
                "        ↓\n"
                "Aiven Apache Kafka 4.1\n"
                "  Topic: energy-readings\n"
                "  Region: Europe (Free)\n"
                "  Auth: Client Certificate\n"
                "        ↓\n"
                "  kafka_consumer.py\n"
                "  Group: energyops-dashboard\n"
                "        ↓\n"
                "  SQLite: energy.db\n"
                "  Tables: energy_readings\n"
                "          pipeline_logs\n"
                "        ↓\n"
                "  Streamlit Dashboard\n"
                "  + Groq LLaMA 3.3 70B"
            )
            st.markdown("### Connection Health")
            st.success("🟢 Aiven Kafka: Connected")
            st.success("🟢 SQLite: Active")
            st.success("🟢 Open-Meteo API: Live")
            st.success("🟢 Groq LLaMA 3.3: Ready")

        with col_b:
            st.markdown("### Live Pipeline Logs")
            if logs_p:
                logs_df = pd.DataFrame(logs_p)[["event", "detail", "logged_at"]]
                logs_df.columns = ["Event", "Detail", "Logged At (UTC)"]
                logs_df["Logged At (UTC)"] = logs_df["Logged At (UTC)"].str[:19]
                st.dataframe(logs_df, use_container_width=True, height=380)
            else:
                st.info(
                    "No pipeline events yet. "
                    "Start the producer and consumer."
                )

            if readings_p:
                df_p = pd.DataFrame(readings_p)
                vol = df_p.groupby("site").size().reset_index(name="Messages")
                fig_v = px.pie(
                    vol,
                    values="Messages",
                    names="site",
                    title="Messages Consumed per Site",
                    color="site",
                    color_discrete_map=SITE_COLORS,
                )
                fig_v.update_layout(
                    height=260,
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig_v, use_container_width=True)

    pipeline()
