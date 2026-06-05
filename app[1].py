import streamlit as st
from medical_expert_panel import EnhancedMedicalPanel
from datetime import datetime
import glob
import html
import io
import json
import os
import re
import zipfile

# Set page config
st.set_page_config(page_title="Biodesign AI Roundtable", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 1.4rem;
    }
    h1 {
        font-size: 2.05rem !important;
        line-height: 1.15 !important;
        margin-bottom: 0.35rem !important;
    }
    h3 {
        font-size: 1.15rem !important;
        line-height: 1.25 !important;
        margin-bottom: 0.8rem !important;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .status-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        background: #ffffff;
    }
    .status-phase {
        color: #4b5563;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    .status-role {
        color: #111827;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .status-next {
        color: #6b7280;
        font-size: 0.95rem;
    }
    .phase-chip {
        display: inline-block;
        border: 1px solid #d1d5db;
        border-radius: 999px;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        background: #ffffff;
        color: #374151;
        font-size: 0.86rem;
    }
    .phase-chip-active {
        border-color: #2563eb;
        background: #eff6ff;
        color: #1d4ed8;
        font-weight: 700;
    }
    .phase-chip-done {
        border-color: #16a34a;
        background: #f0fdf4;
        color: #166534;
    }
    .result-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0 18px 0;
        background: #ffffff;
    }
    .roundtable-dashboard {
        border: 1px solid #dbe3ef;
        border-radius: 8px;
        padding: 12px;
        margin: 14px 0;
        background: #ffffff;
    }
    .roundtable-header {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .roundtable-title {
        color: #111827;
        font-size: 1.05rem;
        font-weight: 750;
        margin-bottom: 4px;
    }
    .roundtable-subtitle {
        color: #64748b;
        font-size: 0.9rem;
    }
    .roundtable-now {
        min-width: 210px;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 8px 10px;
        background: #eff6ff;
        color: #1e3a8a;
    }
    .roundtable-now-label {
        color: #475569;
        font-size: 0.78rem;
        margin-bottom: 2px;
    }
    .roundtable-now-role {
        font-size: 1rem;
        font-weight: 750;
    }
    .roundtable-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
        gap: 8px;
    }
    .speaker-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 8px 9px;
        min-height: 64px;
        background: #f8fafc;
        color: #334155;
    }
    .speaker-card-active {
        border-color: #2563eb;
        background: #eff6ff;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
    }
    .speaker-card-next {
        border-color: #f59e0b;
        background: #fffbeb;
    }
    .speaker-card-done {
        border-color: #bbf7d0;
        background: #f0fdf4;
    }
    .speaker-card-waiting {
        opacity: 0.78;
    }
    .speaker-topline {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        align-items: center;
        margin-bottom: 4px;
    }
    .speaker-role {
        font-weight: 750;
        color: #111827;
        line-height: 1.2;
        font-size: 0.88rem;
    }
    .speaker-icon {
        font-size: 1.15rem;
    }
    .speaker-status {
        display: inline-block;
        border-radius: 999px;
        padding: 1px 7px;
        font-size: 0.72rem;
        background: #e2e8f0;
        color: #475569;
        margin-bottom: 3px;
    }
    .speaker-card-active .speaker-status {
        background: #2563eb;
        color: #ffffff;
    }
    .speaker-card-next .speaker-status {
        background: #f59e0b;
        color: #111827;
    }
    .speaker-card-done .speaker-status {
        background: #16a34a;
        color: #ffffff;
    }
    .speaker-phase {
        color: #64748b;
        font-size: 0.72rem;
        line-height: 1.25;
    }
    .phase-lane-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(110px, 1fr));
        gap: 8px;
    }
    .phase-lane {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 9px;
        background: #f8fafc;
        min-height: 170px;
        max-height: 430px;
        overflow-y: auto;
    }
    .phase-lane-active {
        border-color: #2563eb;
        background: #eff6ff;
    }
    .phase-lane-done {
        border-color: #bbf7d0;
        background: #f0fdf4;
    }
    .phase-lane-title {
        color: #111827;
        font-size: 0.9rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 3px;
    }
    .phase-lane-subtitle {
        color: #64748b;
        font-size: 0.72rem;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .phase-agent-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 6px;
    }
    @media (max-width: 720px) {
        .roundtable-header {
            display: block;
        }
        .roundtable-now {
            margin-top: 8px;
        }
        .phase-lane-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize system
if "panel" not in st.session_state:
    st.session_state.panel = EnhancedMedicalPanel()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "result_artifacts" not in st.session_state:
    st.session_state.result_artifacts = None

if "current_status" not in st.session_state:
    st.session_state.current_status = None

if "status_history" not in st.session_state:
    st.session_state.status_history = []

# Roles and Icons Mapping
ROLE_ICONS = {
    "Moderator": "🎤",
    "Intake Analyzer": "📋",
    "需求萃取分析師": "📋",
    "Clinical-Technical Expert": "🩺",
    "臨床技術專家": "🩺",
    "Regulatory-Business Expert": "⚖️",
    "法規商業專家": "⚖️",
    "Human-Patient Expert": "🌐",
    "人因病患專家": "🌐",
    "Option Formation Agent": "🧱",
    "方案形成代理人": "🧱",
    "Critical Review Agent": "🔍",
    "批判審查代理人": "🔍",
    "Consolidated Evaluator": "🎯",
    "整合評估者": "🎯",
    # Legacy role names kept so old reports / saved messages still render with icons.
    "Needs Source Agent": "🧩",
    "臨床現象整理代理人": "🧩",
    "Case Packet Extractor": "📋",
    "臨床特徵萃取代理人": "📋",
    "Clinical Physician": "🩺",
    "Biomedical Engineer": "⚙️",
    "Regulatory Expert": "⚖️",
    "法規專家": "⚖️",
    "Market & IP Expert": "📊",
    "市場與智財專家": "📊",
    "Human Factors Expert": "🧪",
    "人因工程專家": "🧪",
    "Patient & Access Expert": "🌐",
    "病患體驗與可近性專家": "🌐",
    "Devil's Advocate": "🔥",
    "Fact Checker": "🔍",
    "事實查核員": "🔍",
    "Bias Detector": "🧭",
    "偏誤偵測員": "🧭",
    "Identify Portfolio Agent": "🗂️",
    "需求檔案代理人": "🗂️",
}

PARTICIPANT_ROLES = [
    "Intake Analyzer",
    "Clinical-Technical Expert",
    "Regulatory-Business Expert",
    "Human-Patient Expert",
    "Option Formation Agent",
    "Critical Review Agent",
    "Consolidated Evaluator",
]

ROUNDTABLE_DISPLAY_ROLES = [
    "Intake Analyzer",
    "Clinical-Technical Expert",
    "Regulatory-Business Expert",
    "Human-Patient Expert",
    "Option Formation Agent",
    "Critical Review Agent",
    "Consolidated Evaluator",
]

st.title("🧬 Biodesign 7-Agent Collaboration System")
st.subheader("STB Biodesign Identify Workspace: Observation to Top Need")

# Sidebar: Participants
with st.sidebar:
    st.markdown("### 🗣️ Reduced Agent Panel")
    st.caption("7 merged agents")
    REDUCED_AGENTS = [
        ("Intake Analyzer", "📋", "Case Packet + Needs Source"),
        ("Clinical-Technical Expert", "🩺", "Clinical Physician + Biomedical Engineer"),
        ("Regulatory-Business Expert", "⚖️", "Regulatory + Market/IP"),
        ("Human-Patient Expert", "🌐", "Human Factors + Patient Access"),
        ("Option Formation Agent", "🧱", "3-5 Invent options"),
        ("Critical Review Agent", "🔍", "Devil's Advocate + Fact Checker + Bias Detector"),
        ("Consolidated Evaluator", "🎯", "MCDM + ranking + final decision"),
    ]
    for role, icon, covers in REDUCED_AGENTS:
        st.markdown(
            f"**{icon} {role}**  \n"
            f"<span style='color:#9ca3af;font-size:0.78rem'>{covers}</span>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.header("MCDM Weights")
    system_impact = st.slider("System Impact", 0, 100, 40, 5)
    implementability = st.slider("Implementability", 0, 100, 25, 5)
    risk_control = st.slider("Risk Control", 0, 100, 20, 5)
    innovation = st.slider("Innovation", 0, 100, 10, 5)
    cost_benefit = st.slider("Cost-Benefit", 0, 100, 5, 5)
    mcdm_weights = {
        "System Impact": system_impact,
        "Implementability": implementability,
        "Risk Control": risk_control,
        "Innovation": innovation,
        "Cost-Benefit": cost_benefit,
    }
    st.caption(f"Normalized automatically. Current total: {sum(mcdm_weights.values())}%")

    st.divider()
    st.header("Pipeline Mode")
    identify_only = st.toggle(
        "Identify Only",
        value=True,
        help="Turn off to run the full Identify → Invent pipeline: brainstorm, multi-round solution debate, and MCDM convergence.",
    )
    if identify_only:
        st.caption("🔒 Invent phase disabled. Toggle off to enable solution debate & MCDM.")
    else:
        st.caption("✅ Full pipeline: Identify → Invent (Brainstorm → Options → Debate → MCDM)")

    st.divider()
    st.header("Debate Rounds")
    debate_rounds = st.slider(
        "Identify Debate Rounds",
        min_value=2,
        max_value=4,
        value=2,
        step=1,
        help="2 rounds = initial position + cross-challenge. 3 rounds adds revision. 4 rounds is deepest but slowest.",
    )
    if not identify_only:
        invent_rounds = st.slider(
            "Invent Solution Debate Rounds",
            min_value=2,
            max_value=4,
            value=2,
            step=1,
            help="2 rounds = initial critique + cross-challenge. 3 rounds adds final revision.",
        )
    else:
        invent_rounds = 2

    st.divider()
    st.header("Evidence Grounding")
    enable_grounding = st.toggle(
        "Use external evidence APIs",
        value=os.getenv("ENABLE_EVIDENCE_GROUNDING", "0").lower() not in {"0", "false", "no"},
        help="Sends extracted claim queries to PubMed/openFDA and optional TFDA endpoint.",
    )
    evidence_budget = st.slider("Max external evidence queries", 0, 30, int(os.getenv("EVIDENCE_MAX_QUERIES", "12")), 1)

    st.divider()
    agenda_sidebar = st.empty()
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.current_status = None
        st.session_state.status_history = []
        st.rerun()


def stage_key(phase):
    phase = phase or ""
    if "臨床現象" in phase or "Phenomenon" in phase or "臨床特徵" in phase or "Feature Extraction" in phase:
        return "Phenomenon Analysis"
    if "專家立場" in phase or "立場" in phase or "Position" in phase:
        return "Expert Review"
    if ("證據缺口" in phase or "批判" in phase or "Critique" in phase or "Evidence Gaps" in phase) and "Invent" not in phase:
        return "Risk & Evidence"
    if "需求篩選" in phase or "Need Screening" in phase or "定義需求" in phase or "Formulating" in phase or "Portfolio" in phase or "需求檔案" in phase or "Need Synthesis" in phase or "Synthesis" in phase:
        return "Screening"
    return "Workflow"


def render_phase_chips(status):
    stages = ["Phenomenon Analysis", "Expert Review", "Risk & Evidence", "Screening"]
    current_stage = stage_key(status.get("phase"))
    completed = {stage_key(item.get("phase")) for item in status.get("agenda", [])[: max(status.get("step", 1) - 1, 0)]}
    chips = []
    for stage in stages:
        css_class = "phase-chip"
        prefix = "○"
        if stage in completed:
            css_class += " phase-chip-done"
            prefix = "✓"
        if stage == current_stage and not status.get("done"):
            css_class += " phase-chip-active"
            prefix = "▶"
        chips.append(f"<span class='{css_class}'>{prefix} {stage}</span>")
    return "".join(chips)


def render_agenda_table(status):
    rows = []
    for idx, item in enumerate(status.get("agenda", []), start=1):
        if idx < status.get("step", 0):
            state = "Done"
        elif idx == status.get("step") and not status.get("done"):
            state = "In Progress"
        else:
            state = "Waiting"
        rows.append({
            "Step": idx,
            "Status": state,
            "Phase": item.get("phase", ""),
            "Role": item.get("role", ""),
            "Action": item.get("action", ""),
        })
    return rows


def render_roundtable_dashboard(status, cjk_output=False):
    agenda = status.get("agenda", [])
    current_step = status.get("step", 1)
    current_role = status.get("role", "")
    next_role = status.get("next_role")
    current_phase = status.get("phase", "")
    current_action = status.get("action", "")
    done = status.get("done")
    labels = {
        "active": "發言中" if cjk_output else "Speaking",
        "next": "下一位" if cjk_output else "Next",
        "done": "已發言" if cjk_output else "Done",
        "waiting": "等待" if cjk_output else "Waiting",
        "title": "圓桌儀錶板" if cjk_output else "Roundtable Dashboard",
        "subtitle": "即時顯示目前發言者、下一位與各專家狀態" if cjk_output else "Live speaker, next speaker, and expert status",
        "now": "目前發言" if cjk_output else "Now speaking",
    }

    phase_lanes = [
        {
            "key": "phenomenon",
            "title": "1. 臨床現象分析" if cjk_output else "1. Phenomenon",
            "subtitle": "整理原始觀察與問題情境" if cjk_output else "Structure observation and context",
            "match": lambda phase: "臨床現象" in phase or "Phenomenon" in phase or "臨床特徵" in phase or "Feature Extraction" in phase or "待命：臨床現象" in phase,
            "fallback_roles": ["Intake Analyzer"],
        },
        {
            "key": "positions",
            "title": "2. 專家立場圓桌" if cjk_output else "2. Expert Positions",
            "subtitle": "多專家提出工作流、風險與證據需求" if cjk_output else "Experts frame workflow, risk, evidence needs",
            "match": lambda phase: "專家立場" in phase or "立場" in phase or "Position" in phase or "待命：專家立場" in phase,
            "fallback_roles": [
                "Clinical-Technical Expert",
                "Regulatory-Business Expert",
                "Human-Patient Expert",
            ],
        },
        {
            "key": "critique",
            "title": "3. 批判與證據缺口" if cjk_output else "3. Critique & Evidence",
            "subtitle": "挑戰假設、標記偏誤與關鍵缺口" if cjk_output else "Challenge assumptions and evidence gaps",
            "match": lambda phase: ("證據缺口" in phase or "批判" in phase or "Critique" in phase or "Evidence Gaps" in phase or "待命：批判" in phase) and "Invent" not in phase,
            "fallback_roles": [
                "Critical Review Agent",
            ],
        },
        {
            "key": "synthesis",
            "title": "4. 需求篩選與檔案" if cjk_output else "4. Screening & Portfolio",
            "subtitle": "整合 Need Statement、篩選與驗證計畫" if cjk_output else "Synthesize need, screening, validation plan",
            "match": lambda phase: (
                "需求篩選" in phase
                or "Need Screening" in phase
                or "定義需求" in phase
                or "Formulating" in phase
                or "Portfolio" in phase
                or "需求檔案" in phase
                or "Screening & Portfolio" in phase
                or "待命：需求整合" in phase
                or "Need Synthesis" in phase
                or "Synthesis" in phase
            ),
            "fallback_roles": ["Consolidated Evaluator"],
        },
        {
            "key": "invent",
            "title": "5. Invent 方案辯論" if cjk_output else "5. Invent · Solution Debate",
            "subtitle": "方案發散→整合→多輪辯論→MCDM 收斂" if cjk_output else "Brainstorm → Formation → Debate → MCDM",
            "match": lambda phase: (
                "Invent" in phase
                or "方案發散" in phase
                or "方案整合" in phase
                or "方案辯論" in phase
                or "MCDM 收斂" in phase
                or "Solution Debate" in phase
                or "Brainstorm" in phase
                or "MCDM Convergence" in phase
            ),
            "fallback_roles": [
                "Clinical-Technical Expert",
                "Regulatory-Business Expert",
                "Human-Patient Expert",
                "Option Formation Agent",
                "Critical Review Agent",
                "Consolidated Evaluator",
            ],
        },
    ]

    def lane_key_for_phase(phase):
        phase = phase or ""
        for lane in phase_lanes:
            if lane["match"](phase):
                return lane["key"]
        return "positions"

    completed_items = agenda[: max(current_step - 1, 0)]
    completed_pairs = {
        (lane_key_for_phase(item.get("phase", "")), item.get("role", ""))
        for item in completed_items
        if item.get("role")
    }
    active_lane_key = lane_key_for_phase(current_phase)
    next_lane_key = lane_key_for_phase(status.get("next_phase", "") or "")

    roles_by_lane = {lane["key"]: [] for lane in phase_lanes}
    phase_by_pair = {}
    for item in agenda:
        role = item.get("role", "")
        if not role:
            continue
        lane_key = lane_key_for_phase(item.get("phase", ""))
        if role not in roles_by_lane[lane_key]:
            roles_by_lane[lane_key].append(role)
        phase_by_pair[(lane_key, role)] = item.get("phase", "")
    for lane in phase_lanes:
        if not roles_by_lane[lane["key"]]:
            roles_by_lane[lane["key"]] = list(lane["fallback_roles"])
            for role in lane["fallback_roles"]:
                phase_by_pair[(lane["key"], role)] = lane["title"]

    def render_speaker_card(role, lane_key):
        if done and (lane_key, role) in completed_pairs:
            card_state = "done"
            state_label = labels["done"]
        elif role == current_role and lane_key == active_lane_key and not done:
            card_state = "active"
            state_label = labels["active"]
        elif role == next_role and lane_key == next_lane_key and not done:
            card_state = "next"
            state_label = labels["next"]
        elif (lane_key, role) in completed_pairs or done:
            card_state = "done"
            state_label = labels["done"]
        else:
            card_state = "waiting"
            state_label = labels["waiting"]
        icon = ROLE_ICONS.get(role, "🤖")
        role_html = html.escape(role)
        phase_html = html.escape(phase_by_pair.get((lane_key, role), ""))
        return (
            f'<div class="speaker-card speaker-card-{card_state}">'
            f'<div class="speaker-topline">'
            f'<div class="speaker-role">{role_html}</div>'
            f'<div class="speaker-icon">{icon}</div>'
            f'</div>'
            f'<div class="speaker-status">{state_label}</div>'
            f'<div class="speaker-phase">{phase_html}</div>'
            f'</div>'
        )

    lane_html = []
    completed_lane_keys = {lane_key_for_phase(item.get("phase", "")) for item in completed_items}
    for lane in phase_lanes:
        lane_key = lane["key"]
        lane_state = "active" if lane_key == active_lane_key and not done else "done" if lane_key in completed_lane_keys or done else "waiting"
        cards = "".join(render_speaker_card(role, lane_key) for role in roles_by_lane[lane_key])
        lane_html.append(
            f'<div class="phase-lane phase-lane-{lane_state}">'
            f'<div class="phase-lane-title">{html.escape(lane["title"])}</div>'
            f'<div class="phase-lane-subtitle">{html.escape(lane["subtitle"])}</div>'
            f'<div class="phase-agent-grid">{cards}</div>'
            f'</div>'
        )

    if current_role:
        current_role_text = html.escape(current_role)
    elif done:
        current_role_text = "討論完成" if cjk_output else "Complete"
    else:
        current_role_text = "尚未開始" if cjk_output else "Not started"
    current_phase_text = html.escape(current_phase)
    current_action_text = html.escape(current_action)
    return (
        '<div class="roundtable-dashboard">'
        '<div class="roundtable-header">'
        '<div>'
        f'<div class="roundtable-title">{labels["title"]}</div>'
        f'<div class="roundtable-subtitle">{labels["subtitle"]}</div>'
        '</div>'
        '<div class="roundtable-now">'
        f'<div class="roundtable-now-label">{labels["now"]}</div>'
        f'<div class="roundtable-now-role">{ROLE_ICONS.get(current_role, "🤖")} {current_role_text}</div>'
        f'<div class="roundtable-subtitle">{current_phase_text} · {current_action_text}</div>'
        '</div>'
        '</div>'
        f'<div class="phase-lane-grid">{"".join(lane_html)}</div>'
        '</div>'
    )


def build_idle_roundtable_status():
    idle_agenda = (
        [{"phase": "Standby: Phenomenon Analysis", "role": "Intake Analyzer", "action": "Waiting"}]
        + [
            {"phase": "Standby: Expert Positions", "role": role, "action": "Waiting"}
            for role in [
                "Clinical-Technical Expert",
                "Regulatory-Business Expert",
                "Human-Patient Expert",
            ]
        ]
        + [
            {"phase": "Standby: Critique & Evidence", "role": role, "action": "Waiting"}
            for role in [
                "Critical Review Agent",
            ]
        ]
        + [
            {"phase": "Standby: Need Synthesis", "role": role, "action": "Waiting"}
            for role in ["Consolidated Evaluator"]
        ]
    )
    return {
        "step": 0,
        "total": len(idle_agenda),
        "phase": "Awaiting start",
        "role": "",
        "action": "Fill in the STB Identify Intake form to begin the roundtable",
        "next_role": "Intake Analyzer",
        "next_phase": "Phenomenon Analysis",
        "agenda": idle_agenda,
        "done": False,
    }


def read_text_file(path):
    if not path or not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_latest_artifacts():
    report_paths = sorted(glob.glob("reports/biodesign_report_*.md"), reverse=True)
    for report_path in report_paths:
        timestamp_match = re.search(r"biodesign_report_(\d{8}_\d{6})\.md$", report_path)
        if not timestamp_match:
            continue
        timestamp = timestamp_match.group(1)
        log_path = f"reports/biodesign_discovery_log_{timestamp}.json"
        portfolio_path = f"reports/biodesign_identify_portfolio_{timestamp}.md"
        report_markdown = read_text_file(report_path)
        discovery_json = read_text_file(log_path)
        portfolio_markdown = read_text_file(portfolio_path)
        if not report_markdown:
            continue
        discovery_log = {}
        if discovery_json:
            try:
                discovery_log = json.loads(discovery_json)
            except json.JSONDecodeError:
                discovery_log = {}
        if not portfolio_markdown:
            portfolio_markdown = (
                "# STB Identify Portfolio\n\n"
                f"{discovery_log.get('identify_portfolio') or 'N/A'}"
            )
        observation = discovery_log.get("observation") or ""
        return {
            "timestamp": timestamp,
            "observation": observation,
            "report_path": report_path,
            "log_path": log_path,
            "portfolio_path": portfolio_path,
            "report_file_name": os.path.basename(report_path),
            "log_file_name": os.path.basename(log_path),
            "portfolio_file_name": os.path.basename(portfolio_path),
            "report_markdown": report_markdown,
            "discovery_json": discovery_json or "{}",
            "portfolio_markdown": portfolio_markdown,
            "discovery_log": discovery_log,
        }
    return None


def render_result_center():
    artifacts = st.session_state.get("result_artifacts")
    if not artifacts:
        artifacts = load_latest_artifacts()
        if artifacts:
            st.session_state.result_artifacts = artifacts
    if not artifacts:
        return

    st.markdown(
        f"""
        <div class="result-card">
            <div class="status-phase">Latest result · {artifacts.get('timestamp', '')}</div>
            <div class="status-role">Result Center</div>
            <div>{artifacts.get('observation', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    download_cols = st.columns(3)
    with download_cols[0]:
        st.download_button(
            label="Download Full Report (Markdown)",
            data=artifacts["report_markdown"],
            file_name=artifacts["report_file_name"],
            mime="text/markdown",
            key=f"download_report_{artifacts['timestamp']}",
        )
    with download_cols[1]:
        st.download_button(
            label="Download Discovery Log (JSON)",
            data=artifacts["discovery_json"],
            file_name=artifacts["log_file_name"],
            mime="application/json",
            key=f"download_log_{artifacts['timestamp']}",
        )
    with download_cols[2]:
        st.download_button(
            label="Download Identify Portfolio (Markdown)",
            data=artifacts["portfolio_markdown"],
            file_name=artifacts["portfolio_file_name"],
            mime="text/markdown",
            key=f"download_portfolio_{artifacts['timestamp']}",
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr(artifacts["report_file_name"], artifacts["report_markdown"])
        bundle.writestr(artifacts["log_file_name"], artifacts["discovery_json"])
        bundle.writestr(artifacts["portfolio_file_name"], artifacts["portfolio_markdown"])
    st.download_button(
        label="Download All Files (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=f"biodesign_outputs_{artifacts['timestamp']}.zip",
        mime="application/zip",
        key=f"download_bundle_{artifacts['timestamp']}",
    )

    discovery_log = artifacts.get("discovery_log") or {}
    if discovery_log.get("identify_portfolio"):
        with st.expander("View STB Identify Portfolio", expanded=False):
            portfolio_tabs = st.tabs(["Need Profile", "Screening", "Validation", "Criteria", "Full Portfolio"])
            with portfolio_tabs[0]:
                st.markdown(discovery_log.get("need_profile") or discovery_log["identify_portfolio"])
            with portfolio_tabs[1]:
                st.markdown(discovery_log.get("screening_result") or "N/A")
            with portfolio_tabs[2]:
                st.markdown(discovery_log.get("validation_plan") or "N/A")
            with portfolio_tabs[3]:
                st.markdown(discovery_log.get("need_criteria") or "N/A")
            with portfolio_tabs[4]:
                st.markdown(discovery_log["identify_portfolio"])

    if discovery_log.get("invent_mcdm_report") or discovery_log.get("invent_brainstorm_text"):
        st.markdown("### Invent Phase Results")
        hist_invent_tabs = st.tabs(["Brainstorm", "Option Formation", "Solution Debate", "MCDM Convergence"])
        with hist_invent_tabs[0]:
            st.markdown(discovery_log.get("invent_brainstorm_text") or "N/A")
        with hist_invent_tabs[1]:
            st.markdown(discovery_log.get("invent_options_text") or "N/A")
        with hist_invent_tabs[2]:
            st.markdown(discovery_log.get("invent_debate_summary") or "N/A")
        with hist_invent_tabs[3]:
            st.markdown(discovery_log.get("invent_mcdm_report") or "N/A")


def compact_intake_markdown(project_context, observation, known_constraints, evidence_available):
    rows = [
        ("Clinical Area", project_context.get("clinical_area")),
        ("Care Setting", project_context.get("care_setting")),
        ("Target Stakeholders", project_context.get("target_stakeholders")),
        ("Team Strengths", project_context.get("team_strengths")),
        ("Market Focus", project_context.get("market_focus")),
        ("Risk Appetite", project_context.get("risk_appetite")),
    ]
    focus_lines = "\n".join(f"- **{label}:** {value}" for label, value in rows if value)
    return (
        "### STB Identify Intake\n\n"
        f"{focus_lines or '- N/A'}\n\n"
        "### Clinical Observation\n\n"
        f"{observation}\n\n"
        "### Known Constraints\n\n"
        f"{known_constraints or 'N/A'}\n\n"
        "### Evidence Available\n\n"
        f"{evidence_available or 'N/A'}"
    )

# STB Identify Intake
with st.form("stb_identify_intake", clear_on_submit=False):
    st.markdown("### Clinical Observation")
    clinical_observation = st.text_area(
        "Clinical Observation",
        height=150,
        placeholder="Describe what you observed in a clinical setting. E.g.: During implant surgery, the surgeon repeatedly breaks sterile technique to reposition the overhead light, forcing glove changes or re-sterilization each time.",
        label_visibility="collapsed"
    )

    with st.expander("Advanced Settings & Project Context (Optional)", expanded=False):
        focus_cols = st.columns(2)
        with focus_cols[0]:
            clinical_area = st.text_input("Clinical Area", placeholder="e.g. Dental implants, ICU, Emergency, Rehabilitation")
            care_setting = st.text_input("Care Setting", placeholder="e.g. OR, Outpatient clinic, Ward, Home care")
            target_stakeholders = st.text_input("Target Stakeholders", placeholder="e.g. Surgeon, Nurse, Patient, Caregiver")
        with focus_cols[1]:
            team_strengths = st.text_input("Team Strengths", placeholder="e.g. AI, Mechanical design, Materials, Service design")
            market_focus = st.text_input("Market Focus", placeholder="e.g. Taiwan, USA, Asia, Global")
            risk_appetite = st.selectbox("Risk Appetite", ["Low regulatory risk", "Moderate risk", "High innovation / high risk"], index=1)

        lower_cols = st.columns(2)
        with lower_cols[0]:
            known_constraints = st.text_area(
                "Known Constraints",
                height=90,
                placeholder="e.g. Must not increase procedure time, cannot break sterile field, limited clinic space",
            )
        with lower_cols[1]:
            evidence_available = st.text_area(
                "Evidence Available",
                height=90,
                placeholder="e.g. 2 shadowing sessions, 1 physician interview, no quantitative data yet",
            )
    submitted = st.form_submit_button("Run Identify Agent", type="primary")

roundtable_overview = st.empty()
if st.session_state.current_status:
    roundtable_overview.markdown(
        render_roundtable_dashboard(st.session_state.current_status, False),
        unsafe_allow_html=True,
    )
else:
    roundtable_overview.markdown(
        render_roundtable_dashboard(build_idle_roundtable_status(), False),
        unsafe_allow_html=True,
    )

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=ROLE_ICONS.get(msg["role"], "🤖")):
        st.write(f"**{msg['role']}**")
        st.markdown(msg["content"])

if submitted:
    prompt = clinical_observation.strip()
    if not prompt:
        st.warning("Please fill in the Clinical Observation before running.")
        st.stop()
    project_context = {
        "clinical_area": clinical_area.strip(),
        "care_setting": care_setting.strip(),
        "target_stakeholders": target_stakeholders.strip(),
        "team_strengths": team_strengths.strip(),
        "market_focus": market_focus.strip(),
        "risk_appetite": risk_appetite.strip(),
    }
    intake_markdown = compact_intake_markdown(project_context, prompt, known_constraints.strip(), evidence_available.strip())
    cjk_output = bool(re.search(r"[\u4e00-\u9fff]", prompt))
    st.session_state.current_status = None
    st.session_state.status_history = []
    st.session_state.panel.evidence_grounder.enabled = enable_grounding
    st.session_state.panel.evidence_grounder.max_queries = evidence_budget
    st.session_state.panel.evidence_grounder.query_count = 0
    st.session_state.panel.evidence_grounder.cache = {}
    st.session_state.messages.append({"role": "user", "content": intake_markdown})

    # Show user input
    with st.chat_message("user", avatar="👤"):
        st.markdown(intake_markdown)
    
    # Callback to update UI
    def update_ui(role, message):
        st.session_state.messages.append({"role": role, "content": message})
        with st.chat_message(role, avatar=ROLE_ICONS.get(role, "🤖")):
            st.write(f"**{role}**")
            # Display message preserving markdown formatting
            st.markdown(message)

    progress_bar = st.progress(0, text="正在準備專家小組..." if cjk_output else "Preparing expert panel...")
    roundtable_panel = roundtable_overview
    status_card = st.empty()
    phase_panel = st.empty()
    agenda_panel = st.empty()
    recent_panel = st.empty()

    def render_agenda(status):
        agenda_lines = []
        for idx, item in enumerate(status["agenda"], start=1):
            role_icon = ROLE_ICONS.get(item["role"], "🤖")
            if idx < status["step"]:
                marker = "✓"
            elif idx == status["step"] and not status["done"]:
                marker = "▶"
            else:
                marker = "○"
            agenda_lines.append(
                f"{marker} **{idx}. {role_icon} {item['role']}**  \n"
                f"<span style='color:#6b7280'>{item['phase']} · {item['action']}</span>"
            )
        return "\n\n".join(agenda_lines)

    def update_status(status):
        st.session_state.current_status = status
        st.session_state.status_history.append({
            "step": status.get("step"),
            "phase": status.get("phase"),
            "role": status.get("role"),
            "action": status.get("action"),
            "done": status.get("done"),
        })
        st.session_state.status_history = st.session_state.status_history[-8:]
        current_icon = ROLE_ICONS.get(status["role"], "🤖")
        next_role = status.get("next_role") or "None"
        next_icon = ROLE_ICONS.get(next_role, "🤖") if next_role != "None" else "—"
        next_text = "Discussion complete" if status["done"] else f"{next_icon} {next_role}"
        step_label = "步驟" if cjk_output else "Step"
        next_label = "下一位" if cjk_output else "Next"
        agenda_title = "討論議程" if cjk_output else "Discussion Agenda"
        live_agenda_title = "即時議程" if cjk_output else "Live Agenda"
        progress_bar.progress(
            status["step"] / status["total"],
            text=f"{step_label} {status['step']} / {status['total']} · {status['action']}",
        )
        roundtable_panel.markdown(render_roundtable_dashboard(status, cjk_output), unsafe_allow_html=True)
        status_card.markdown(
            f"""
            <div class="status-card">
                <div class="status-phase">{status['phase']}</div>
                <div class="status-role">{current_icon} {status['role']}</div>
                <div>{status['action']}</div>
                <div class="status-next">{step_label}: {status['step']} / {status['total']}</div>
                <div class="status-next">{next_label}: {next_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        phase_panel.markdown(render_phase_chips(status), unsafe_allow_html=True)
        agenda_md = render_agenda(status)
        with agenda_panel.container():
            st.markdown(f"### {agenda_title}")
            st.dataframe(render_agenda_table(status), hide_index=True, use_container_width=True)
        with recent_panel.container():
            st.markdown("### 最近進度" if cjk_output else "### Recent Progress")
            st.dataframe(st.session_state.status_history, hide_index=True, use_container_width=True)
        agenda_sidebar.markdown(f"### {live_agenda_title}\n\n{agenda_md}", unsafe_allow_html=True)

    # Start discussion
    spinner_text = "專家會議進行中..." if cjk_output else "Expert meeting in progress..."
    with st.spinner(spinner_text):
        try:
            full_report = st.session_state.panel.run_discussion(
                prompt,
                callback=update_ui,
                status_callback=update_status,
                mcdm_weights=mcdm_weights,
                identify_only=identify_only,
                project_context=project_context,
                known_constraints=known_constraints.strip(),
                evidence_available=evidence_available.strip(),
                debate_rounds=debate_rounds,
                invent_rounds=invent_rounds,
            )
        except Exception as exc:
            st.error(f"Discussion failed: {exc}")
            st.stop()
        
    st.success("討論已完成，已產生最終需求陳述與評估。" if cjk_output else "Discussion concluded successfully! Final Need Statement and evaluation generated.")
    
    # Save report automatically
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/biodesign_report_{timestamp}.md"
    log_path = f"reports/biodesign_discovery_log_{timestamp}.json"
    portfolio_path = f"reports/biodesign_identify_portfolio_{timestamp}.md"
    report_markdown = f"# Biodesign Round-Table Report\n\n{intake_markdown}\n\n{full_report}"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    discovery_log = st.session_state.panel.last_discovery_log or {}
    if discovery_log:
        quality = discovery_log.get("need_statement_quality", {})
        st.markdown("### Need Statement Quality")
        if cjk_output:
            st.write(
                f"格式: {quality.get('format_ok')} · "
                f"不含解決方案: {quality.get('solution_free')} · "
                f"目標族群: {quality.get('has_target_population')} · "
                f"結果指標: {quality.get('has_measurable_outcome')} · "
                f"通過: {quality.get('passed')}"
            )
        else:
            st.write(
                f"Format: {quality.get('format_ok')} · "
                f"Solution-free: {quality.get('solution_free')} · "
                f"Population: {quality.get('has_target_population')} · "
                f"Outcome: {quality.get('has_measurable_outcome')} · "
                f"Pass: {quality.get('passed')}"
            )
        versions = discovery_log.get("need_statement_versions", [])
        if versions:
            with st.expander("Need Statement Version History"):
                for idx, item in enumerate(versions, start=1):
                    st.markdown(f"**{idx}. {item.get('phase')} · {item.get('role')}**")
                    st.markdown(item.get("statement", ""))
        if discovery_log.get("sensitivity_analysis"):
            with st.expander("MCDM Sensitivity Analysis"):
                st.json(discovery_log["sensitivity_analysis"])
        if discovery_log.get("evidence_grounding"):
            with st.expander("Evidence Grounding Results"):
                st.json(discovery_log["evidence_grounding"])
        if discovery_log.get("identify_portfolio"):
            st.markdown("### STB Identify Portfolio")
            portfolio_tabs = st.tabs(
                ["Need Profile", "Screening", "Validation", "Criteria", "Full Portfolio"]
            )
            with portfolio_tabs[0]:
                st.markdown(discovery_log.get("need_profile") or discovery_log["identify_portfolio"])
            with portfolio_tabs[1]:
                st.markdown(discovery_log.get("screening_result") or "N/A")
            with portfolio_tabs[2]:
                st.markdown(discovery_log.get("validation_plan") or "N/A")
            with portfolio_tabs[3]:
                st.markdown(discovery_log.get("need_criteria") or "N/A")
            with portfolio_tabs[4]:
                st.markdown(discovery_log["identify_portfolio"])

    if discovery_log.get("invent_mcdm_report") or discovery_log.get("invent_brainstorm_text"):
        st.success("✅ Invent phase complete — solution debate and MCDM convergence results below.")
        st.markdown("### 5. Invent Phase Results")
        invent_tabs = st.tabs(["📡 Brainstorm", "🧱 Option Formation", "⚔️ Solution Debate", "🎯 MCDM Convergence"])
        with invent_tabs[0]:
            st.markdown(discovery_log.get("invent_brainstorm_text") or "N/A")
        with invent_tabs[1]:
            st.markdown(discovery_log.get("invent_options_text") or "N/A")
        with invent_tabs[2]:
            st.markdown(discovery_log.get("invent_debate_summary") or "N/A")
        with invent_tabs[3]:
            st.markdown(discovery_log.get("invent_mcdm_report") or "N/A")
    elif not discovery_log.get("invent_mcdm_report"):
        st.info("ℹ️ Invent phase not run. Toggle off **Identify Only** in the sidebar and re-run to enable solution debate & MCDM convergence.")

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(discovery_log, f, ensure_ascii=False, indent=2)

    portfolio_markdown = (
        f"# STB Identify Portfolio\n\n"
        f"{intake_markdown}\n\n"
        f"{discovery_log.get('identify_portfolio') or 'N/A'}"
    )
    with open(portfolio_path, "w", encoding="utf-8") as f:
        f.write(portfolio_markdown)

    discovery_json = json.dumps(discovery_log, ensure_ascii=False, indent=2)
    st.session_state.result_artifacts = {
        "timestamp": timestamp,
        "observation": prompt,
        "report_path": report_path,
        "log_path": log_path,
        "portfolio_path": portfolio_path,
        "report_file_name": f"biodesign_report_{timestamp}.md",
        "log_file_name": f"biodesign_discovery_log_{timestamp}.json",
        "portfolio_file_name": f"biodesign_identify_portfolio_{timestamp}.md",
        "report_markdown": report_markdown,
        "discovery_json": discovery_json,
        "portfolio_markdown": portfolio_markdown,
        "discovery_log": discovery_log,
    }

    st.markdown("### 下載與結果" if cjk_output else "### Downloads and Results")
    render_result_center()

if not submitted:
    st.markdown("---")
    render_result_center()
