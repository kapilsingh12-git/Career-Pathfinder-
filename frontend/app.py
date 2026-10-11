"""Streamlit UI.   Run:  streamlit run frontend/app.py"""
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API = os.getenv("BACKEND_URL", "http://localhost:8000")
PRIORITY_COLORS = {"Critical": "#d62728", "Important": "#ff9f1c", "Nice-to-have": "#2a9d8f"}

st.set_page_config(page_title="SDG 8 Career Guide", page_icon="🧭", layout="wide")


# ------------------------------------------------------------------ API helpers
def call(method: str, path: str, **kw):
    """Call the backend; show a friendly error and return None on failure."""
    try:
        r = requests.request(method, f"{API}{path}", timeout=120, **kw)
        if r.status_code >= 400:
            detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
            st.error(f"{path}: {detail}")
            return None
        return r.json()
    except requests.ConnectionError:
        st.error(f"Cannot reach the backend at {API}. Start it with `uvicorn backend.main:app --reload`.")
    except requests.Timeout:
        st.error("The backend timed out. Please try again.")
    return None


@st.cache_data(ttl=300, show_spinner=False)
def load_meta():
    try:
        return requests.get(f"{API}/roles", timeout=10).json()
    except Exception:
        return None


# ------------------------------------------------------------------ header & sidebar
st.title("🧭 Career Guidance & Skill-Gap Platform")
st.caption("Supporting **SDG 8 – Decent Work & Economic Growth**: match skills to real market demand and close the gap.")

meta = load_meta()
if not meta:
    st.error(f"Backend unavailable at {API}. Start it first: `uvicorn backend.main:app --reload`")
    st.stop()

with st.sidebar:
    st.header("1 · Your inputs")
    upload = st.file_uploader("Resume (PDF or TXT)", type=["pdf", "txt"])
    industry = st.selectbox("Target industry", ["Any"] + meta["industries"])
    role_options = [r for r, ind in meta["roles"].items() if industry in ("Any", ind)]
    dream = st.selectbox("Dream role (optional)", ["Best match"] + role_options)
    hours = st.slider("Study hours per week", 2, 30, 8)
    run = st.button("🔍 Analyze my profile", type="primary", use_container_width=True, disabled=upload is None)

# ------------------------------------------------------------------ pipeline
if run and upload:
    with st.spinner("Parsing resume..."):
        parsed = call("POST", "/parse-resume", files={"file": (upload.name, upload.getvalue())})
    if parsed:
        st.session_state.update(parsed=parsed, match=None, roadmap=None)

parsed = st.session_state.get("parsed")
if not parsed:
    st.info("👈 Upload a resume and click **Analyze** to begin.")
    st.stop()

tab_profile, tab_match, tab_gap, tab_road = st.tabs(["👤 Profile", "📊 Match analytics", "🧩 Skill gaps", "🗓️ 4-week roadmap"])

with tab_profile:
    st.subheader("Extracted profile (edit before matching)")
    c1, c2 = st.columns(2)
    c1.metric("Current role", parsed.get("current_role") or "Not detected")
    c2.metric("Years of experience", parsed["years_experience"])
    skills = st.multiselect("Skills", options=sorted(set(parsed["skills"])), default=parsed["skills"],
                            accept_new_options=True, help="Remove wrong skills or add missing ones.")
    if parsed["education"]:
        st.dataframe(pd.DataFrame(parsed["education"]), hide_index=True, use_container_width=True)
    st.caption(f"Extraction mode: **{parsed['extraction_method']}**")
    with st.expander("Raw JSON"):
        st.json(parsed)
    if st.button("Find matching jobs", type="primary"):
        if not skills:
            st.warning("Add at least one skill.")
        else:
            with st.spinner("Matching against the job market..."):
                m = call("POST", "/predict-match", json={
                    "skills": skills, "years_experience": parsed["years_experience"],
                    "industry": industry, "target_role": None if dream == "Best match" else dream})
            if m:
                st.session_state.update(match=m, skills=skills, roadmap=None)
                st.success("Done - open the other tabs.")

