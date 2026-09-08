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
AVAILABLE_RATES = [100, 110, 120, 130, 140, 150, 160, 180, 200]

# Function to pull live data from Google Sheets
def load_gsheet_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = ["Customer", "Phone", "BasePrice", "Day", "RegQty", "SpecQty", "SpecPrice", "ExtraChicken", "OrderNotes"]
        return df
    except Exception:
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

# Function to save data updates back to Google Sheets
def save_gsheet_data(df):
    st.session_state.current_df = df
    if APPS_SCRIPT_WEBAPP_URL != "PASTE_YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE":
        try:
            payload = [df.columns.tolist()] + df.values.tolist()
            requests.post(APPS_SCRIPT_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except Exception:
            pass

# Custom Premium Styling matching the exact UI theme
st.markdown("""
    <style>
    .stApp { background-color: #0F1319; color: #E2E8F0; }
    
    /* Day Node Card Layouts */
    .day-card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
    }
    .day-node-card {
        background-color: #161B26;
        border: 1px solid #232D3F;
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }
    .day-node-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }
    .day-node-card.active {
        border: 2px solid #3B82F6;
        background-color: rgba(59, 130, 246, 0.08);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
    }
    
    .day-name { font-size: 11px; color: #718096; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .day-date { font-size: 20px; font-weight: 800; color: #FFFFFF; margin: 4px 0; }
    
    /* Integrated Label Badges */
    .badge-item {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-top: 4px;
        display: inline-block;
        width: 85%;
        text-align: center;
    }
    .badge-reg { background-color: rgba(59, 130, 246, 0.15); color: #3B82F6; }
    .badge-spec { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; }
    .badge-note { background-color: rgba(168, 85, 247, 0.15); color: #A855F7; }
    .badge-empty { height: 18px; }

    .custom-section-box { background-color: #161B26; border: 1px solid #232D3F; padding: 20px; border-radius: 12px; margin-bottom: 16px; }
    .summary-card { background-color: #171E2E; border-radius: 16px; padding: 24px; border: 1px solid #243146; }
    .whatsapp-btn { background-color: #10B981 !important; color: white !important; text-align: center; padding: 14px; border-radius: 30px; font-weight: bold; display: block; text-decoration: none; margin-top: 15px; font-size: 16px; width: 100%; text-transform: uppercase; }
    
    /* Hide default streamlit button styling for card selections */
    div[data-testid="stFormSubmitButton"] > button, div.stButton > button {
        opacity: 0;
        position: absolute;
        z-index: 2;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
    }
    .card-wrapper { position: relative; }
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
    st.markdown("<h2 style='text-align:center; margin-top:40px;'>🔐 Catering App Gateway Authentication</h2>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
        st.subheader("🛠️ Management Portal")
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
        st.subheader("👤 Client Portal")
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

# Title Headers
st.markdown("<p style='color: #3B82F6; font-weight: bold; margin-bottom: 0px;'>SEPTEMBER 2026 <span style='color:#64748B; font-weight:normal;'>• Cycle Mapping frame: Sat → Fri</span></p>", unsafe_allow_html=True)
st.markdown("<h2 style='margin-top: 0px; color: white;'>Customer Cycle Mapping Invoice Generator</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94A3B8; font-size: 14px; margin-bottom: 25px;'>Current profile: <span style='color:#FFF; font-weight:600;'>{customer}</span> (• Base Price: {price_per_reg} Tk)</p>", unsafe_allow_html=True)

total_reg_meals = int(cust_df["RegQty"].sum()) if not cust_df.empty else 0
total_spec_meals = int(cust_df["SpecQty"].sum()) if not cust_df.empty else 0
total_extra_chicken = int(cust_df["ExtraChicken"].sum()) if not cust_df.empty else 0
total_bill = (total_reg_meals * price_per_reg) + int((cust_df["SpecQty"] * cust_df["SpecPrice"]).sum()) + (total_extra_chicken * 40)

# 📅 NEW BORDERLESS DYNAMIC SELECTION CARD GRID
col_main, col_summary = st.columns([3, 1])

with col_main:
    day_cols = st.columns(7)
    for idx, day_id in enumerate(DAYS_KEYS):
        with day_cols[idx]:
            day_name, day_num = day_id.split()
            day_row = cust_df[cust_df["Day"] == day_id] if not cust_df.empty else pd.DataFrame()
            
            reg_q = int(day_row["RegQty"].iloc[0]) if not day_row.empty else 0
            spec_q = int(day_row["SpecQty"].iloc[0]) if not day_row.empty else 0
            has_note = str(day_row["OrderNotes"].iloc[0]).strip() != "" if not day_row.empty and "OrderNotes" in day_row.columns and not pd.isna(day_row["OrderNotes"].iloc[0]) else False
            
            is_active = (current_day == day_id)
            active_class = "active" if is_active else ""
            
            # Badge generation matching design requirement colors
            badge_html = ""
            if spec_q > 0:
                badge_html += f"<div class='badge-item badge-spec'>Spc {spec_q}</div>"
            elif reg_q > 0:
                badge_html += f"<div class='badge-item badge-reg'>Reg {reg_q}</div>"
            else:
                badge_html += "<div class='badge-empty'></div>"
                
            if has_note:
                badge_html += "<div class='badge-item badge-note'>📝 Note</div>"
                
            # Render HTML Node card container layout frame maps
            st.markdown(f"""
                <div class="card-wrapper">
                    <div class="day-node-card {active_class}">
                        <div class="day-name">{day_name}</div>
                        <div class="day-date">{day_num}</div>
                        <div style="width: 100%; display: flex; flex-direction: column; align-items: center; gap: 2px;">
                            {badge_html}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Invisible button layer overlaying the custom HTML card to intercept direct tap events
            if st.button("", key=f"btn_click_{day_id}"):
                st.session_state.selected_day = day_id
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    if is_owner:
        c_p, c_r = st.columns(2)
        with c_p:
            chosen_customer = st.selectbox("Customer Profile", options=customers_list, index=customers_list.index(customer))
            if chosen_customer != customer:
                st.session_state.selected_customer_idx = customers_list.index(chosen_customer)
                st.rerun()
        with c_r:
            rate_idx = AVAILABLE_RATES.index(price_per_reg) if price_per_reg in AVAILABLE_RATES else 2
            new_rate = st.selectbox("Per-Meal Price (Tk)", options=AVAILABLE_RATES, index=rate_idx, format_func=lambda x: f"{x} Tk")
            if new_rate != price_per_reg:
                df_db.loc[df_db["Customer"] == customer, "BasePrice"] = new_rate
                save_gsheet_data(df_db)
                st.rerun()

with col_summary:
    st.markdown(f"""
        <div class="summary-card">
            <p style="color: #64748B; font-weight: bold; font-size: 13px; text-transform: uppercase; margin-bottom: 12px;">Cycle Summary</p>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span style="color:#94A3B8;">Regular meals total:</span><span style="color:white; font-weight:bold;">{total_reg_meals} pcs</span></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span style="color:#94A3B8;">Special meals total:</span><span style="color:white; font-weight:bold;">{total_spec_meals} pcs</span></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px;"><span style="color:#94A3B8;">Extra Chicken protein:</span><span style="color:white; font-weight:bold;">{total_extra_chicken} pcs</span></div>
            <div style="border-top:1px solid #243146; padding-top:12px; display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#94A3B8;">Base rate applied:</span><span style="color:#3B82F6; font-weight:bold;">{price_per_reg} Tk</span></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><span style="color: white; font-weight: bold; font-size: 16px;">Total Bill:</span><span style="color: #10B981; font-weight: 800; font-size: 24px;">{total_bill} Tk</span></div>
            <button style="width:100%; background-color:#2563EB; border:none; color:white; padding:10px; border-radius:8px; font-weight:bold;">Export Dashboard</button>
        </div>
    """, unsafe_allow_html=True)

# 🛠️ DYNAMIC DAY CONFIGURATION DATAFRAME PARAMS
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"<h3>Daily Parameters Grid • <span style='color:#3B82F6;'>{current_day.upper()} Config</span></h3>", unsafe_allow_html=True)

day_mask = (df_db["Customer"] == customer) & (df_db["Day"] == current_day)
active_row = df_db[day_mask]
curr_note = str(active_row["OrderNotes"].iloc[0]) if not active_row.empty and "OrderNotes" in active_row.columns and not pd.isna(active_row["OrderNotes"].iloc[0]) else ""

if is_owner:
    st.markdown("<div class='custom-section-box' style='border-left: 4px solid #A855F7;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A855F7; font-weight:bold; font-size:12px; text-transform:uppercase; margin-bottom:4px;'>📝 Special Order Note Tool</p>", unsafe_allow_html=True)
    new_note = st.text_input("Tap to write custom update notes for this client's day entry", value=curr_note, placeholder="e.g. Extra spicy, holiday cancel...")
    if new_note != curr_note and not active_row.empty:
        df_db.loc[day_mask, "OrderNotes"] = new_note
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
elif curr_note.strip() != "":
    st.markdown(f"<div class='custom-section-box' style='border-left: 4px solid #A855F7;'><p style='color:#A855F7; font-weight:bold; font-size:12px;'>📝 OWNER ORDER NOTE</p><p style='color:white; font-style:italic; margin-bottom:0;'>\"{curr_note}\"</p></div>", unsafe_allow_html=True)

if is_owner:
    # 1. Safely extract values only if data rows exist in memory
    if not active_row.empty:
        curr_reg = int(active_row["RegQty"].iloc[0])
        curr_spec = int(active_row["SpecQty"].iloc[0])
        curr_spec_p = int(active_row["SpecPrice"].iloc[0])
        curr_extra = int(active_row["ExtraChicken"].iloc[0])
    else:
        curr_reg, curr_spec, curr_spec_p, curr_extra = 0, 0, 150, 0

    # 2. Regular Meals Input Box Container Layout
    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#3B82F6; font-weight:bold; font-size:12px; text-transform:uppercase;'>Regular Meals Config</p>", unsafe_allow_html=True)
    new_reg = st.number_input("Quantity Regular", min_value=0, value=curr_reg, key=f"r_edit_{current_day}")
    if new_reg != curr_reg and not active_row.empty:
        df_db.loc[day_mask, "RegQty"] = new_reg
        if new_reg > 0: 
            df_db.loc[day_mask, "SpecQty"] = 0
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Special Section Inputs Box Container Layout
    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#F59E0B; font-weight:bold; font-size:12px; text-transform:uppercase;'>Special Section Config</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        new_spec = st.number_input("Quantity Special", min_value=0, value=curr_spec, key=f"s_edit_{current_day}")
        if new_spec != curr_spec and not active_row.empty:
            df_db.loc[day_mask, "SpecQty"] = new_spec
            if new_spec > 0: 
                df_db.loc[day_mask, "RegQty"] = 0
            save_gsheet_data(df_db)
            st.rerun()
    with c2:
        new_spec_p = st.number_input("Custom Special Price (Tk)", min_value=0, value=curr_spec_p, key=f"sp_edit_{current_day}")
        if new_spec_p != curr_spec_p and not active_row.empty:
            df_db.loc[day_mask, "SpecPrice"] = new_spec_p
            save_gsheet_data(df_db)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
        # 4. Extra Chicken Box Container Layout
    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#10B981; font-weight:bold; font-size:12px; text-transform:uppercase;'>Extra Chicken Protein Add-Ons</p>", unsafe_allow_html=True)
    new_extra = st.number_input("Quantity Extra", min_value=0, value=curr_extra, key=f"e_edit_{current_day}")
    if new_extra != curr_extra and not active_row.empty:
        df_db.loc[day_mask, "ExtraChicken"] = new_extra
        save_gsheet_data(df_db)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Live Message Display and Official WhatsApp API Send Button
    st.markdown("<div class='custom-section-box'>", unsafe_allow_html=True)
    invoice_msg = f"*Catering Invoice - {customer}*\n• Regular Meals: {total_reg_meals} pcs\n• Special Meals: {total_spec_meals} pcs\n• Extra Chicken: {total_extra_chicken} pcs\n*Total Due: {total_bill} Tk*"
    st.text_area("Live Message Payload Preview", value=invoice_msg, height=100, disabled=True)
    
    clean_phone = phone_num.replace('+', '').replace(' ', '').replace('-', '')
    whatsapp_link = f"https://wa.me{clean_phone}?text={urllib.parse.quote(invoice_msg)}"
    st.markdown(f'<a href="{whatsapp_link}" target="_blank" class="whatsapp-btn">➤ Open WhatsApp API Link</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # 6. View-Only Layout for clients logging into the system
    if not active_row.empty:
        st.markdown(f"""
            <div class='custom-section-box'>
                <p style='color:#3B82F6; font-weight:bold; margin-bottom:4px;'>📊 Delivered Order Record for Today</p>
                • Regular Meals Delivered: <b>{active_row['RegQty'].iloc[0]} pcs</b><br>
                • Special Meals Delivered: <b>{active_row['SpecQty'].iloc[0]} pcs</b> (Price: {active_row['SpecPrice'].iloc[0]} Tk)<br>
                • Extra Chicken Pieces Added: <b>{active_row['ExtraChicken'].iloc[0]} pieces</b>
            </div>
        """, unsafe_allow_html=True)
  
