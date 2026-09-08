import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json

# Set web dashboard configurations
st.set_page_config(page_title="Catering Management Suite", page_icon="🍲", layout="wide")

# =====================================================================
# 🛠️ SYSTEM CONNECTORS: PASTE YOUR GOOGLE SHEET LINKS HERE
# =====================================================================
SPREADSHEET_ID = "1cdB_oR7HrbL-mTJ1wb58eaU_kFcUuCmeXtbI0gJYKXw"
APPS_SCRIPT_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxK---0qS2M07Hz_8f9g-XXS9QZfrqaxy2fT43mvZODOwX3kf0ElkbKgIR-_BgkShbl/exec"
# =====================================================================

DAYS_KEYS = ["Sat 05", "Sun 06", "Mon 07", "Tue 08", "Wed 09", "Thu 10", "Fri 11"]
CSV_URL = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
AVAILABLE_RATES = [100, 110, 120, 130, 140, 150]

# Function to pull live data from Google Sheets
def load_gsheet_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = ["Customer", "Phone", "BasePrice", "Day", "RegQty", "SpecQty", "SpecPrice", "ExtraChicken", "OrderNotes"]
        return df
    except Exception:
        # Fallback template matrix matching system structures if spreadsheet initialization yields empty sets
        default_rows = []
        liam_data = {
            "Sat 05": (2, 0, 150, 1, "Delivered early"), "Sun 06": (2, 0, 150, 0, ""), 
            "Mon 07": (0, 1, 150, 0, "Requested mild spice"), "Tue 08": (2, 0, 150, 1, ""), 
            "Wed 09": (2, 0, 150, 0, ""), "Thu 10": (2, 0, 150, 1, ""), "Fri 11": (0, 0, 150, 0, "")
        }
        for day in DAYS_KEYS:
            reg, spec, spec_p, ext, note = liam_data[day]
            default_rows.append(["Liam Anderson", "+15550199", 120, day, reg, spec, spec_p, ext, note])
        for day in DAYS_KEYS:
            default_rows.append(["Aria Roberts", "+8801711223344", 150, day, 0, 0, 150, 0, ""])
        
        return pd.DataFrame(default_rows, columns=["Customer", "Phone", "BasePrice", "Day", "RegQty", "SpecQty", "SpecPrice", "ExtraChicken", "OrderNotes"])

