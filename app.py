import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- 1. CONFIG & DARK MODE MAGIC ---
st.set_page_config(page_title="Zero", page_icon="⭕", layout="centered")

st.markdown("""
    <style>
    /* DEEP BLACK MODE */
    .stApp { background-color: #000000; color: #e0e0e0; }
    
    /* HIDE STREAMLIT UI CLUTTER */
    header {visibility: hidden;}
    .stApp > footer {display: none;}
    [data-testid="stToolbar"] {visibility: hidden;} /* Hides top right menu */
    
    /* MOBILE OPTIMIZATION */
    div.block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* PREMIUM BUTTONS */
    .stButton button {
        width: 100%;
        height: 3.5rem;
        border-radius: 16px; /* Softer corners */
        font-weight: 700;
        background: linear-gradient(45deg, #1a1a1a, #2a2a2a);
        border: 1px solid #333;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.1s;
    }
    .stButton button:active { transform: scale(0.98); } /* Click effect */
    
    /* NEON ACCENTS */
    [data-testid="stMetricValue"] { 
        font-size: 2.8rem !important; 
        font-family: 'Helvetica Neue', sans-serif;
        background: -webkit-linear-gradient(#00FF94, #00CC7A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* PILLS (SELECTION BUTTONS) STYLING */
    [data-testid="stStSelectbox"] { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    try: return conn.read(worksheet=worksheet_name, ttl=0)
    except: return pd.DataFrame()

def write_log(intensity, trigger, action, resisted, location):
    try:
        df = get_data("Logs")
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Intensity": intensity, "Trigger": trigger,
            "Action": action, "Resisted": resisted, "Location": location
        }])
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        conn.update(worksheet="Logs", data=updated_df)
        st.cache_data.clear()
        return True
    except: return False

def update_settings(quit_date, cost, cigs):
    try:
        new_settings = pd.DataFrame([
            {"Key": "quit_date", "Value": str(quit_date)},
            {"Key": "cost_per_pack", "Value": str(cost)},
            {"Key": "cigs_per_day", "Value": str(cigs)}
        ])
        conn.update(worksheet="Settings", data=new_settings)
        st.cache_data.clear()
        return True
    except: return False

# --- 3. PROGRESS ENGINE ---
def get_progress(settings_dict):
    q_date = settings_dict.get('quit_date', '2024-01-01')
    cost = float(settings_dict.get('cost_per_pack', 12.0))
    daily = float(settings_dict.get('cigs_per_day', 15.0))
    
    try: quit_dt = datetime.strptime(q_date, "%Y-%m-%d")
    except: quit_dt = datetime(2024, 1, 1)

    delta = datetime.now() - quit_dt
    days = delta.days
    money = days * (cost / 20 * daily)
    avoided = days * daily
    hours = delta.total_seconds() / 3600
    return days, money, avoided, hours, quit_dt, cost, daily

def get_level(days):
    if days < 1: return "🌱 The Seed", 0.0
    if days < 3: return "🛡️ The Survivor", 0.1
    if days < 7: return "⚔️ The Warrior", 0.25
    if days < 14: return "🦅 The Falcon", 0.50
    if days < 30: return "🔥 The Phoenix", 0.75
    return "👑 The Legend", 1.0

def get_quote():
    quotes = [
        "The urge is temporary. The pride is forever.",
        "Not another puff, no matter what.",
        "You are not giving up something. You are getting free.",
        "Pain is weakness leaving the body."
    ]
    return random.choice(quotes)

# --- 4. APP UI ---

# Load Settings
df_set = get_data("Settings")
my_settings = dict(zip(df_set['Key'], df_set['Value'])) if not df_set.empty else {}
days, money, avoided, hours, q_date_obj, s_cost, s_daily = get_progress(my_settings)
level_name, level_progress = get_level(days)

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["⭕ ZERO", "🛡️ FIGHT", "📈 JOURNEY", "⚙️ CALIB"])

# === TAB 1: DASHBOARD ===
with tab1:
    # LEVEL HEADER
    st.caption(f"CURRENT RANK: {level_name.upper()}")
    st.progress(level_progress)
    
    st.title("Zero.")
    st.markdown(f"_{get_quote()}_")
    
    # MAIN STATS (Grid Layout)
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Days Free", f"{days}")
        c2.metric("Saved", f"${money:,.0f}")
    
    with st.container(border=True):
        c3, c4 = st.columns([3,1])
        c3.metric("Avoided", f"{int(avoided)}")
        c4.markdown("## 🚬")

    # HEALTH TIMELINE
    st.divider()
    st.subheader("Health Recovery")
    
    # Visual Timeline Logic
    stages = [
        (24, "CO Cleared", "🩸"),
        (72, "Nicotine Free", "🧠"),
        (336, "Lung Repair", "🫁"),
        (2160, "Cilia Regrowth", "🌿")
    ]
    
    for h, label, icon in stages:
        if hours < h:
            # Current Stage
            pct = max(0.0, min(1.0, hours / h))
            st.write(f"**Current Mission:** {label}")
            st.progress(pct)
            st.caption(f"{int(hours)} / {h} Hours")
            break
    else:
        st.success("🏆 You have cleared the hardest biological hurdles!")

# === TAB 2: THE FIGHT (User Friendly Upgrade) ===
with tab2:
    st.header("Manage Urges")
    
    # PANIC BUTTON (Big & Red)
    with st.container(border=True):
        st.markdown("### 🚨 SOS")
        if st.button("I AM STRUGGLING", type="primary"):
            with st.status("Initiating Calming Sequence...", expanded=True):
                st.write("1. Drop your shoulders.")
                time.sleep(1)
                st.write("2. Unclench your jaw.")
                time.sleep(1)
                st.write("3. Take a deep breath...")
                bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    bar.progress(i+1)
            st.balloons()
            st.success("The wave has passed. Good job.")

    st.write("") # Gap
    
    # QUICK LOG (Using Pills for Speed)
    with st.container(border=True):
        st.markdown("### ⚡ Quick Log")
        
        with st.form("fast_log"):
            # Pills are faster than dropdowns
            st.caption("How strong is it?")
            intensity = st.slider("Intensity", 1, 10, 5, label_visibility="collapsed")
            
            st.caption("What triggered it?")
            # NEW FEATURE: Pills
            trigger = st.pills("", ["Stress", "Boredom", "Meal", "Coffee", "Alcohol", "Social"], selection_mode="single")
            
            st.caption("Where are you?")
            location = st.pills("", ["Home", "Work", "Car", "Outside"], selection_mode="single")
            
            # Default values if user ignores pills
            final_trig = trigger if trigger else "Other"
            final_loc = location if location else "Other"
            
            if st.form_submit_button("LOG & CRUSH IT 👊"):
                write_log(intensity, final_trig, "Fast Log", "TRUE", final_loc)
                st.toast("Logged! Streak maintained.", icon="✅")
                time.sleep(1)
                st.rerun()

# === TAB 3: JOURNEY ===
with tab3:
    st.header("Your Data")
    logs = get_data("Logs")
    
    if not logs.empty and "Trigger" in logs.columns:
        with st.container(border=True):
            st.caption("ENEMY IDENTIFICATION (Top Triggers)")
            counts = logs["Trigger"].value_counts().reset_index()
            counts.columns = ["Trigger", "Count"]
            
            fig = px.bar(counts, x="Count", y="Trigger", orientation='h', text_auto=True)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            fig.update_traces(marker_color='#00FF94')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Data visualization activates after your first log.")

# === TAB 4: CALIBRATION ===
with tab4:
    st.header("Settings")
    
    with st.container(border=True):
        with st.form("settings"):
            st.caption("My Freedom Date")
            d_date = st.text_input("YYYY-MM-DD", str(q_date_obj.date()))
            
            c1, c2 = st.columns(2)
            d_cost = c1.number_input("$/Pack", value=s_cost)
            d_cigs = c2.number_input("Cigs/Day", value=s_daily)
            
            if st.form_submit_button("Update"):
                update_settings(d_date, d_cost, d_cigs)
                st.rerun()
