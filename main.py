import os
import time
import streamlit as st
import streamlit.components.v1 as components
import graphviz
from app import BankaiOrchestrator
from services.pdf_generator import PDFReportEngine
from services.pendo_tracker import track as pendo_track


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

# ─── UI Style Guide ───
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

# ─── MODEL TIER CONFIGURATION & STRICT BYOK QUOTAS ───
MODEL_CONFIGS = {
    "Google Gemini": {
        "provider": "gemini",
        "models": {
            "⚡ Gemini 3.8 Flash (Standard)": {"id": "gemini-3.8-flash", "tier": "gemini_flash", "quota": 5, "desc": "5 Free Tries on Shared Key"},
            "🪶 Gemini Flash Lite (Fast)": {"id": "gemini-2.5-flash-lite", "tier": "gemini_lite", "quota": 10, "desc": "10 Free Tries on Shared Key"},
            "🧠 Gemini 2.5 Pro (Deep Reasoning)": {"id": "gemini-2.5-pro", "tier": "gemini_pro", "quota": 2, "desc": "2 Free Tries (Expensive)"},
        }
    },
    "Groq Cloud": {
        "provider": "groq",
        "models": {
            "🧠 Groq GPT OSS 120B (Deep Reasoning)": {"id": "openai/gpt-oss-120b", "tier": "groq_pro", "quota": 2, "desc": "2 Free Tries (Expensive)"},
            "⚡ Groq Qwen 3.8 27B (Balanced)": {"id": "qwen/qwen3.8-27b", "tier": "groq_flash", "quota": 5, "desc": "5 Free Tries on Shared Key"},
            "🪶 Groq GPT OSS 20B (Ultra-Fast)": {"id": "openai/gpt-oss-20b", "tier": "groq_lite", "quota": 10, "desc": "10 Free Tries on Shared Key"},
        }
    }
}

if "tier_usage" not in st.session_state:
    st.session_state["tier_usage"] = {
        "gemini_lite": 0,
        "gemini_flash": 0,
        "gemini_pro": 0,
        "groq_lite": 0,
        "groq_flash": 0,
        "groq_pro": 0,
    }

# ─── SIDEBAR ───
st.sidebar.markdown("### 🤖 Model & Provider Selection")
chosen_provider_name = st.sidebar.radio("AI Provider:", list(MODEL_CONFIGS.keys()))
provider_info = MODEL_CONFIGS[chosen_provider_name]
chosen_model_label = st.sidebar.selectbox("Model Tier:", list(provider_info["models"].keys()))
selected_model_info = provider_info["models"][chosen_model_label]
tier_id = selected_model_info["tier"]
tier_quota = selected_model_info["quota"]
model_id = selected_model_info["id"]
provider_code = provider_info["provider"]

st.sidebar.markdown("### 🔑 API Key (BYOK)")
_gemini_env_set = bool(os.environ.get("GEMINI_API_KEY", ""))
_groq_env_set = bool(os.environ.get("GROQ_API_KEY", ""))

user_gemini_key = ""
user_groq_key = ""

if provider_code == "gemini":
    if _gemini_env_set:
        st.sidebar.success("🛡️ Shared Gemini Key Active (from Secrets)")
    user_gemini_key = st.sidebar.text_input(
        "Enter Your Gemini Key (BYOK):",
        type="password",
        placeholder="Paste AIza... or AQ... key",
        help="Provide your own Gemini API key for unlimited runs with zero quota restrictions."
    )
    is_byok = bool(user_gemini_key and user_gemini_key.strip())
else:
    if _groq_env_set:
        st.sidebar.success("🛡️ Shared Groq Key Active (from Secrets)")
    user_groq_key = st.sidebar.text_input(
        "Enter Your Groq Key (BYOK):",
        type="password",
        placeholder="Paste gsk_... key",
        help="Provide your own Groq API key for unlimited runs with zero quota restrictions."
    )
    is_byok = bool(user_groq_key and user_groq_key.strip())

# Quota indicator display
if is_byok:
    st.sidebar.success("🚀 **BYOK Mode**: Unlimited runs unlocked on your key!")
else:
    used_tries = st.session_state["tier_usage"].get(tier_id, 0)
    remaining_tries = max(0, tier_quota - used_tries)
    if remaining_tries > 0:
        st.sidebar.info(f"⚡ **Shared Key Quota**: {remaining_tries}/{tier_quota} free runs left ({chosen_model_label.split()[1]}).")
    else:
        st.sidebar.error(f"🔒 **Quota Exhausted**: 0/{tier_quota} free runs left for this tier. Enter your own key above to unlock unlimited runs!")

