import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- 1. CONFIG & "MIDNIGHT AURORA" THEME ---
st.set_page_config(page_title="Zero", page_icon="⭕", layout="centered")

st.markdown("""
    <style>
    /* 1. TRUE OLED BLACK BACKGROUND */
    .stApp { 
        background-color: #000000; 
        color: #F0F2F6;
    }
    
    /* 2. HIDE UI CLUTTER */
    header {visibility: hidden;}
    .stApp > footer {display: none;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* 3. MOBILE PADDING */
    div.block-container { padding-top: 1rem; padding-bottom: 6rem; }
    
    /* 4. PREMIUM CARDS (Glassmorphism effect) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #0E1117;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* 5. BUTTONS: GRADIENTS */
    .stButton button {
        width: 100%;
        height: 3.5rem;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        color: white;
        background: linear-gradient(90deg, #2b5876 0%, #4e4376 100%); /* Deep Ocean Gradient */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.1s ease-in-out;
    }
    .stButton button:active { transform: scale(0.97); }
    
    /* Special styling for specific buttons via key/label targeting implies logic in python, 
       but here we set a global premium feel */

    /* 6. METRICS: AURORA GRADIENT TEXT */
    [data-testid="stMetricValue"] { 
        font-size: 2.8rem !important; 
        font-weight: 800;
        background: -webkit-linear-gradient(0deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stMetricLabel"] { 
        color: #94a3b8; 
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* 7. PILLS / TABS */
    [data-testid="stStSelectbox"] { border-radius: 12px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0E1117;
        border-radius: 10px;
        color: #64748b;
        font-size: 14px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1e293b;
        color: #38bdf8; /* Sky blue active tab */
    }
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
    # Using Emojis and Colors to denote rank
    if days < 1: return "🌱 Sprout", 0.0
    if days < 3: return "💧 Drop", 0.1
    if days < 7: return "🌊 Stream", 0.25
    if days < 14: return "⚔️ River", 0.50
    if days < 30: return "🏔️ Mountain", 0.75
    return "💎 Diamond", 1.0

def get_quote():
    quotes = [
        "Discipline is freedom.",
        "The only way out is through.",
        "Don't trade what you want most for what you want now.",
        "Clear lungs, clear mind."
    ]
    return random.choice(quotes)

# --- 4. APP UI ---

# Load Settings
df_set = get_data("Settings")
my_settings = dict(zip(df_set['Key'], df_set['Value'])) if not df_set.empty else {}
days, money, avoided, hours, q_date_obj, s_cost, s_daily = get_progress(my_settings)
level_name, level_progress = get_level(days)

# TABS
# We use spaces to make tabs wider and easier to tap
tab1, tab2, tab3, tab4 = st.tabs(["  🏠 ZERO  ", "  🛡️ FIGHT  ", "  📊 DATA  ", "  ⚙️ SET  "])

# === TAB 1: DASHBOARD (The Calm) ===
with tab1:
    # HEADER
    c_rank, c_prog = st.columns([2, 3])
    with c_rank:
        st.caption("CURRENT RANK")
        st.markdown(f"**{level_name}**")
    with c_prog:
        st.caption("NEXT LEVEL")
        st.progress(level_progress)
    
    st.title("Zero.")
    st.markdown(f"*{get_quote()}*")
    st.write("") # Spacer

    # METRIC CARDS
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Days Free", f"{days}")
        c2.metric("Saved", f"${money:,.0f}")
    
    with st.container(border=True):
        c3, c4 = st.columns([3,1])
        c3.metric("Cigs Avoided", f"{int(avoided)}")
        c4.markdown("# 💀")

    st.divider()
    st.subheader("🧬 Biological Timeline")
    
    # Timeline Logic with Icons
    stages = [
        (24, "Carbon Monoxide cleared", "🩸"),
        (72, "Nicotine removed", "🧠"),
        (336, "Circulation improving", "❤️"),
        (2160, "Lung capacity +10%", "🫁")
    ]
    
    found_stage = False
    for h, label, icon in stages:
        if hours < h:
            pct = max(0.0, min(1.0, hours / h))
            st.info(f"**Current Phase:** {label}")
            st.progress(pct)
            st.caption(f"{int(hours)} / {h} Hours completed")
            found_stage = True
            break
    if not found_stage:
        st.success("💎 You are in the advanced healing phase!")

# === TAB 2: FIGHT (The Fire) ===
with tab2:
    st.header("Emergency Room")
    
    # PANIC BUTTON - Uses a different CSS class implicitly via 'type=primary'
    # We use a container to frame it in Red
    st.error("Craving Intensity: High? Tap below.")
    
    if st.button("🆘 ACTIVATE RESCUE MODE", type="primary"):
        with st.status("⚡ Hack your biology...", expanded=True):
            st.markdown("**Step 1:** 🧊 Drink cold water (Shock the system)")
            time.sleep(1)
            st.markdown("**Step 2:** 🌬️ Exhale fully (Empty the lungs)")
            time.sleep(1)
            st.markdown("**Step 3:** ⏳ Wait out the timer...")
            
            bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                bar.progress(i+1)
        st.balloons()
        st.success("Dopamine hit provided. You are safe.")

    st.write("---")
    
    # LOGGING (Clean & Fast)
    with st.container(border=True):
        st.subheader("📝 Fast Log")
        with st.form("fast_log"):
            st.caption("Intensity Level")
            intensity = st.slider("Select", 1, 10, 5, label_visibility="collapsed")
            
            st.caption("Trigger")
            # Using Pills for colorful, easy selection
            trigger = st.pills("Source", ["Stress", "Boredom", "Meal", "Coffee", "Alcohol", "Social"], selection_mode="single")
            
            st.caption("Location")
            location = st.pills("Place", ["Home", "Work", "Car", "Outside"], selection_mode="single")
            
            # Safe defaults
            trig_val = trigger if trigger else "Unknown"
            loc_val = location if location else "Unknown"
            
            submit = st.form_submit_button("LOG & WIN")
            
            if submit:
                write_log(intensity, trig_val, "Logged", "TRUE", loc_val)
                st.toast("Victory Logged.", icon="🛡️")
                time.sleep(0.5)
                st.rerun()

# === TAB 3: DATA (The Logic) ===
with tab3:
    st.header("Patterns")
    logs = get_data("Logs")
    
    if not logs.empty and "Trigger" in logs.columns:
        with st.container(border=True):
            st.caption("YOUR TOP TRIGGERS")
            counts = logs["Trigger"].value_counts().reset_index()
            counts.columns = ["Trigger", "Count"]
            
            # Aesthetic Chart
            fig = px.bar(counts, x="Count", y="Trigger", orientation='h', text_auto=True)
            
            # Custom Color Palette for the Chart (Teal/Blue)
            fig.update_traces(marker_color='#38bdf8', marker_line_color='#0ea5e9', marker_line_width=1.5, opacity=0.8)
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start logging to see your data come to life.")

# === TAB 4: SETTINGS ===
with tab4:
    st.header("Configuration")
    
    with st.container(border=True):
        with st.form("settings"):
            st.caption("Quit Date (YYYY-MM-DD)")
            d_date = st.text_input("Date", str(q_date_obj.date()), label_visibility="collapsed")
            
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Cost/Pack")
                d_cost = st.number_input("Cost", value=s_cost, label_visibility="collapsed")
            with c2:
                st.caption("Cigs/Day")
                d_cigs = st.number_input("Count", value=s_daily, label_visibility="collapsed")
            
            if st.form_submit_button("Update Profile"):
                update_settings(d_date, d_cost, d_cigs)
                st.rerun()
