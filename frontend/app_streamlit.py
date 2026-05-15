import time
import streamlit as st
from datetime import date, datetime
import requests
import pandas as pd
import math
import calendar

API = "http://127.0.0.1:5002"

st.set_page_config(
    page_title="EMS Admin Panel",
    page_icon="🏭",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #07080f; }

.main .block-container {
    max-width: 1400px !important;
    width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 1.2rem !important;
    padding-bottom: 1rem !important;
    margin: 0 auto !important;
}

section[data-testid="stSidebar"] {
    background: #0b0c17 !important;
    border-right: 1px solid #181830;
}
[data-testid="metric-container"] {
    background: #0f1020;
    border: 1px solid #1e2040;
    border-radius: 14px;
    padding: 14px 18px;
}
.thin-div {
    height: 1px;
    background: linear-gradient(to right, transparent, #1e2040, transparent);
    margin: 4px 0;
}
.auth-glass {
    background: linear-gradient(135deg, #0f1020 0%, #141530 100%);
    border: 1px solid #1e2245;
    border-radius: 20px;
    padding: 40px 36px;
    box-shadow: 0 8px 48px #0005;
}
.auth-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 4px;
    margin-bottom: 4px;
}
.auth-sub {
    text-align: center;
    color: #444870;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 28px;
}
.sec-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 600;
    color: #818cf8;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.row-badge {
    display: inline-block;
    background: #1e2040;
    color: #818cf8;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
}
.stButton > button {
    font-size: 13px !important;
    padding: 6px 18px !important;
    border-radius: 8px !important;
}
.att-sep { height: 1px; background: #13142a; margin: 2px 0; }

/* ── Table: centered, proper size ── */
[data-testid="stDataFrame"] {
    width: 100% !important;
    max-width: 860px !important;
    margin: 0 auto !important;
    display: block !important;
}
[data-testid="stDataFrame"] > div {
    width: 100% !important;
    border: 2px solid #3a3d6b !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 12px #0005 !important;
}
[data-testid="stDataFrame"] iframe {
    width: 100% !important;
    min-width: 400px !important;
    min-height: 80px !important;
    max-height: 340px !important;
    font-size: 15px !important;
}
.stDataFrame {
    width: 100% !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}

/* increase table font size via iframe body */
[data-testid="stDataFrame"] iframe body {
    font-size: 15px !important;
}

/* ── Pagination bar compact ── */
.pg-bar .stButton > button {
    padding: 4px 14px !important;
    min-width: 70px !important;
    font-size: 12px !important;
}

/* reduce gap between elements */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.3rem !important;
}
</style>
""", unsafe_allow_html=True)

for k, v in [("s", requests.Session()), ("login", False), ("user", {})]:
    if k not in st.session_state:
        st.session_state[k] = v

def safe(res):
    try:
        d = res.json().get("data", [])
        return d if d else []
    except:
        return []

def api_msg(res):
    try:
        j = res.json()
        return j.get("massage") or j.get("message") or "Unknown error"
    except:
        return res.text or "Unknown error"

PAGE_SIZE = 5

def paginate(data, key):
    total       = len(data)
    total_pages = max(1, math.ceil(total / PAGE_SIZE))
    pg_key      = f"pg_{key}"

    if pg_key not in st.session_state:
        st.session_state[pg_key] = 1

    page = max(1, min(st.session_state[pg_key], total_pages))
    st.session_state[pg_key] = page

    start = (page - 1) * PAGE_SIZE
    chunk = data[start: start + PAGE_SIZE]

    pc1, pc2, pc3, pc4 = st.columns([1, 1, 2, 4])
    with pc1:
        if st.button("◀", key=f"prev_{key}", disabled=(page <= 1), use_container_width=True):
            st.session_state[pg_key] -= 1
            st.rerun()
    with pc2:
        if st.button("▶", key=f"next_{key}", disabled=(page >= total_pages), use_container_width=True):
            st.session_state[pg_key] += 1
            st.rerun()
    with pc3:
        st.markdown(
            f"<div style='color:#818cf8;font-family:JetBrains Mono,monospace;"
            f"font-size:12px;padding-top:8px;'>Page {page}/{total_pages}</div>",
            unsafe_allow_html=True
        )
    with pc4:
        st.markdown(
            f"<div style='color:#555880;font-family:JetBrains Mono,monospace;"
            f"font-size:12px;padding-top:8px;'>Total : {total} rows</div>",
            unsafe_allow_html=True
        )
    return chunk

if not st.session_state.login:
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at 20% 50%, #0d0e28 0%, #07080f 60%);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    _, C, _ = st.columns([2, 1.6, 2])
    with C:
        st.markdown("""
        <div class="auth-glass">
            <div class="auth-logo">EMS</div>
            <div class="auth-sub">Employee Management System</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab_l, tab_r = st.tabs(["🔐  Login", "📝  Register"])

        with tab_l:
            lu = st.text_input("Username", placeholder="Enter username", key="lu")
            lp = st.text_input("Password", type="password", placeholder="Enter password", key="lp")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Login", use_container_width=True, type="primary"):
                if not lu.strip() or not lp.strip():
                    st.error("Username and password required")
                else:
                    r = st.session_state.s.post(
                        f"{API}/Auth/login",
                        json={"username": lu.strip(), "password": lp}
                    )
                    if r.status_code == 200:
                        st.session_state.login = True
                        st.session_state.user  = r.json()["data"]
                        st.rerun()
                    else:
                        st.error(f"❌ {api_msg(r)}")

        with tab_r:
            ru   = st.text_input("Username", placeholder="Choose username",  key="ru")
            rp   = st.text_input("Password", type="password", placeholder="Choose password", key="rp")
            role = st.selectbox("Role", ["Employee", "admin", "superadmin"], key="rg_role")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝  Register", use_container_width=True, type="primary"):
                if not ru.strip() or not rp.strip():
                    st.error("Username and password required")
                else:
                    r = st.session_state.s.post(
                        f"{API}/Auth/register",
                        json={"username": ru.strip(), "password": rp, "role": role}
                    )
                    if r.status_code == 200:
                        st.success("✅ Registered! Switch to Login tab.")
                    else:
                        st.error(f"❌ {api_msg(r)}")
    st.stop()

with st.sidebar:
    rc    = "#818cf8" if st.session_state.user.get("role") == "superadmin" else "#34d399"
    rc_bg = "#818cf822" if st.session_state.user.get("role") == "superadmin" else "#34d39922"
    uname = st.session_state.user.get("username", "User")
    initials = uname[:2].upper()
    user_id   = st.session_state.user.get("id", "—")
    user_role = st.session_state.user.get("role", "—")

    st.markdown(f"""
    <div style="border:1px solid #1e2040;border-radius:14px;
                padding:14px 12px 12px;margin-bottom:12px;
                background:#0f1020;text-align:center;">
        <p style="margin:0 0 8px 0;">
            <span style="display:inline-block;background:#818cf8;border-radius:50%;
                         width:40px;height:40px;font-family:monospace;font-size:14px;
                         font-weight:bold;color:#fff;padding:10px 0;text-align:center;">
                {initials}
            </span>
        </p>
        <p style="margin:0 0 4px 0;font-family:monospace;font-size:12px;">
            <span style="color:#555880;">username :</span>
            <span style="color:#c7caf5;font-weight:bold;"> {uname}</span>
        </p>
        <p style="margin:0 0 10px 0;font-family:monospace;font-size:12px;">
            <span style="color:#555880;">id :</span>
            <span style="color:#c7caf5;font-weight:bold;"> {user_id}</span>
        </p>
        <span style="background:{rc_bg};color:{rc};padding:3px 12px;border-radius:20px;
                     font-size:9px;font-weight:bold;letter-spacing:1.5px;border:1px solid {rc}44;">
            {user_role}
        </span>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Employees", "🏢 Departments", "📅 Attendance", "💰 Salary"],
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ═══════════════════════════════════════════════════
#                   DASHBOARD
# ═══════════════════════════════════════════════════
if menu == "📊 Dashboard":

    st.markdown("<div class='sec-header'>📊 Live Dashboard</div>", unsafe_allow_html=True)

    employees = safe(st.session_state.s.get(
        f"{API}/employee/get/all", headers={"Cache-Control": "no-cache"}
    ))
    summary_res = st.session_state.s.get(
        f"{API}/attendance/today/summary", headers={"Cache-Control": "no-cache"}
    )

    if not employees:
        st.warning("⚠️ No employees found")
        st.stop()

    total_employees = len(employees)
    total_salary    = sum(e.get("salary", 0) for e in employees)

    present_today  = 0
    half_day_today = 0
    absent_today   = 0
    sick_today     = 0

    if summary_res.status_code == 200:
        s = summary_res.json().get("data", {})
        present_today  = s.get("present",    0)
        half_day_today = s.get("half_day",   0)
        absent_today   = s.get("absent",     0)
        sick_today     = s.get("sick_leave", 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Total Employees", total_employees)
    c2.metric("✅ Present Today",   present_today)
    c3.metric("💰 Total Salary",    f"₹ {total_salary:,.0f}")

    c4, c5, c6 = st.columns(3)
    c4.metric("🚫 Absent Today", absent_today)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div class='sec-header' style='font-size:16px;'>🏢 Department-wise Employee Count</div>",
        unsafe_allow_html=True
    )

    dept_count = {}
    for emp in employees:
        d = emp.get("department") or "Unknown"
        dept_count[d] = dept_count.get(d, 0) + 1

    if dept_count:
        pie_df = pd.DataFrame({
            "Department": list(dept_count.keys()),
            "Employees":  list(dept_count.values())
        })
        try:
            import altair as alt
            chart = alt.Chart(pie_df).mark_arc(innerRadius=55, outerRadius=130).encode(
                theta=alt.Theta("Employees:Q"),
                color=alt.Color(
                    "Department:N",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(
                        orient="right", titleColor="#818cf8", labelColor="#c0c4f0",
                        titleFontSize=13, labelFontSize=12
                    )
                ),
                tooltip=["Department:N", "Employees:Q"]
            ).properties(width=400, height=300, background="transparent").configure_view(strokeWidth=0)

            col_pie, col_tbl = st.columns([1.5, 1])
            with col_pie:
                st.altair_chart(chart, use_container_width=True)
            with col_tbl:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='row-badge'>📋 Total Departments : {len(pie_df)}</div>",
                    unsafe_allow_html=True
                )
                st.dataframe(
                    pie_df.sort_values("Employees", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        except ImportError:
            st.bar_chart(pie_df.set_index("Department"))
    else:
        st.info("No department data")

# ═══════════════════════════════════════════════════
#                   EMPLOYEES
# ═══════════════════════════════════════════════════
elif menu == "👥 Employees":

    st.markdown("<div class='sec-header'>👥 Employee Management</div>", unsafe_allow_html=True)

    tabs = st.tabs(["📋 All", "➕ Add", "🔎 Search", "✏️ Update", "🗑 Delete", "🏢 By Dept"])

    with tabs[0]:
        data = safe(st.session_state.s.get(f"{API}/employee/get/all"))
        if data:
            data = sorted(data, key=lambda x: x.get("id", 0))
            chunk = paginate(data, "emp_all")
            st.dataframe(pd.DataFrame(chunk), use_container_width=True, hide_index=True)
        else:
            st.info("No employees found")

    with tabs[1]:
        dept_data  = safe(st.session_state.s.get(f"{API}/department/all"))
        dept_names = [d["name"] for d in dept_data] if dept_data else []

        col1, col2 = st.columns(2)
        with col1:
            a_name  = st.text_input("👤 Name",  key="a_name")
            a_email = st.text_input("📧 Email", key="a_email")
            a_city  = st.text_input("🏙 City",  key="a_city")
        with col2:
            a_salary = st.number_input("💰 Salary", step=1000, min_value=0, key="a_salary")
            a_dept   = st.selectbox("🏢 Department", dept_names, key="a_dept") if dept_names else None

        if not dept_names:
            st.warning("⚠️ Add departments first")

        if st.button("➕ Add Employee", type="primary"):
            errs = []
            if not a_name.strip():  errs.append("Name required")
            if not a_email.strip(): errs.append("Email required")
            if not a_city.strip():  errs.append("City required")
            if not a_dept:          errs.append("Department required")
            if a_salary <= 0:       errs.append("Salary must be > 0")
            if errs:
                for e in errs: st.error(f"❌ {e}")
            else:
                r = st.session_state.s.post(
                    f"{API}/employee/add_emp",
                    json={"name": a_name.strip(), "city": a_city.strip(),
                          "email": a_email.strip(), "salary": a_salary, "department": a_dept}
                )
                st.success("✅ Employee Added!") if r.status_code in (200, 201) else st.error(f"❌ {api_msg(r)}")

    with tabs[2]:
        s_by = st.selectbox("Search By", ["Name", "ID", "Email", "City"], key="s_by")
        s_q  = st.text_input("Search Query", key="s_q", placeholder="Type here…")

        if st.button("🔎 Search", key="btn_srch"):
            if not s_q.strip():
                st.error("Enter search query")
            else:
                ep_map = {
                    "Name":  f"{API}/employee/search/{s_q.strip()}",
                    "ID":    f"{API}/employee/get/{s_q.strip()}",
                    "Email": f"{API}/employee/search/email/{s_q.strip()}",
                    "City":  f"{API}/employee/search/city/{s_q.strip()}",
                }
                res = safe(st.session_state.s.get(ep_map[s_by]))
                if isinstance(res, dict): res = [res]
                if res:
                    st.markdown(f"<div class='row-badge'>📋 Results : {len(res)}</div>", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else:
                    st.info("No employees found")

    with tabs[3]:
        dept_data  = safe(st.session_state.s.get(f"{API}/department/all"))
        dept_names = [d["name"] for d in dept_data] if dept_data else []

        with st.expander("🔍 ID search here", expanded=False):
            us_by = st.selectbox("Search By", ["Name", "Email", "City", "By Dept"], key="us_by")
            us_q  = st.text_input("Search Query", key="us_q", placeholder="Search to find ID…")
            if st.button("🔎 Search", key="btn_upd_srch"):
                if not us_q.strip():
                    st.error("Enter query")
                else:
                    ep2 = {
                        "Name":    f"{API}/employee/search/{us_q.strip()}",
                        "Email":   f"{API}/employee/search/email/{us_q.strip()}",
                        "City":    f"{API}/employee/search/city/{us_q.strip()}",
                        "By Dept": f"{API}/employee/by-department/{us_q.strip()}",
                    }
                    sres = safe(st.session_state.s.get(ep2[us_by]))
                    if sres:
                        show_cols = ["id", "name", "email", "city", "department"]
                        sdf = pd.DataFrame(sres)
                        show_cols = [c for c in show_cols if c in sdf.columns]
                        st.dataframe(sdf[show_cols], use_container_width=True, hide_index=True)
                    else:
                        st.info("No results found")

        st.markdown("##### ✏️ Update Employee")

        # render_key — fetch झाल्यावर बदलतो → Streamlit नवीन values नेच render करतो
        if "u_render_key" not in st.session_state:
            st.session_state["u_render_key"] = 0
        if "u_id_val" not in st.session_state:
            st.session_state["u_id_val"] = 1

        fc1, fc2 = st.columns([3, 1])
        with fc1:
            u_id = st.number_input(
                "🆔 Employee ID", step=1, min_value=1,
                value=st.session_state["u_id_val"], key="u_id"
            )
            st.session_state["u_id_val"] = u_id
        with fc2:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_clicked = st.button("🔍 Fetch Details", key="btn_fetch", type="primary", use_container_width=True)

        if fetch_clicked:
            fd = safe(st.session_state.s.get(f"{API}/employee/get/{u_id}"))
            fetched = fd if isinstance(fd, dict) else (fd[0] if fd else None)
            if fetched:
                st.session_state["prefill"]      = fetched
                st.session_state["prefill_id"]   = u_id
                # ✅ key बदलतो → widgets नवीन values नेच दाखवतात
                st.session_state["u_render_key"] += 1
                st.rerun()
            else:
                st.session_state.pop("prefill", None)
                st.session_state.pop("prefill_id", None)
                st.error(f"❌ Employee ID {u_id} not found")

        pf  = {}
        rk  = st.session_state["u_render_key"]   # widget key suffix
        if st.session_state.get("prefill_id") == u_id:
            pf = st.session_state.get("prefill") or {}

        # ✅ fetch झाल्यावर success banner
        if pf:
            st.markdown(
                f"<div style='background:#0a1a0f;border:1px solid #166534;border-radius:8px;"
                f"padding:8px 14px;margin-bottom:8px;font-size:13px;color:#4ade80;'>"
                f"✅ Details fetched for <b>{pf.get('name','')}</b> — edit below and click Update</div>",
                unsafe_allow_html=True
            )

        uc1, uc2 = st.columns(2)
        with uc1:
            u_name  = st.text_input("👤 Name",  value=pf.get("name",""),  key=f"u_name_{rk}")
            u_email = st.text_input("📧 Email", value=pf.get("email",""), key=f"u_email_{rk}")
            u_city  = st.text_input("🏙 City",  value=pf.get("city",""),  key=f"u_city_{rk}")
        with uc2:
            cur_sal = int(pf.get("salary", 0) or 0)
            u_salary = st.number_input("💰 Salary", step=1000, min_value=0, value=cur_sal, key=f"u_salary_{rk}")
            cur_di = 0
            if pf.get("department") and dept_names and pf["department"] in dept_names:
                cur_di = dept_names.index(pf["department"])
            u_dept = st.selectbox("🏢 Department", dept_names, index=cur_di, key=f"u_dept_{rk}") if dept_names else None

        if st.button("✏️ Update Employee", type="primary"):
            if not pf:
                st.error("❌ Please click 'Fetch Details' button first!")
            else:
                payload = {}
                if u_name.strip():  payload["name"]       = u_name.strip()
                if u_email.strip(): payload["email"]       = u_email.strip()
                if u_city.strip():  payload["city"]        = u_city.strip()
                if u_salary > 0:    payload["salary"]      = u_salary
                if u_dept:          payload["department"]  = u_dept
                if not payload:
                    st.error("❌ At least one field required")
                else:
                    r = st.session_state.s.put(f"{API}/employee/update/{u_id}", json=payload)
                    if r.status_code in (200, 201):
                        st.success("✅ Employee Updated!")
                        st.session_state.pop("prefill", None)
                        st.session_state.pop("prefill_id", None)
                        st.session_state["u_render_key"] += 1
                        st.rerun()
                    else:
                        st.error(f"❌ {api_msg(r)}")

    # ═══════════════════════════════════════════════════
    # 🗑 DELETE — confirm + role check
    # ═══════════════════════════════════════════════════
    with tabs[4]:
        current_role = st.session_state.user.get("role", "")

        # ✅ फक्त superadmin ला delete ची authority आहे
        if current_role != "superadmin":
            st.markdown("""
            <div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:12px;
                        padding:20px 24px;margin-top:10px;">
                <p style="color:#f87171;font-size:16px;font-weight:600;margin:0 0 6px 0;">
                    🔒 Access Denied
                </p>
                <p style="color:#fca5a5;font-size:13px;margin:0;">
                    Only <b>superadmin</b> has permission to delete employees.<br>
                    Your current role : <b>{role}</b>
                </p>
            </div>
            """.format(role=current_role), unsafe_allow_html=True)
        else:
            # Step 1 — ID टाका आणि details fetch करा
            if "del_emp_data" not in st.session_state:
                st.session_state["del_emp_data"] = None
            if "del_emp_id" not in st.session_state:
                st.session_state["del_emp_id"] = 1

            d_id = st.number_input(
                "🆔 Employee ID to Delete",
                step=1, min_value=1,
                value=st.session_state["del_emp_id"],
                key="d_id"
            )
            st.session_state["del_emp_id"] = d_id

            if st.button("🔍 Fetch Employee Details", key="btn_del_fetch", type="primary"):
                fd = safe(st.session_state.s.get(f"{API}/employee/get/{d_id}"))
                fetched = fd if isinstance(fd, dict) else (fd[0] if fd else None)
                if fetched:
                    st.session_state["del_emp_data"] = fetched
                else:
                    st.session_state["del_emp_data"] = None
                    st.error(f"❌ Employee ID {d_id} not found")

            # Step 2 — Details दाखवा आणि confirm करा
            del_data = st.session_state.get("del_emp_data")
            if del_data and st.session_state.get("del_emp_id") == d_id:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#100a0a;border:1px solid #7f1d1d;border-radius:12px;
                            padding:18px 22px;margin-bottom:12px;">
                    <p style="color:#f87171;font-size:13px;font-weight:700;
                               letter-spacing:1px;margin:0 0 10px 0;">
                        ⚠️  DELETE CONFIRMATION
                    </p>
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <tr>
                            <td style="color:#555880;padding:3px 0;width:120px;">ID</td>
                            <td style="color:#c7caf5;font-weight:600;">{del_data.get('id','—')}</td>
                        </tr>
                        <tr>
                            <td style="color:#555880;padding:3px 0;">Name</td>
                            <td style="color:#c7caf5;font-weight:600;">{del_data.get('name','—')}</td>
                        </tr>
                        <tr>
                            <td style="color:#555880;padding:3px 0;">Email</td>
                            <td style="color:#c7caf5;">{del_data.get('email','—')}</td>
                        </tr>
                        <tr>
                            <td style="color:#555880;padding:3px 0;">Department</td>
                            <td style="color:#818cf8;">{del_data.get('department','—')}</td>
                        </tr>
                        <tr>
                            <td style="color:#555880;padding:3px 0;">Salary</td>
                            <td style="color:#34d399;">₹ {del_data.get('salary',0):,.0f}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

                st.warning("⚠️ This employee will be permanently deleted. This action cannot be undone!")

                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("🗑 Confirm Delete", type="primary", use_container_width=True):
                        r = st.session_state.s.delete(f"{API}/employee/delete/{d_id}")
                        if r.status_code == 200:
                            st.success(f"✅ Employee '{del_data.get('name')}' deleted successfully!")
                            st.session_state["del_emp_data"] = None
                        else:
                            st.error(f"❌ {api_msg(r)}")
                with cc2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state["del_emp_data"] = None
                        st.rerun()

    with tabs[5]:
        dept_data = safe(st.session_state.s.get(f"{API}/department/all"))
        if not dept_data:
            st.warning("⚠️ No departments found")
        else:
            dn  = [d["name"] for d in dept_data]
            sel = st.selectbox("🏢 Select Department", dn, key="bd_sel")
            if st.button("📂 Load Employees", type="primary"):
                st.session_state["bd_data"] = safe(
                    st.session_state.s.get(f"{API}/employee/by-department/{sel}")
                )
                st.session_state["pg_bd"] = 1

            bd = st.session_state.get("bd_data")
            if bd is not None:
                if bd:
                    chunk = paginate(bd, "bd")
                    st.dataframe(pd.DataFrame(chunk), use_container_width=True, hide_index=True)
                else:
                    st.info("No employees in this department")

# ═══════════════════════════════════════════════════
#                   DEPARTMENTS
# ═══════════════════════════════════════════════════
elif menu == "🏢 Departments":

    st.markdown("<div class='sec-header'>🏢 Department Management</div>", unsafe_allow_html=True)

    tabs = st.tabs(["📋 All", "➕ Add", "🔍 Search / By ID", "✏️ Update", "🗑 Delete"])

    with tabs[0]:
        data = safe(st.session_state.s.get(f"{API}/department/all"))
        if data:
            data = sorted(data, key=lambda x: x.get("id", 0))
            chunk = paginate(data, "dept_all")
            st.dataframe(pd.DataFrame(chunk), use_container_width=True, hide_index=True)
        else:
            st.info("No departments found")

    with tabs[1]:
        dn = st.text_input("Department Name", key="d_add")
        if st.button("➕ Add Department", type="primary"):
            if not dn.strip():
                st.error("❌ Name required")
            else:
                r = st.session_state.s.post(f"{API}/department/add_dept", json={"name": dn.strip()})
                st.success("✅ Department Added!") if r.status_code in (200, 201) else st.error(f"❌ {api_msg(r)}")

    with tabs[2]:
        ds_by = st.selectbox("Search By", ["Name", "ID"], key="ds_by")
        ds_q  = st.text_input("Search Query", key="ds_q", placeholder="Enter name or ID…")
        if st.button("🔎 Search", key="btn_dsrch"):
            if not ds_q.strip():
                st.error("Enter query")
            else:
                if ds_by == "Name":
                    dres = safe(st.session_state.s.get(f"{API}/department/search/{ds_q.strip()}"))
                else:
                    dres = safe(st.session_state.s.get(f"{API}/department/{ds_q.strip()}"))
                    if isinstance(dres, dict): dres = [dres]
                if dres:
                    st.markdown(f"<div class='row-badge'>📋 Results : {len(dres)}</div>", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(dres), use_container_width=True, hide_index=True)
                else:
                    st.info("No departments found")

    with tabs[3]:
        du_id   = st.number_input("Department ID to Update", step=1, min_value=1, key="du_id")
        du_name = st.text_input("New Name", key="du_name")
        if st.button("✏️ Update Department", type="primary"):
            if not du_name.strip():
                st.error("❌ Name required")
            else:
                r = st.session_state.s.put(
                    f"{API}/department/update/{du_id}", json={"name": du_name.strip()}
                )
                st.success("✅ Updated!") if r.status_code == 200 else st.error(f"❌ {api_msg(r)}")

    # ═══════════════════════════════════════════════════
    # 🗑 DEPARTMENT DELETE — confirm + role check
    # ═══════════════════════════════════════════════════
    with tabs[4]:
        current_role = st.session_state.user.get("role", "")

        if current_role != "superadmin":
            st.markdown("""
            <div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:12px;
                        padding:20px 24px;margin-top:10px;">
                <p style="color:#f87171;font-size:16px;font-weight:600;margin:0 0 6px 0;">
                    🔒 Access Denied
                </p>
                <p style="color:#fca5a5;font-size:13px;margin:0;">
                    Only <b>superadmin</b> has permission to delete departments.<br>
                    Your current role : <b>{role}</b>
                </p>
            </div>
            """.format(role=current_role), unsafe_allow_html=True)
        else:
            if "del_dept_data" not in st.session_state:
                st.session_state["del_dept_data"] = None
            if "del_dept_id" not in st.session_state:
                st.session_state["del_dept_id"] = 1

            dd_id = st.number_input(
                "🆔 Department ID to Delete",
                step=1, min_value=1,
                value=st.session_state["del_dept_id"],
                key="dd_id"
            )
            st.session_state["del_dept_id"] = dd_id

            if st.button("🔍 Fetch Department Details", key="btn_ddel_fetch", type="primary"):
                fd = safe(st.session_state.s.get(f"{API}/department/{dd_id}"))
                fetched = fd if isinstance(fd, dict) else (fd[0] if fd else None)
                if fetched:
                    st.session_state["del_dept_data"] = fetched
                else:
                    st.session_state["del_dept_data"] = None
                    st.error(f"❌ Department ID {dd_id} not found")

            del_dept = st.session_state.get("del_dept_data")
            if del_dept and st.session_state.get("del_dept_id") == dd_id:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#100a0a;border:1px solid #7f1d1d;border-radius:12px;
                            padding:18px 22px;margin-bottom:12px;">
                    <p style="color:#f87171;font-size:13px;font-weight:700;
                               letter-spacing:1px;margin:0 0 10px 0;">
                        ⚠️  DELETE CONFIRMATION
                    </p>
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <tr>
                            <td style="color:#555880;padding:3px 0;width:120px;">ID</td>
                            <td style="color:#c7caf5;font-weight:600;">{del_dept.get('id','—')}</td>
                        </tr>
                        <tr>
                            <td style="color:#555880;padding:3px 0;">Name</td>
                            <td style="color:#c7caf5;font-weight:600;">{del_dept.get('name','—')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

                st.warning("⚠️ All employees in this department will lose their department link!")

                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("🗑 Confirm Delete", key="btn_dept_confirm", type="primary", use_container_width=True):
                        r = st.session_state.s.delete(f"{API}/department/delete/{dd_id}")
                        if r.status_code == 200:
                            st.success(f"✅ Department '{del_dept.get('name')}' deleted successfully!")
                            st.session_state["del_dept_data"] = None
                        else:
                            st.error(f"❌ {api_msg(r)}")
                with dc2:
                    if st.button("❌ Cancel", key="btn_dept_cancel", use_container_width=True):
                        st.session_state["del_dept_data"] = None
                        st.rerun()

# ═══════════════════════════════════════════════════
#                   ATTENDANCE
# ═══════════════════════════════════════════════════
elif menu == "📅 Attendance":

    st.markdown("<div class='sec-header'>📅 Attendance — Today</div>", unsafe_allow_html=True)
    st.caption(f"📆 {date.today().strftime('%d %B %Y')}")

    # HD option removed — backend auto-converts P to HD after 12 PM
    STATUS_OPTIONS = {
        "P  — Present":    "P",
        "A  — Absent":     "A",
        "SL — Sick Leave": "SL",
    }

    # Show info banner if after 12 PM
    now_hour = datetime.now().hour
    if now_hour >= 12:
        st.info(
            f"🕛 Current time is {datetime.now().strftime('%I:%M %p')} — "
            "Marking **Present** after 12 PM will automatically be saved as **Half Day**."
        )

    emp = safe(st.session_state.s.get(f"{API}/employee/get/all"))
    if not emp:
        st.warning("⚠️ No employees found")
        st.stop()

    df = pd.DataFrame(emp)

    h1, h2, h3, h4, h5 = st.columns([0.6, 3, 2, 2.5, 1.5])
    for col, label in zip([h1, h2, h3, h4, h5],
                          ["**ID**", "**Name**", "**Dept**", "**Status**", "**Save**"]):
        col.markdown(label)

    st.markdown("<div class='thin-div'></div>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([0.6, 3, 2, 2.5, 1.5])
        c1.markdown(f"`{row['id']}`")
        c2.markdown(f"**{row['name']}**")
        c3.markdown(f"<small style='color:#818cf8'>{row.get('department','—')}</small>", unsafe_allow_html=True)
        sl = c4.selectbox("", list(STATUS_OPTIONS.keys()), key=f"att_{row['id']}", label_visibility="collapsed")
        if c5.button("💾", key=f"sv_{row['id']}", use_container_width=True):
            res = st.session_state.s.post(
                f"{API}/attendance/mark",
                json={"employee_id": int(row["id"]), "status": STATUS_OPTIONS[sl]}
            )
            if res.status_code == 200:
                final_status = STATUS_OPTIONS[sl]
                res_data = res.json().get("data", {})
                if res_data.get("half_days", 0) > 0 and STATUS_OPTIONS[sl] == "P":
                    st.success(f"✅ **{row['name']}** — Present → **Half Day** (marked after 12 PM)")
                else:
                    st.success(f"✅ **{row['name']}** saved ({STATUS_OPTIONS[sl]})")
            else:
                msg = api_msg(res)
                if "already" in msg.lower():
                    st.warning(f"🔒 **{row['name']}** already marked today")
                else:
                    st.error(f"❌ {msg}")
        st.markdown("<div class='att-sep'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
#                   SALARY
# ═══════════════════════════════════════════════════
elif menu == "💰 Salary":

    st.markdown("<div class='sec-header'>💰 Salary Calculator</div>", unsafe_allow_html=True)

    # Month name dropdown (January, February...)
    MONTH_NAMES = {
        1: "January", 2: "February", 3: "March",    4: "April",
        5: "May",     6: "June",     7: "July",      8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        sal_id = st.number_input("Employee ID", step=1, min_value=1, key="sal_id")
    with c2:
        sal_yr = st.number_input(
            "Year", min_value=2020, max_value=datetime.now().year,
            value=datetime.now().year, step=1, key="sal_yr"
        )
    with c3:
        # ✅ Month dropdown — नाव दिसते, number जाते
        month_options = list(MONTH_NAMES.values())
        default_month_idx = datetime.now().month - 1
        sel_month_name = st.selectbox(
            "Month", month_options,
            index=default_month_idx,
            key="sal_mo_name"
        )
        sal_mo = month_options.index(sel_month_name) + 1

    if st.button("📤 Get Salary Details", type="primary"):
        r = st.session_state.s.get(
            f"{API}/attendance/salary/{sal_id}",
            params={"year": sal_yr, "month": sal_mo}
        )
        if r.status_code == 200:
            data = r.json().get("data", {})
            if not data:
                st.warning("⚠️ Salary data not available")
            else:
                # ✅ Month number → नाव दाखवा
                raw_month = data.get("month", "")
                try:
                    mo_num = int(raw_month.split("-")[1])
                    display_month = f"{MONTH_NAMES.get(mo_num, raw_month)} {sal_yr}"
                except:
                    display_month = raw_month

                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("👤 Employee",     data.get("employee_name", "—"))
                mc2.metric("💰 Base Salary",  f"₹ {data.get('base_salary', 0):,.0f}")
                mc3.metric("✅ Final Salary", f"₹ {data.get('final_salary', 0):,.0f}")

                mc4, mc5, mc6 = st.columns(3)
                mc4.metric("📅 Month",           display_month)
                mc5.metric("📉 Salary Cut",       f"₹ {data.get('salary_cut', 0):,.0f}")
                mc6.metric("⬇️ Deduction Days",   data.get("total_deduction_days", 0))

                st.divider()
                st.markdown("#### 📊 Attendance Breakdown")

                marked_days = (
                    data.get("half_days",       0) +
                    data.get("sick_leave_used", 0) +
                    data.get("absent_days",     0)
                )
                present_days = max(
                    0,
                    data.get("days_in_month", 0) - marked_days - data.get("extra_absents_cut", 0)
                )

                breakdown = {
                    "Status": [
                        "✅ Present Days",
                        "🌓 Half Days",
                        "💊 Sick Leave Used",
                        "🚫 Absent Days (paid)",
                        "⚠️ Extra Absents (unpaid)",
                    ],
                    "Count": [
                        present_days,
                        data.get("half_days",        0),
                        data.get("sick_leave_used",  0),
                        min(data.get("absent_days", 0), data.get("paid_absents_allowed", 2)),
                        data.get("extra_absents_cut", 0),
                    ]
                }
                st.dataframe(pd.DataFrame(breakdown), use_container_width=True, hide_index=True)
                st.info(
                    f"💡 Per Day Salary : ₹ {data.get('per_day_salary', 0):,.2f}  "
                    f"| Days in Month : {data.get('days_in_month', '—')}"
                )
        else:
            st.error(f"❌ {api_msg(r)}")