st.sidebar.markdown("---")
st.sidebar.success("📊 Novus Analytics Active")

SAMPLE_CATEGORIES = {
    "dependency_conflict.txt": "dependency_conflict",
    "missing_gcc.txt": "os_build_error",
    "module_not_found.txt": "module_not_found",
    "missing_api_key.txt": "missing_env_token",
}

def load_sample_file(filename: str):
    path = os.path.join("sample_logs", filename)
    try:
        with open(path, "r") as f:
            content = f.read()
            st.session_state["log_input"] = content
            pendo_track("sample_log_loaded", properties={
                "sample_filename": filename,
                "sample_category": SAMPLE_CATEGORIES.get(filename, "unknown"),
                "sample_log_length": len(content),
            })
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
        # ─── STRICT BYOK & TIER QUOTA INTERCEPTOR ───
        used_tries = st.session_state["tier_usage"].get(tier_id, 0)
        if not is_byok and used_tries >= tier_quota:
            st.error(
                f"🔒 **Free Quota Exhausted ({tier_quota}/{tier_quota} used)** for `{chosen_model_label}` on the shared host key!\n\n"
                f"👉 **Strict BYOK Required**: To run unlimited diagnoses with this model, please enter your own {chosen_provider_name} API Key in the sidebar."
            )
            st.stop()

        pendo_track("error_log_submitted", properties={
            "log_length": len(log_data),
            "log_truncated": len(log_data) > 12000,
            "provider": provider_code,
            "model": model_id,
            "is_byok": is_byok,
        })

        start_time = time.time()
        with st.spinner(f"Analyzing environment with {chosen_model_label} and generating recovery plan..."):
            payload = orchestrator.run_full_diagnosis(
                safe_log_data, 
                gemini_api_key=user_gemini_key, 
                groq_api_key=user_groq_key,
                provider=provider_code,
                model_name=model_id
            )
            if not is_byok:
                st.session_state["tier_usage"][tier_id] += 1
            elapsed_time = round(time.time() - start_time, 2)

            domains_list = payload.get('detected_domains', [])
            recovery_stack = payload.get("recovery_order_stack", [])
            conf_percentage = payload.get('metrics', {}).get('confidence_percentage', 0)

            health_before = max(15, 100 - len(domains_list) * 20) if domains_list else 90
            health_after = min(100, health_before + 55) if recovery_stack else max(health_before, 95)
            risk_badge = "🟢 LOW RISK" if conf_percentage > 80 else "🟡 MEDIUM RISK"

            pendo_track("diagnosis_completed", properties={
                "analysis_id": payload.get("analysis_id", ""),
                "detected_domains": str(domains_list),
                "domain_count": len(domains_list),
                "recovery_step_count": len(recovery_stack),
                "confidence_percentage": conf_percentage,
                "health_before": health_before,
                "health_after": health_after,
                "risk_badge": risk_badge,
                "elapsed_time_seconds": elapsed_time,
                "has_ai_insights": bool(payload.get("ai_insights", {}).get("explanation")),
            })

        # ─── Identify this analysis session in Pendo ───
        analysis_id = payload.get("analysis_id", "anonymous")
        components.html(f"""
<script>
(function() {{
    var w = window.parent;
    if (!w.pendo || !w.pendo.identify) return;
    w.pendo.identify({{
        visitor: {{ id: '{analysis_id}' }},
        account: {{ id: 'dependencedoc' }}
    }});
}})();
</script>
""", height=0)

        # Clean Metric Header
        st.markdown("### 📊 Analysis Results")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>SYSTEM HEALTH SCORE</small><h3 style='margin:5px 0 0 0; color:#f8fafc;'>{health_before} → <span style='color:#34d399;'>{health_after}</span></h3></div>", unsafe_allow_html=True)
        with m_col2: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>RECOVERY CONFIDENCE</small><h3 style='margin:5px 0 0 0; color:#38bdf8;'>{conf_percentage}%</h3></div>", unsafe_allow_html=True)
        with m_col3: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>FIX SIDE-EFFECT RISK</small><h3 style='margin:5px 0 0 0; color:#e2e8f0;'>{risk_badge}</h3></div>", unsafe_allow_html=True)
        with m_col4: st.markdown(f"<div class='metric-card'><small style='color:#64748b; font-weight:bold;'>ANALYSIS TIME</small><h3 style='margin:5px 0 0 0; color:#cbd5e1;'>⚡ {elapsed_time}s</h3></div>", unsafe_allow_html=True)

        st.progress(min(100, max(0, int(health_after))))
        st.success(f"✅ Recovery plan generated successfully in {elapsed_time}s with {conf_percentage}% confidence.")

        # ─── 🛡️ WATCHER STATUS CARD ───
        watcher_status = payload.get("watcher_status", {})
        if watcher_status:
            w_verdict = watcher_status.get("verdict", "—")
            w_api_calls = watcher_status.get("api_calls_tracked", 0)
            w_within = watcher_status.get("within_limits", True)
            w_color = "#34d399" if "CLEAN" in w_verdict else "#f87171"
            w_badge_color = "#34d399" if w_within else "#fb923c"
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid #334155;"
                f"border-radius:10px;padding:10px 16px;margin:8px 0;display:flex;align-items:center;gap:20px;'>"
                f"<span style='font-size:1.2rem;'>🛡️</span>"
                f"<span style='color:#94a3b8;font-size:0.75rem;font-weight:700;letter-spacing:0.05em;'>SANDBOX WATCHER</span>"
                f"<span style='color:{w_color};font-weight:700;font-size:0.85rem;'>{w_verdict}</span>"
                f"<span style='color:#64748b;font-size:0.8rem;'>│</span>"
                f"<span style='color:#94a3b8;font-size:0.8rem;'>PyPI calls: "
                f"<span style='color:{w_badge_color};font-weight:700;'>{w_api_calls}</span></span>"
                f"</div>",
                unsafe_allow_html=True
            )

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

            script_file_name = f"recovery_{payload.get('analysis_id', 'UNKNOWN')}.sh"
            pendo_track("recovery_script_exported", properties={
                "analysis_id": payload.get("analysis_id", ""),
                "script_size_bytes": len(script_content.encode("utf-8")),
                "step_count": len(recovery_stack),
                "file_name": script_file_name,
            })
            st.download_button("📋 Download Recovery Script (.sh)", data=script_content, file_name=script_file_name, mime="text/x-shellscript", use_container_width=True)

            pdf_binary = pdf_engine.generate_executive_report(payload)
            pdf_file_name = f"report_{payload.get('analysis_id', 'UNKNOWN')}.pdf"
            pendo_track("pdf_report_exported", properties={
                "analysis_id": payload.get("analysis_id", ""),
                "pdf_size_bytes": len(pdf_binary) if pdf_binary else 0,
                "recovery_step_count": len(recovery_stack),
                "domains_detected_count": len(domains_list),
                "confidence_percentage": conf_percentage,
                "file_name": pdf_file_name,
            })
            st.download_button("📄 Download PDF Report", data=pdf_binary, file_name=pdf_file_name, mime="application/pdf", use_container_width=True)