# Function to save data updates back to Google Sheets via Apps Script Web App
def save_gsheet_data(df):
    st.session_state.current_df = df
    if APPS_SCRIPT_WEBAPP_URL != "https://script.google.com/macros/s/AKfycbxK---0qS2M07Hz_8f9g-XXS9QZfrqaxy2fT43mvZODOwX3kf0ElkbKgIR-_BgkShbl/exec":
        try:
            # Convert the dataframe table into a list of rows to send over the web safely
            payload = [df.columns.tolist()] + df.values.tolist()
            requests.post(APPS_SCRIPT_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except Exception:
            pass

# Live dynamic theme configuration setup
if 'app_theme' not in st.session_state:
    st.session_state.app_theme = "Deep Charcoal (Default)"

theme = st.session_state.app_theme
bg_color = "#0F1319" if theme == "Deep Charcoal (Default)" else "#18181B" if theme == "Midnight Onyx" else "#0F172A"
card_color = "#161B26" if theme == "Deep Charcoal (Default)" else "#242427" if theme == "Midnight Onyx" else "#1E293B"
border_color = "#232D3F" if theme == "Deep Charcoal (Default)" else "#3F3F46" if theme == "Midnight Onyx" else "#334155"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: #E2E8F0; }}
    .custom-section-box {{ background-color: {card_color}; border: 1px solid {border_color}; padding: 20px; border-radius: 10px; margin-bottom: 16px; }}
    .summary-card {{ background-color: {card_color}; border-radius: 16px; padding: 24px; border: 1px solid {border_color}; }}
    .day-node {{ flex: 1; background-color: rgba(0,0,0,0.2); border-radius: 10px; padding: 12px 6px; text-align: center; border: 1px solid {border_color}; }}
    .day-node.active {{ border: 2px solid #3B82F6; background-color: rgba(59, 130, 246, 0.1); }}
    .day-node .day-name {{ font-size: 12px; color: #718096; font-weight: 700; text-transform: uppercase; }}
    .day-node .day-date {{ font-size: 18px; font-weight: 800; color: #FFFFFF; margin: 2px 0; }}
    .badge-reg {{ background-color: rgba(59, 130, 246, 0.15); color: #3B82F6; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
    .badge-spec {{ background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
    .note-indicator {{ color: #A855F7; font-size: 12px; font-weight: bold; margin-top: 4px; }}
    .whatsapp-btn {{ background-color: #10B981 !important; color: white !important; text-align: center; padding: 14px; border-radius: 30px; font-weight: bold; display: block; text-decoration: none; margin-top: 15px; font-size: 16px; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.selected_customer = None

if 'current_df' not in st.session_state:
    st.session_state.current_df = load_gsheet_data()

df_db = st.session_state.current_df
customers_list = sorted(df_db["Customer"].unique().tolist())
# Security Access Gateways UI Block
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🔐 Catering App Gateway Authentication</h2>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
        st.subheader("🛠️ Management / Developer Portal")
        owner_pass = st.text_input("Enter Management Pin Password", type="password")
        if st.button("Access Admin Panel", use_container_width=True):
            if owner_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "owner"
                st.session_state.selected_customer_idx = 0
                st.rerun()
            else:
                st.error("Incorrect portal pin access password entered.")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
        st.subheader("👤 Client Tracking View Portal")
        client_user = st.selectbox("Select Your Profile Name", options=customers_list)
        if st.button("Open My Tracking Dashboard", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "customer"
            st.session_state.selected_customer = client_user
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if st.sidebar.button("🔒 Sign Out / Exit Profile"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

is_owner = (st.session_state.user_role == "owner")

if is_owner:
    st.sidebar.markdown("### ⚙️ Developer Settings Control Panel")
    selected_theme = st.sidebar.selectbox("Live Web Dashboard Theme Color", ["Deep Charcoal (Default)", "Midnight Onyx", "Slate Matrix"])
    if selected_theme != st.session_state.app_theme:
        st.session_state.app_theme = selected_theme
        st.rerun()

if is_owner:
    if 'selected_customer_idx' not in st.session_state or st.session_state.selected_customer_idx >= len(customers_list):
        st.session_state.selected_customer_idx = 0
    customer = customers_list[st.session_state.selected_customer_idx]
else:
    customer = st.session_state.selected_customer

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = "Sat 05"
current_day = st.session_state.selected_day

cust_df = df_db[df_db["Customer"] == customer]
phone_num = str(cust_df["Phone"].iloc[0]) if not cust_df.empty else ""
price_per_reg = int(cust_df["BasePrice"].iloc[0]) if not cust_df.empty else 120

# 📊 REVENUE GRAPH ENGINE
if is_owner:
    st.markdown("<p style='color: #3B82F6; font-weight: bold; margin-bottom: 0px;'>OWNER / SYSTEM DEVELOPER SUITE</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0px; color: white;'>Live Analytics & Revenue Tracker</h2>", unsafe_allow_html=True)
    revenue_records = []
    for c_name in customers_list:
        c_data = df_db[df_db["Customer"] == c_name]
        c_base = int(c_data["BasePrice"].iloc[0]) if not c_data.empty else 120
        c_total = (int(c_data["RegQty"].sum()) * c_base) + int((c_data["SpecQty"] * c_data["SpecPrice"]).sum()) + (int(c_data["ExtraChicken"].sum()) * 40)
        revenue_records.append({"Client Profile Name": c_name, "Weekly Revenue (Tk)": c_total})
    st.bar_chart(data=pd.DataFrame(revenue_records), x="Client Profile Name", y="Weekly Revenue (Tk)", color="#3B82F6", use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color: #10B981; font-weight: bold; margin-bottom: 0px;'>🔒 CLIENT MONITORING DASHBOARD (LOCKED VIEW-ONLY)</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='margin-top: 0px; color: white;'>Weekly Tracking History for {customer}</h2>", unsafe_allow_html=True)

total_reg_meals = int(cust_df["RegQty"].sum()) if not cust_df.empty else 0
total_spec_meals = int(cust_df["SpecQty"].sum()) if not cust_df.empty else 0
total_extra_chicken = int(cust_df["ExtraChicken"].sum()) if not cust_df.empty else 0
total_bill = (total_reg_meals * price_per_reg) + int((cust_df["SpecQty"] * cust_df["SpecPrice"]).sum()) + (total_extra_chicken * 40)

col_main, col_summary = st.columns()
with col_main:
    st.markdown("<div style='display: flex; gap: 8px;'>", unsafe_allow_html=True)
    day_cols = st.columns(7)
    for idx, day_id in enumerate(DAYS_KEYS):
        with day_cols[idx]:
            day_name, day_num = day_id.split()
            day_row = cust_df[cust_df["Day"] == day_id] if not cust_df.empty else pd.DataFrame()
            reg_q = int(day_row["RegQty"].iloc[0]) if not day_row.empty else 0
            spec_q = int(day_row["SpecQty"].iloc[0]) if not day_row.empty else 0
            has_note = str(day_row["OrderNotes"].iloc[0]).strip() != "" if not day_row.empty and "OrderNotes" in day_row.columns else False
            
            is_active = (current_day == day_id)
            active_class = "active" if is_active else ""
            badge_str = "<div style='height:21px;'></div>"
            if spec_q > 0: badge_str = f"<div class='badge-spec'>Spc {spec_q}</div>"
            elif reg_q > 0: badge_str = f"<div class='badge-reg'>Reg {reg_q}</div>"
            note_str = "<div class='note-indicator'>📝 Note</div>" if has_note else ""
            
            st.markdown(f'<div class="day-node {active_class}"><div class="day-name">{day_name}</div><div class="day-date">{day_num}</div><div style="margin-top:6px;">{badge_str}</div>{note_str}</div>', unsafe_allow_html=True)
            if st.button("Select", key=f"btn_{day_id}", use_container_width=True):
                st.session_state.selected_day = day_id
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if is_owner:
        chosen_customer = st.selectbox("Switch Customer View", options=customers_list, index=customers_list.index(customer))
        if chosen_customer != customer:
            st.session_state.selected_customer_idx = customers_list.index(chosen_customer)
            st.rerun()

with col_summary:
    st.markdown(f"""
        <div class="summary-card">
            <p style="color: #64748B; font-weight: bold; font-size: 13px; text-transform: uppercase; margin-bottom: 12px;">Cycle Aggregates</p>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span style="color:#94A3B8;">Regular meals:</span><span style="color:white; font-weight:bold;">{total_reg_meals} pcs</span></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span style="color:#94A3B8;">Special meals:</span><span style="color:white; font-weight:bold;">{total_spec_meals} pcs</span></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px;"><span style="color:#94A3B8;">Extra Chicken:</span><span style="color:white; font-weight:bold;">{total_extra_chicken} pcs</span></div>
            <div style="border-top:1px solid {border_color}; padding-top:12px; display:flex; justify-content:space-between; margin-bottom:15px;"><span style="color: white; font-weight: bold;">Total Bill Statement:</span><span style="color: #10B981; font-weight: 800; font-size: 24px;">{total_bill} Tk</span></div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"<h3>Selected Schedule Details • <span style='color:#3B82F6;'>{current_day.upper()}</span></h3>", unsafe_allow_html=True)

day_mask = (df_db["Customer"] == customer) & (df_db["Day"] == current_day)
active_row = df_db[day_mask]
curr_note = str(active_row["OrderNotes"].iloc[0]) if not active_row.empty and "OrderNotes" in active_row.columns else ""

if is_owner:
    st.markdown("<div class='custom-section-box' style='border-left: 4px solid #A855F7;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A855F7; font-weight:bold; font-size:12px; text-transform:uppercase; margin-bottom:4px;'>🛠️ Special Order Note Tool</p>", unsafe_allow_html=True)
    new_note = st.text_input("Tap to write custom update notes for this client's day entry", value=curr_note, placeholder="e.g. Extra spicy, holiday cancel...")
    if new_note != curr_note and not active_row.empty:
        df_db.loc[day_mask, "OrderNotes"] = new_note
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
elif curr_note.strip() != "":
    st.markdown(f"<div class='custom-section-box' style='border-left: 4px solid #A855F7;'><p style='color:#A855F7; font-weight:bold; font-size:12px;'>📝 OWNER ORDER NOTE</p><p style='color:white; font-style:italic; margin-bottom:0;'>\"{curr_note}\"</p></div>", unsafe_allow_html=True)

if is_owner:
    if not active_row.empty:
        curr_reg = int(active_row["RegQty"].iloc[0])
        curr_spec = int(active_row["SpecQty"].iloc[0])
        curr_spec_p = int(active_row["SpecPrice"].iloc[0])
        curr_extra = int(active_row["ExtraChicken"].iloc[0])
    else:
        curr_reg, curr_spec, curr_spec_p, curr_extra = 0, 0, 150, 0
        
    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    new_reg = st.number_input("Regular Quantity count input", min_value=0, value=curr_reg, key=f"r_edit_{current_day}")
    if new_reg != curr_reg:
        df_db.loc[day_mask, "RegQty"] = new_reg
        if new_reg > 0: df_db.loc[day_mask, "SpecQty"] = 0
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        new_spec = st.number_input("Special Quantity count input", min_value=0, value=curr_spec, key=f"s_edit_{current_day}")
        if new_spec != curr_spec:
            df_db.loc[day_mask, "SpecQty"] = new_spec
            if new_spec > 0: df_db.loc[day_mask, "RegQty"] = 0
            save_gsheet_data(df_db)
            st.rerun()
    with c2:
        new_spec_p = st.number_input("Special meal specific unit pricing", min_value=0, value=curr_spec_p, key=f"sp_edit_{current_day}")
        if new_spec_p != curr_spec_p:
            df_db.loc[day_mask, "SpecPrice"] = new_spec_p
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    new_extra = st.number_input("Extra chicken pieces item inputs", min_value=0, value=curr_extra, key=f"e_edit_{current_day}")
    if new_extra != curr_extra:
        df_db.loc[day_mask, "ExtraChicken"] = new_extra
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    invoice_msg = f"Catering Invoice - {customer}\n• Regular Meals: {total_reg_meals} pcs\n• Special Meals: {total_spec_meals} pcs\n• Extra Chicken: {total_extra_chicken} pcs\nTotal Due: {total_bill} Tk"
    st.text_area("Live Message Payload Preview", value=invoice_msg, height=100, disabled=True)
    whatsapp_link = f"wa.me{phone_num.replace('+', '').replace(' ', '')}?text={urllib.parse.quote(invoice_msg)}"
    st.markdown(f'➤ Open WhatsApp API Link', unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
else:
    if not active_row.empty:
        st.markdown(f"📊 Delivered Order Record for Today• Regular Meals Delivered: {active_row['RegQty'].iloc[0]} pcs• Special Meals Delivered: {active_row['SpecQty'].iloc[0]} pcs (Price: {active_row['SpecPrice'].iloc[0]} Tk)• Extra Chicken Pieces Added: {active_row['ExtraChicken'].iloc[0]} pieces", unsafe_allow_html=True)
