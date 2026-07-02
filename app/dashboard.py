# app/dashboard.py
# Day 6 — Skill Gap Highlighter

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import tempfile
import sys

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))

from utils.extractor import extract_and_clean
from utils.parser import parse_resume
from utils.scorer import calculate_score

# =============================================
# PAGE CONFIG
# =============================================

st.set_page_config(
    page_title="Resume Ranker",
    page_icon="📄",
    layout="wide"
)

# =============================================
# CUSTOM CSS
# =============================================

st.markdown("""
<style>
    .skill-match   { color: #00C853; font-weight: bold; }
    .skill-missing { color: #FF1744; font-weight: bold; }
    .score-high    { color: #00C853; }
    .score-medium  { color: #FF9100; }
    .score-low     { color: #FF1744; }
    .candidate-card {
        background: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# HEADER
# =============================================

st.title("📄 Resume Ranker")
st.markdown("**AI-powered resume screening for recruiters**")
st.divider()

# =============================================
# SIDEBAR
# =============================================

st.sidebar.title("📋 Job Description")
st.sidebar.markdown("Paste the job description below:")

jd_text = st.sidebar.text_area(
    label="Job Description",
    placeholder="We are looking for a Python Developer...",
    height=300,
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("### ℹ️ How to use")
st.sidebar.markdown("""
1. Paste job description here
2. Upload resumes on the right
3. Click Analyze Resumes
4. See ranked results!
""")

# =============================================
# UPLOAD SECTION
# =============================================

st.markdown("### 📤 Upload Resumes")
st.markdown("Upload one or more resumes (PDF or DOCX)")

uploaded_files = st.file_uploader(
    label="Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

analyze_clicked = st.button(
    "🔍 Analyze Resumes",
    type="primary",
    use_container_width=True
)

# =============================================
# HELPER FUNCTIONS
# =============================================

def score_color(score):
    """Returns color based on score"""
    if score >= 70:
        return "🟢"
    elif score >= 50:
        return "🟡"
    else:
        return "🔴"


def score_label(score):
    """Returns label based on score"""
    if score >= 70:
        return "Strong Match"
    elif score >= 50:
        return "Good Match"
    elif score >= 30:
        return "Partial Match"
    else:
        return "Weak Match"


def build_skill_gap_table(jd_skills, matched, missing):
    """
    Builds a color coded skill gap dataframe
    """
    rows = []
    for skill in jd_skills:
        if skill in matched:
            rows.append({
                "Skill"  : skill,
                "Status" : "✅ Present",
                "Match"  : "Yes"
            })
        else:
            rows.append({
                "Skill"  : skill,
                "Status" : "❌ Missing",
                "Match"  : "No"
            })
    return pd.DataFrame(rows)


# =============================================
# RESULTS
# =============================================

if analyze_clicked:

    if not jd_text.strip():
        st.error("⚠️ Please paste a Job Description!")
        st.stop()

    if not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
        st.stop()

    st.divider()

    results  = []
    progress = st.progress(0)
    status   = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        status.text(f"Processing {uploaded_file.name}...")
        progress.progress((i + 1) / len(uploaded_files))

        try:
            suffix = ".pdf" if uploaded_file.name.endswith(
                ".pdf") else ".docx"

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix
            ) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            text   = extract_and_clean(tmp_path)
            parsed = parse_resume(text)
            result = calculate_score(text, jd_text, parsed)

            results.append({
                "Name"          : parsed['name'],
                "Email"         : parsed['email'],
                "Final Score"   : result['final_score'],
                "Skill Score"   : result['skill_score'],
                "Semantic Score": result['semantic_score'],
                "Section Score" : result['section_score'],
                "Matched"       : result['matched'],
                "Missing"       : result['missing'],
                "JD Skills"     : result['jd_skills'],
                "File"          : uploaded_file.name
            })

            os.unlink(tmp_path)

        except Exception as e:
            st.warning(f"Could not process "
                      f"{uploaded_file.name}: {e}")

    progress.empty()
    status.empty()

    if not results:
        st.error("No resumes could be processed!")
        st.stop()

    # Sort by score
    results = sorted(
        results,
        key=lambda x: x['Final Score'],
        reverse=True
    )

    # =============================================
    # TABS
    # =============================================

    tab1, tab2, tab3 = st.tabs([
        "🏆 Rankings",
        "📊 Skill Gap",
        "🔍 Details"
    ])

    # =============================================
    # TAB 1 — RANKINGS
    # =============================================

    with tab1:
        st.markdown("### 🏆 Candidate Rankings")

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Candidates",
                      len(results))
        with col2:
            top_score = results[0]['Final Score']
            st.metric("Top Score",
                      f"{top_score}%")
        with col3:
            avg_score = round(
                sum(r['Final Score'] for r in results)
                / len(results), 2
            )
            st.metric("Average Score",
                      f"{avg_score}%")

        st.divider()

        # Ranking table
        table_data = []
        for i, r in enumerate(results):
            medal = ["🥇", "🥈", "🥉"][i] \
                    if i < 3 else f"{i+1}."
            table_data.append({
                "Rank"        : medal,
                "Name"        : r['Name'],
                "Email"       : r['Email'],
                "Final Score" : f"{r['Final Score']}%",
                "Skill Score" : f"{r['Skill Score']}%",
                "Status"      : score_label(
                                r['Final Score'])
            })

        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Bar chart
        st.markdown("### 📊 Score Comparison")
        chart_data = pd.DataFrame({
            "Candidate": [r['Name'] for r in results],
            "Score"    : [r['Final Score'] for r in results]
        })
        st.bar_chart(
            chart_data.set_index("Candidate"),
            use_container_width=True
        )

    # =============================================
    # TAB 2 — SKILL GAP
    # =============================================

    with tab2:
        st.markdown("### 📊 Skill Gap Analysis")
        st.markdown("See exactly which skills each "
                   "candidate has or is missing")

        for i, r in enumerate(results):
            medal = ["🥇", "🥈", "🥉"][i] \
                    if i < 3 else f"#{i+1}"

            st.markdown(f"#### {medal} {r['Name']}"
                       f" — {score_color(r['Final Score'])}"
                       f" {r['Final Score']}%")

            # Build skill gap table
            skill_df = build_skill_gap_table(
                r['JD Skills'],
                r['Matched'],
                r['Missing']
            )

            if not skill_df.empty:
                # Color the Status column
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**Required Skills:**")
                    st.dataframe(
                        skill_df[['Skill', 'Status']],
                        use_container_width=True,
                        hide_index=True
                    )

                with col2:
                    # Pie chart
                    matched_count = len(r['Matched'])
                    missing_count = len(r['Missing'])

                    fig = go.Figure(
                        go.Pie(
                            labels=['Matched', 'Missing'],
                            values=[matched_count,
                                   missing_count],
                            marker_colors=['#00C853',
                                         '#FF1744'],
                            hole=0.4
                        )
                    )
                    fig.update_layout(
                        title=f"Skill Coverage",
                        height=300,
                        showlegend=True,
                        margin=dict(t=40, b=0,
                                   l=0, r=0)
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=f"pie_chart_{i}"
                    )

            st.divider()

    # =============================================
    # TAB 3 — DETAILS
    # =============================================

    with tab3:
        st.markdown("### 🔍 Candidate Details")

        for i, r in enumerate(results):
            medal = ["🥇", "🥈", "🥉"][i] \
                    if i < 3 else f"#{i+1}"

            with st.expander(
                f"{medal} {r['Name']} "
                f"— {r['Final Score']}% "
                f"({score_label(r['Final Score'])})"
            ):
                # Score breakdown
                st.markdown("**Score Breakdown:**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Final Score",
                        f"{r['Final Score']}%"
                    )
                with col2:
                    st.metric(
                        "Skill Score",
                        f"{r['Skill Score']}%"
                    )
                with col3:
                    st.metric(
                        "Semantic Score",
                        f"{r['Semantic Score']}%"
                    )
                with col4:
                    st.metric(
                        "Section Score",
                        f"{r['Section Score']}%"
                    )

                st.divider()

                # Skills
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**✅ Matched Skills:**")
                    if r['Matched']:
                        for skill in r['Matched']:
                            st.success(f"✅ {skill}")
                    else:
                        st.warning("No skills matched")

                with col2:
                    st.markdown("**❌ Missing Skills:**")
                    if r['Missing']:
                        for skill in r['Missing']:
                            st.error(f"❌ {skill}")
                    else:
                        st.success(
                            "🎉 No missing skills!"
                        )

                st.divider()
                st.caption(f"📄 File: {r['File']} "
                          f"| 📧 {r['Email']}")
                # =============================================
    # DOWNLOAD REPORT BUTTON
    # =============================================

    st.divider()
    st.markdown("### 📥 Download Report")

    try:
        from utils.report import generate_report

        pdf_bytes = generate_report(results, jd_text)

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name="resume_ranking_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        st.success("Report ready! Click above to download.")

    except Exception as e:
        st.error(f"Could not generate report: {e}")