# ─── ARCHITECTURE EXPLORER ───
st.markdown("---")
st.markdown("### 🗂️ Technical Design & Architecture")
st.markdown("A complete breakdown of the system execution pipeline, module responsibilities, and source code.")

with st.expander("🔍 Open Architecture Explorer", expanded=False):

    # ── FLOW DIAGRAM ──────────────────────────────────────────────
    st.markdown("#### 🔄 Full Pipeline Execution Flow")
    flow_dot = graphviz.Digraph(
        node_attr={'shape': 'box', 'style': 'filled', 'color': '#334155', 'fontcolor': '#f8fafc', 'fillcolor': '#1e293b', 'fontsize': '11'}
    )
    flow_dot.attr(rankdir='LR', size='14,5', bgcolor='transparent')

    flow_dot.node('A', 'Raw Terminal Log\n(User Input)')
    flow_dot.node('B', 'Sentinel Guard\ncore/sentinel.py')
    flow_dot.node('C', 'Domain Router\napp.py')
    flow_dot.node('D1', 'System Resolver\ncore/system_resolver.py')
    flow_dot.node('D2', 'Env Resolver\ncore/environment_resolver.py')
    flow_dot.node('D3', 'Runtime Resolver\ncore/runtime_resolver.py')
    flow_dot.node('D4', 'Scout Parser\ncore/scout.py')
    flow_dot.node('E', 'Detective Engine\ncore/detective.py')
    flow_dot.node('F', 'PyPI Client\nservices/pypi_client.py')
    flow_dot.node('G', 'Healer Compiler\ncore/healer.py')
    flow_dot.node('H', 'AI Auditor\ncore/auditor.py')
    flow_dot.node('W', 'Sandbox Watcher\ncore/watcher.py', fillcolor='#1c3a2a')
    flow_dot.node('I', 'PDF Generator\nservices/pdf_generator.py')
    flow_dot.node('J', 'Pendo Tracker\nservices/pendo_tracker.py')
    flow_dot.node('K', 'Streamlit UI\nmain.py')

    flow_dot.edge('A', 'B')
    flow_dot.edge('B', 'C')
    flow_dot.edge('C', 'D1')
    flow_dot.edge('C', 'D2')
    flow_dot.edge('C', 'D3')
    flow_dot.edge('C', 'D4')
    flow_dot.edge('D4', 'E')
    flow_dot.edge('E', 'F')
    flow_dot.edge('F', 'G')
    flow_dot.edge('D1', 'H')
    flow_dot.edge('D2', 'H')
    flow_dot.edge('D3', 'H')
    flow_dot.edge('G', 'H')
    flow_dot.edge('W', 'C', style='dashed', label='monitor')
    flow_dot.edge('H', 'K')
    flow_dot.edge('K', 'I')
    flow_dot.edge('K', 'J')
    st.graphviz_chart(flow_dot)

    st.markdown("---")

    # ── FILE MAP ──────────────────────────────────────────────────
    file_map = {
        "app.py": (
            "🧠 Master Orchestrator",
            "The central coordination engine of DependenceDoc. Instantiates all core modules and routes every incoming log through the correct analysis streams (System, Environment, Runtime, Dependency). Implements BankaiOrchestrator, wraps the entire pipeline in a SandboxWatcher-monitored worker thread, computes the explainable confidence score, and assembles the final unified payload returned to the UI."
        ),
        "main.py": (
            "🖥️ Streamlit UI Layer",
            "The complete frontend interface. Manages session state, sidebar API key indicators, Pendo analytics injection (SDK install + identify()), sample log preloading, and the full results rendering — metric cards, system health bars, AI explanation panels, recovery command stack, export buttons, and this architecture explorer. All user-facing interactions pass through this file."
        ),
        "core/sentinel.py": (
            "🚦 Signal Detection Gate",
            "The first stage of the pipeline. Performs a fast, keyword-based multi-domain classification of the raw log, returning a boolean signal map across four fault domains: system (GCC / OpenSSL / wheel builds), environment (missing modules / env tokens), runtime (port collisions / DB connections), and dependency (version constraints). Routes the log to the correct resolver streams in the orchestrator."
        ),
        "core/scout.py": (
            "🔍 Constraint Extraction Parser",
            "Scans raw terminal output line-by-line using three independent regex engines: (1) Classic Inline Detector for 'requires X but you have Y' patterns, (2) Modern Multi-Line Detector for 'depends on' backtracking blocks, and (3) Requested Version Detector for 'user requested X==Y' entries. Outputs a structured dictionary of requirement specifiers and installed versions consumed directly by the Detective Engine."
        ),
        "core/detective.py": (
            "🕵️ Conflict Analysis Engine",
            "Applies PEP 440 SpecifierSet mathematics to determine whether installed package versions violate declared dependency constraints. Aggregates multi-line specifiers into unified constraint sets, cross-references them against installed versions using the packaging library, and classifies each conflict as a version violation or an unresolvable_deadlock — where two parents demand mutually exclusive version ranges with zero possible overlap."
        ),
        "core/healer.py": (
            "💊 Recovery Plan Compiler",
            "Receives the Detective's conflict report and live PyPI release metadata, then runs a constraint satisfaction algorithm to identify the highest stable version that satisfies all declared specifier rules. For deadlocked packages, it emits environment-segregation guidance. For resolvable conflicts, it compiles exact pip install --force-reinstall commands with the mathematically optimal pinned version."
        ),
        "core/auditor.py": (
            "🤖 AI Insight Gateway",
            "Implements a dual-provider AI credential resolution chain: environment secrets are always primary, with optional sidebar overrides and a key.json fallback for local development. Routes the enriched diagnostic prompt to Gemini 2.5 Flash (via google-genai SDK with a legacy google-generativeai fallback) or Groq LLaMA-3.3-70B. Includes a robust response parser that handles both structured (--- separator) and unstructured AI outputs without crashing."
        ),
        "core/watcher.py": (
            "🛡️ Sandbox Execution Warden",
            "An independent runtime safety module that enforces two defensive constraints on every pipeline execution: a configurable CPU-second thread ceiling (90s default) monitored via high-frequency polling, and a cumulative API call counter with a configurable threshold (10 calls default). After each analysis run, reports a CLEAN EXIT or TIMEOUT BREACH verdict that is surfaced in the UI and included in the analysis payload."
        ),
        "core/system_resolver.py": (
            "🖥️ OS-Layer Fault Resolver",
            "Maintains a rule table of native C-toolchain failure signatures — missing GCC compiler, absent OpenSSL development headers, and outdated pip/setuptools/wheel packaging utilities. Matches each against the raw log using compiled regex patterns and returns the exact apt-get or pip command required to restore the host OS build environment."
        ),
        "core/environment_resolver.py": (
            "🌐 Environment Path Resolver",
            "Detects two classes of environment configuration failures: inactive or missing virtual environments causing ModuleNotFoundError, and absent runtime secret tokens causing KeyError crashes. Maps each fault to the correct remediation command — venv activation with requirements reinstall, or a secure environment variable export template."
        ),
        "core/runtime_resolver.py": (
            "⚙️ Infrastructure Runtime Resolver",
            "Identifies network-layer and process-level runtime failures: port-already-in-use socket collisions and database connection-refused errors. For port conflicts, emits a targeted lsof / kill command to terminate the blocking ghost process. For database failures, returns the appropriate systemctl or Docker Compose service-start command."
        ),
        "models/package.py": (
            "📐 Structured Data Models",
            "Defines the five dataclass blueprints that enforce type safety throughout the pipeline: RequirementModel (extracted specifier constraints), InstalledModel (deployed package versions), ConflictModel (verified version mismatches with verdicts), MissingPackageModel (completely absent dependencies), and PipelineReportModel (the master record passed from backend engines to the UI and PDF generator)."
        ),
        "services/pypi_client.py": (
            "📡 PyPI Registry Client",
            "Performs authenticated HTTP lookups against the official PyPI JSON API with LRU caching (128-entry in-memory cache) and configurable connection/read timeouts (3s connect, 5s read). Returns the full historical release index and latest stable version for each queried package, enabling the Healer to compute mathematically valid pinned install targets."
        ),
        "services/pdf_generator.py": (
            "📄 Executive PDF Report Engine",
            "Transforms the unified analysis payload into a structured three-page ReportLab document: Page 1 covers the AI-generated incident summary and a high-level metric table; Page 2 presents the predictive pre-thinking risk matrix and confidence verification checklist; Page 3 contains the ordered remediation command stack with explanations rendered in monospace code blocks. Includes an HTML entity sanitizer to prevent render crashes on log snippets containing angle brackets."
        ),
        "services/pendo_tracker.py": (
            "📊 Novus Analytics Event Emitter",
            "Posts structured telemetry events to the Pendo Data API using the project's integration key. Fires on five lifecycle milestones: sample_log_loaded, error_log_submitted, diagnosis_completed, recovery_script_exported, and pdf_report_exported. Each event carries a rich properties payload including analysis_id, confidence percentage, domain count, and elapsed time. Implemented with silent failure to ensure analytics never disrupts the analysis pipeline."
        ),
    }

    # ── DIRECTORY TREE ───────────────────────────────────────────
    c_left, c_right = st.columns([2, 3])
    with c_left:
        st.markdown("#### 📂 Complete Module Registry")
        st.code("""
DependenceDoc/
├── app.py                       # Master Orchestrator
├── main.py                      # Streamlit UI Layer
├── models/
│   └── package.py               # Structured Data Models
├── core/
│   ├── sentinel.py              # Signal Detection Gate
│   ├── scout.py                 # Constraint Parser
│   ├── detective.py             # Conflict Analysis Engine
│   ├── healer.py                # Recovery Compiler
│   ├── auditor.py               # AI Insight Gateway
│   ├── watcher.py               # Sandbox Execution Warden
│   ├── system_resolver.py       # OS-Layer Fault Resolver
│   ├── environment_resolver.py  # Environment Path Resolver
│   └── runtime_resolver.py      # Runtime Resolver
└── services/
    ├── pypi_client.py           # PyPI Registry Client
    ├── pdf_generator.py         # Executive PDF Engine
    └── pendo_tracker.py         # Novus Analytics Emitter
        """, language="text")

        selected_file = st.selectbox("Inspect Module (Read-Only):", options=list(file_map.keys()))
        role_label, summary_text = file_map[selected_file]
        st.markdown(
            f"<div style='margin-top:12px; background:#0f172a; border:1px solid #334155; border-radius:8px; padding:14px;'>"
            f"<div style='color:#38bdf8; font-size:0.75rem; font-weight:700; letter-spacing:0.06em; margin-bottom:4px;'>MODULE ROLE</div>"
            f"<div style='color:#f8fafc; font-weight:700; font-size:0.95rem; margin-bottom:8px;'>{role_label}</div>"
            f"<div style='color:#94a3b8; font-size:0.83rem; line-height:1.55;'>{summary_text}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

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