match = st.session_state.get("match")

with tab_match:
    if not match:
        st.info("Run **Find matching jobs** in the Profile tab.")
    else:
        st.caption(f"Compared against {match['jobs_searched']} simulated job listings.")
        top = match["top_matches"]
        cols = st.columns(len(top))
        for col, t in zip(cols, top):
            col.metric(t["role"], f"{t['confidence_pct']}%", help=f"Industry: {t['industry']}")
        df = pd.DataFrame(top)
        fig = px.bar(df, x="confidence_pct", y="role", orientation="h", text="confidence_pct", range_x=[0, 100],
                     color="confidence_pct", color_continuous_scale="Teal", labels={"confidence_pct": "Match confidence (%)", "role": ""})
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
        for t in top:
            with st.expander(f"{t['role']} - {t['industry']}"):
                a, b = st.columns(2)
                a.write(f"✅ **Matched:** {', '.join(t['matched_skills']) or '-'}")
                b.write(f"❌ **Missing:** {', '.join(t['missing_skills']) or '-'}")
                st.caption(f"Cosine similarity {t['embedding_similarity']} · skill coverage {t['skill_coverage_pct']}%")

with tab_gap:
    if not match:
        st.info("Run **Find matching jobs** first.")
    else:
        gap = match["skill_gap"]
        st.subheader(f"Gap analysis for: {gap['target_role']}")
        left, right = st.columns([1, 2])
        g = go.Figure(go.Indicator(mode="gauge+number", value=gap["readiness_pct"], number={"suffix": "%"},
                                   title={"text": "Role readiness"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#2a9d8f"}}))
        g.update_layout(height=280, margin=dict(t=60, b=10))
        left.plotly_chart(g, use_container_width=True)
        if gap["missing_skills"]:
            mdf = pd.DataFrame(gap["missing_skills"])
            f = px.bar(mdf, x="demand_pct", y="skill", orientation="h", color="priority", color_discrete_map=PRIORITY_COLORS,
                       labels={"demand_pct": "% of job listings requiring it", "skill": ""})
            f.update_layout(yaxis={"categoryorder": "total ascending"}, height=max(280, 40 * len(mdf)))
            right.plotly_chart(f, use_container_width=True)
        else:
            right.success("🎉 You cover every in-demand skill for this role!")
        st.write("**Skills you already have:** " + (", ".join(gap["matched_skills"]) or "-"))

with tab_road:
    if not match:
        st.info("Run **Find matching jobs** first.")
    else:
        gap = match["skill_gap"]
        st.write(f"Plan for **{gap['target_role']}** at **{hours} h/week**.")
        if st.button("✨ Generate roadmap", type="primary"):
            with st.spinner("Building your roadmap (prompt chain)..."):
                rm = call("POST", "/generate-roadmap", json={
                    "target_role": gap["target_role"], "missing_skills": [m["skill"] for m in gap["missing_skills"]],
                    "current_skills": st.session_state.get("skills", []), "weekly_hours": hours})
            if rm:
                st.session_state["roadmap"] = rm
        rm = st.session_state.get("roadmap")
        if rm:
            st.caption(f"Generated by: {rm['generated_by']}")
            for w in rm["weeks"]:
                with st.expander(f"Week {w['week']} - {w['theme']}", expanded=w["week"] == 1):
                    if w["skills"]:
                        st.write("**Skills:** " + ", ".join(w["skills"]))
                    st.write("**Goals**")
                    for goal in w["goals"]:
                        st.checkbox(goal, key=f"w{w['week']}-{goal}")
                    st.write("**Free resources**")
                    for r in w["resources"]:
                        st.markdown(f"- [{r['title']}]({r['url']}) · _{r['platform']}_")
                    st.info(f"🛠️ **Project:** {w['project']}")
            st.success(f"🏆 **Capstone:** {rm['capstone_project']}")
