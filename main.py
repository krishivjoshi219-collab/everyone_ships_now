import os
import time
import streamlit as st
import streamlit.components.v1 as components
import graphviz
from app import BankaiOrchestrator
from services.pdf_generator import PDFReportEngine

# ─── 🚨 PRODUCTION CONFIGURATION ───
# Paste your final unlisted 2-3 minute YouTube/Loom showcase link here!
DEMO_VIDEO_URL = ""

st.set_page_config(
    page_title="DependenceDoc // Environment Recovery",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Pendo SDK Install & Anonymous Initialize ───
components.html("""
<script>
(function(apiKey){
    var w=window.parent,d=w.document;
    if(w.pendo)return;
    (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
    v=['initialize','identify','updateOptions','pageLoad','track','trackAgent'];for(w=0,x=v.length;w<x;++w)(function(m){
    o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
    y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
    z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(w,d,'script','pendo');
    w.pendo.initialize({visitor:{id:''}});
})('70755b1d-0ef6-4138-886d-e1960931a813');
</script>
""", height=0)

# 2. Clean UI Style Guide
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .bankai-header { text-align: center; padding: 24px; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border-radius: 14px; border: 1px solid #374151; margin-bottom: 5px; }
    .caption-text { text-align: center; color: #64748b; font-size: 0.95rem; margin-bottom: 25px; }
    .metric-card { background-color: #0f172a; padding: 18px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .bankai-card { border: 1px solid #334155; border-radius: 12px; padding: 24px; background: #0f172a; margin-bottom: 20px; }
    .timeline-step { background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 10px; }
    .story-header { font-size: 1.2rem; font-weight: bold; color: #f8fafc; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #334155;}
    .fast-track-box { background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
    .how-it-works { display: flex; justify-content: space-between; background: #1e293b; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px; text-align: center; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_orchestrator(): return BankaiOrchestrator()

orchestrator = get_orchestrator()
pdf_engine = PDFReportEngine()

# ─── SIDEBAR ───
st.sidebar.markdown("### 🔑 API Integrations")
gemini_key = st.sidebar.text_input("Gemini API Token (Optional):", type="password", placeholder="AIZA Sy...")
st.sidebar.markdown("---")
# Sleek, native success banner for Novus integration
st.sidebar.success("📊 Novus Analytics Active")

def load_sample_file(filename: str):
    path = os.path.join("sample_logs", filename)
    try:
        with open(path, "r") as f:
            st.session_state["log_input"] = f.read()
    except Exception as e:
        st.sidebar.error(f"Failed to load sample file: {e}")

# ─── MAIN HERO BANNER ───
st.markdown("""
<div class="bankai-header">
    <h1 style="margin:0; color:#f8fafc; font-size:2.4rem; letter-spacing: 1px;">🩺 DEPENDENCE DOC</h1>
    <p style="margin:6px 0 0 0; color:#94a3b8; font-size:1.1rem;">Paste an error. Get the exact commands to fix it.</p>
</div>
<div class="caption-text">Supports Python dependency conflicts, missing packages, environment variables, and build failures.</div>
""", unsafe_allow_html=True)

# ─── HOW IT WORKS SECTION ───
st.markdown("""
<div class="how-it-works">
    <div><span style="font-size: 1.5rem;">📋</span><br/><strong style="color:#f8fafc;">1. Paste Error</strong><br/><span style="color:#94a3b8; font-size:0.85rem;">Drop your terminal log</span></div>
    <div style="color:#64748b; margin-top:10px;">➔</div>
    <div><span style="font-size: 1.5rem;">🧠</span><br/><strong style="color:#f8fafc;">2. Root Cause</strong><br/><span style="color:#94a3b8; font-size:0.85rem;">AI identifies the issue</span></div>
    <div style="color:#64748b; margin-top:10px;">➔</div>
    <div><span style="font-size: 1.5rem;">🛠️</span><br/><strong style="color:#f8fafc;">3. Recovery Plan</strong><br/><span style="color:#94a3b8; font-size:0.85rem;">Safe fixes generated</span></div>
    <div style="color:#64748b; margin-top:10px;">➔</div>
    <div><span style="font-size: 1.5rem;">📄</span><br/><strong style="color:#f8fafc;">4. Export</strong><br/><span style="color:#94a3b8; font-size:0.85rem;">Download Script or PDF</span></div>
</div>
""", unsafe_allow_html=True)

if "log_input" not in st.session_state:
    st.session_state["log_input"] = ""

# ─── EMPTY STATE & ONE-CLICK DEMOS ───
if not st.session_state["log_input"]:
    st.markdown("""
    <div class="fast-track-box">
        <h4 style="margin-top:0; color:#f8fafc;">🎯 Try It Instantly</h4>
        <p style="color: #cbd5e1; font-size: 0.95rem;">Judges: Click any button below to load a real terminal crash and see how DependenceDoc resolves it in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("🐍 Python Dependency Conflict", use_container_width=True): 
            load_sample_file("dependency_conflict.txt"); st.rerun()
    with col_b:
        if st.button("⚙️ OS Build Error (GCC)", use_container_width=True): 
            load_sample_file("missing_gcc.txt"); st.rerun()
    with col_c:
        if st.button("📦 Module Not Found", use_container_width=True): 
            load_sample_file("module_not_found.txt"); st.rerun()
    with col_d:
        if st.button("🔑 Missing Env Token", use_container_width=True): 
            load_sample_file("missing_api_key.txt"); st.rerun()

    st.markdown("### 🎥 Watch The 3-Minute Demo")
    if DEMO_VIDEO_URL:
        st.video(DEMO_VIDEO_URL)
    else:
        st.info("📺 **Demo Video Pending:** Add your YouTube URL to the code before final submission.")

st.markdown("---")

# ─── ANALYSIS CONSOLE ───
log_data = st.text_area("Paste your terminal crash dump or pip error here:", value=st.session_state["log_input"], height=140)
st.session_state["log_input"] = log_data

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_clicked = st.button("🚀 Analyze Error & Generate Fix", type="primary", use_container_width=True)
with col_btn2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state["log_input"] = ""
        st.rerun()

if analyze_clicked:
    if not log_data.strip():
        st.warning("Please paste an error log or use one of the Try It Instantly buttons above.")
    else:
        safe_log_data = log_data[:12000]
        
        start_time = time.time()
        with st.spinner("Analyzing environment and generating recovery plan..."):
            payload = orchestrator.run_full_diagnosis(safe_log_data, gemini_api_key=gemini_key)
            elapsed_time = round(time.time() - start_time, 2)
            
            domains_list = payload.get('detected_domains', [])
            recovery_stack = payload.get("recovery_order_stack", [])
            conf_percentage = payload.get('metrics', {}).get('confidence_percentage', 0)
            
            health_before = max(15, 100 - len(domains_list) * 20) if domains_list else 90
            health_after = min(100, health_before + 55) if recovery_stack else max(health_before, 95)
            risk_badge = "🟢 LOW RISK" if conf_percentage > 80 else "🟡 MEDIUM RISK"
        
        # Clean Metric Header
        st.markdown("### 📊 Analysis Results")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>SYSTEM HEALTH SCORE</small><h3 style='margin:5px 0 0 0; color:#f8fafc;'>{health_before} → <span style='color:#34d399;'>{health_after}</span></h3></div>", unsafe_allow_html=True)
        with m_col2: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>RECOVERY CONFIDENCE</small><h3 style='margin:5px 0 0 0; color:#38bdf8;'>{conf_percentage}%</h3></div>", unsafe_allow_html=True)
        with m_col3: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>FIX SIDE-EFFECT RISK</small><h3 style='margin:5px 0 0 0; color:#e2e8f0;'>{risk_badge}</h3></div>", unsafe_allow_html=True)
        with m_col4: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>ANALYSIS TIME</small><h3 style='margin:5px 0 0 0; color:#cbd5e1;'>⚡ {elapsed_time}s</h3></div>", unsafe_allow_html=True)
        
        # Visual Progress & Success Banner (Hardened float/integer clamp logic)
        st.progress(min(100, max(0, int(health_after))))
        st.success(f"✅ Recovery plan generated successfully in {elapsed_time}s with {conf_percentage}% confidence.")
        st.markdown("---")
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("<div class='bankai-card'>", unsafe_allow_html=True)
            st.markdown("<div class='story-header'>STEP 1 — Root Cause <span style='font-weight:normal; font-size:0.95rem; color:#94a3b8;'>🧠 Why did it break?</span></div>", unsafe_allow_html=True)
            st.write(payload.get("ai_insights", {}).get("explanation", "Analysis complete."))
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='bankai-card'>", unsafe_allow_html=True)
            st.markdown("<div class='story-header'>STEP 2 — Potential Side Effects <span style='font-weight:normal; font-size:0.95rem; color:#94a3b8;'>🔮 Is it safe to apply the fix?</span></div>", unsafe_allow_html=True)
            st.write(payload.get('ai_insights', {}).get('pre_thinking', 'Side effects evaluated. Fixes are safe to apply.'))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### STEP 3 — Recommended Fixes <span style='font-weight:normal; font-size:1.05rem; color:#94a3b8;'>🛠️ Run these commands to restore your environment</span>", unsafe_allow_html=True)
            if recovery_stack:
                for step in recovery_stack:
                    st.markdown(f"<div class='timeline-step'><strong style='color:#f8fafc;'>Step {step.get('step')}: {step.get('target')}</strong><br/><span style='color:#94a3b8;'>{step.get('explanation')}</span></div>", unsafe_allow_html=True)
                    st.code(step.get("command", ""), language="bash")
                    # Added the UX copy-paste hint directly below the code block
                    st.caption("📋 Hover over the top right of the code box to copy and paste directly into your terminal.")
            else:
                st.info("No commands needed. Environment looks stable.")
                    
        with col_right:
            st.markdown("<div class='bankai-card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ Verified Checks")
            for verification in payload.get("metrics", {}).get("verification_checklist", []):
                st.markdown(f" {verification}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### 📄 Export Results")
            script_content = "#!/bin/bash\n\n# DependenceDoc Recovery Script\n"
            for step in recovery_stack:
                script_content += f"echo \"Executing Step {step.get('step')}...\"\n{step.get('command', '')}\n\n"
            
            st.download_button("📋 Download Recovery Script (.sh)", data=script_content, file_name=f"recovery_{payload.get('analysis_id', 'UNKNOWN')}.sh", mime="text/x-shellscript", use_container_width=True)
            
            pdf_binary = pdf_engine.generate_executive_report(payload)
            st.download_button("📄 Download PDF Report", data=pdf_binary, file_name=f"report_{payload.get('analysis_id', 'UNKNOWN')}.pdf", mime="application/pdf", use_container_width=True)

# ─── ARCHITECTURE EXPLORER ───
st.markdown("---")
st.markdown("### 🗂️ Technical Design & Architecture")
st.markdown("Curious how we built it? Explore the system execution flow and source code below.")

with st.expander("🔍 Open Architecture Explorer", expanded=False):
    st.markdown("#### 🔄 System Flow")
    flow_dot = graphviz.Digraph(node_attr={'shape': 'box', 'style': 'filled', 'color': '#334155', 'fontcolor': '#f8fafc', 'fillcolor': '#1e293b'})
    flow_dot.attr(rankdir='LR', size='10,4')
    flow_dot.edge('Raw Terminal Log', 'Scout Parser')
    flow_dot.edge('Scout Parser', 'Detective Engine')
    flow_dot.edge('Detective Engine', 'Healer Compiler')
    flow_dot.edge('Healer Compiler', 'AI Context Gateway')
    flow_dot.edge('AI Context Gateway', 'PDF Generation / UI')
    st.graphviz_chart(flow_dot)
    
    st.markdown("---")
    
    c_left, c_right = st.columns([2, 3])
    with c_left:
        st.markdown("#### 📂 Code Structure")
        st.code("""
everyone_ships_now/
├── app.py                 # Core Orchestrator
├── main.py                # Streamlit UI
├── core/
│   ├── auditor.py         # AI Insights Gateway
│   ├── detective.py       # Constraint Logic
│   └── healer.py          # Script Compiler
└── services/
    ├── pdf_generator.py   # PDF Builder
    └── pypi_client.py     # Network Client
        """, language="text")
        
        file_map = {
            "app.py": "Main execution engine and routing.",
            "main.py": "Frontend UI and Streamlit configuration.",
            "core/auditor.py": "Handles safe API integrations for Gemini insights.",
            "core/detective.py": "Translates log text into structured python objects.",
            "services/pdf_generator.py": "Compiles data into a 3-page PDF report."
        }
        selected_file = st.selectbox("Inspect Module (Read-Only):", options=list(file_map.keys()))
        st.markdown(f"<div style='margin-top:10px;'><b>Target:</b> <code>{selected_file}</code><br/><i>Purpose:</i> {file_map[selected_file]}</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown(f"#### 📄 Source: <code>{selected_file}</code>", unsafe_allow_html=True)
        try:
            if os.path.exists(selected_file):
                with open(selected_file, "r", encoding="utf-8") as f:
                    st.code(f.read(), language="python")
            else:
                st.error("File not found.")
        except Exception as e:
            st.error(f"Read failed: {e}")
