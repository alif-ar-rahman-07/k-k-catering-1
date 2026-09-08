import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Catering Management Suite",
    page_icon="🍲",
    layout="wide",
)


# ============================================================
# CONFIGURATION
# ============================================================
SPREADSHEET_ID = "1cdB_oR7HrbL-mTJ1wb58eaU_kFcUuCmeXtbI0gJYKXw"

# IMPORTANT:
# Replace this with your actual deployed Google Apps Script Web App URL.
APPS_SCRIPT_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxK---0qS2M07Hz_8f9g-XXS9QZfrqaxy2fT43mvZODOwX3kf0ElkbKgIR-_BgkShbl/exec"

# IMPORTANT:
# Replace this with your actual Google Sheets CSV URL if needed.
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
)

DAYS_KEYS = [
    "Sat 05",
    "Sun 06",
    "Mon 07",
    "Tue 08",
    "Wed 09",
    "Thu 10",
    "Fri 11",
]

AVAILABLE_RATES = [100, 110, 120, 130, 140, 150]

EXTRA_CHICKEN_PRICE = 40
DEFAULT_SPECIAL_PRICE = 150


# ============================================================
# DATA HELPERS
# ============================================================
COLUMNS = [
    "Customer",
    "Phone",
    "BasePrice",
    "Day",
    "RegQty",
    "SpecQty",
    "SpecPrice",
    "ExtraChicken",
    "OrderNotes",
]


def create_default_data():
    """Create fallback demo data if Google Sheets cannot be loaded."""

    default_rows = []

    liam_data = {
        "Sat 05": (2, 0, 150, 1, "Delivered early"),
        "Sun 06": (2, 0, 150, 0, ""),
        "Mon 07": (0, 1, 150, 0, "Requested mild spice"),
        "Tue 08": (2, 0, 150, 1, ""),
        "Wed 09": (2, 0, 150, 0, ""),
        "Thu 10": (2, 0, 150, 1, ""),
        "Fri 11": (0, 0, 150, 0, ""),
    }

    for day in DAYS_KEYS:
        reg, spec, spec_price, extra, note = liam_data[day]

        default_rows.append(
            [
                "Liam Anderson",
                "+15550199",
                120,
                day,
                reg,
                spec,
                spec_price,
                extra,
                note,
            ]
        )

    for day in DAYS_KEYS:
        default_rows.append(
            [
                "Aria Roberts",
                "+8801711223344",
                150,
                day,
                0,
                0,
                150,
                0,
                "",
            ]
        )

    return pd.DataFrame(default_rows, columns=COLUMNS)


def clean_dataframe(df):
    """Normalize dataframe columns and numeric fields."""

    df = df.copy()

    # Make sure all expected columns exist.
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[COLUMNS]

    numeric_columns = [
        "BasePrice",
        "RegQty",
        "SpecQty",
        "SpecPrice",
        "ExtraChicken",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).fillna(0)

    df["BasePrice"] = df["BasePrice"].astype(int)
    df["RegQty"] = df["RegQty"].astype(int)
    df["SpecQty"] = df["SpecQty"].astype(int)
    df["SpecPrice"] = df["SpecPrice"].astype(int)
    df["ExtraChicken"] = df["ExtraChicken"].astype(int)

    df["Customer"] = df["Customer"].fillna("").astype(str)
    df["Phone"] = df["Phone"].fillna("").astype(str)
    df["Day"] = df["Day"].fillna("").astype(str)
    df["OrderNotes"] = df["OrderNotes"].fillna("").astype(str)

    return df


def load_gsheet_data():
    """Load data from Google Sheets."""

    try:
        df = pd.read_csv(CSV_URL)

        if len(df.columns) != len(COLUMNS):
            raise ValueError(
                f"Expected {len(COLUMNS)} columns, got {len(df.columns)}."
            )

        df.columns = COLUMNS
        return clean_dataframe(df)

    except Exception:
        return create_default_data()


def save_gsheet_data(df):
    """Save dataframe locally and send it to Apps Script."""

    df = clean_dataframe(df)

    st.session_state.current_df = df

    try:
        payload = [
            df.columns.tolist()
        ] + df.values.tolist()

        response = requests.post(
            APPS_SCRIPT_WEBAPP_URL,
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json"
            },
            timeout=15,
        )

        # Do not crash the dashboard if Apps Script responds unexpectedly.
        if response.status_code >= 400:
            st.warning(
                f"Google Sheets save returned HTTP {response.status_code}."
            )

    except Exception as exc:
        st.warning(
            f"Local changes were applied, but Google Sheets could not be updated: {exc}"
        )


# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #0F1319;
        color: #E2E8F0;
    }

    /* ========================================================
       DAY CARDS
       ======================================================== */

    .day-node-card {
        background-color: #161B26;
        border: 1px solid #232D3F;
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease-in-out;
    }

    .day-node-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }

    .day-node-card.active {
        border: 2px solid #3B82F6;
        background-color: rgba(59, 130, 246, 0.08);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.20);
    }

    .day-name {
        font-size: 11px;
        color: #718096;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .day-date {
        font-size: 20px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 4px 0;
    }

    /* ========================================================
       BADGES
       ======================================================== */

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

    .badge-reg {
        background-color: rgba(59, 130, 246, 0.15);
        color: #3B82F6;
    }

    .badge-spec {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
    }

    .badge-note {
        background-color: rgba(168, 85, 247, 0.15);
        color: #A855F7;
    }

    .badge-empty {
        height: 18px;
    }

    /* ========================================================
       GENERAL BOXES
       ======================================================== */

    .custom-section-box {
        background-color: #161B26;
        border: 1px solid #232D3F;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 16px;
    }

    .summary-card {
        background-color: #171E2E;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #243146;
    }

    /* ========================================================
       WHATSAPP BUTTON
       ======================================================== */

    .whatsapp-btn {
        background-color: #10B981 !important;
        color: white !important;
        text-align: center;
        padding: 14px;
        border-radius: 30px;
        font-weight: bold;
        display: block;
        text-decoration: none;
        margin-top: 15px;
        font-size: 16px;
        width: 100%;
        text-transform: uppercase;
    }

    .whatsapp-btn:hover {
        background-color: #059669 !important;
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None

if "selected_customer_idx" not in st.session_state:
    st.session_state.selected_customer_idx = 0

if "selected_day" not in st.session_state:
    st.session_state.selected_day = "Sat 05"

if "current_df" not in st.session_state:
    st.session_state.current_df = load_gsheet_data()


# ============================================================
# CURRENT DATA
# ============================================================
df_db = clean_dataframe(st.session_state.current_df)

st.session_state.current_df = df_db

customers_list = sorted(
    df_db["Customer"].dropna().unique().tolist()
)


# ============================================================
# LOGIN SCREEN
# ============================================================
if not st.session_state.logged_in:

    st.markdown(
        """
        <h2 style='text-align:center; margin-top:40px;'>
            🔐 Catering App Gateway Authentication
        </h2>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns(2)

    # --------------------------------------------------------
    # OWNER LOGIN
    # --------------------------------------------------------
    with col_l:

        st.markdown(
            "<div class='custom-section-box'>",
            unsafe_allow_html=True,
        )

        st.subheader("🛠️ Management Portal")

        owner_pass = st.text_input(
            "Enter Management Pin Password",
            type="password",
        )

        if st.button(
            "Access Admin Panel",
            use_container_width=True,
        ):

            if owner_pass == "admin123":

                st.session_state.logged_in = True
                st.session_state.user_role = "owner"
                st.session_state.selected_customer_idx = 0

                st.rerun()

            else:
                st.error(
                    "Incorrect portal pin access password entered."
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # CUSTOMER LOGIN
    # --------------------------------------------------------
    with col_r:

        st.markdown(
            "<div class='custom-section-box'>",
            unsafe_allow_html=True,
        )

        st.subheader("👤 Client Portal")

        if customers_list:

            client_user = st.selectbox(
                "Select Your Profile Name",
                options=customers_list,
            )

            if st.button(
                "Open My Tracking Dashboard",
                use_container_width=True,
            ):

                st.session_state.logged_in = True
                st.session_state.user_role = "customer"
                st.session_state.selected_customer = client_user

                st.rerun()

        else:
            st.error("No customer profiles are available.")

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    st.stop()


# ============================================================
# SIGN OUT
# ============================================================
if st.sidebar.button("🔒 Sign Out / Exit Profile"):

    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.selected_customer = None

    st.rerun()


# ============================================================
# DETERMINE USER ROLE
# ============================================================
is_owner = (
    st.session_state.user_role == "owner"
)


# ============================================================
# DETERMINE CUSTOMER
# ============================================================
if is_owner:

    if not customers_list:
        st.error("No customer profiles found.")
        st.stop()

    if (
        st.session_state.selected_customer_idx < 0
        or st.session_state.selected_customer_idx >= len(customers_list)
    ):
        st.session_state.selected_customer_idx = 0

    customer = customers_list[
        st.session_state.selected_customer_idx
    ]

else:

    customer = st.session_state.selected_customer

    if customer not in customers_list:
        st.error("Customer profile could not be found.")
        st.stop()


# ============================================================
# SELECTED DAY
# ============================================================
current_day = st.session_state.selected_day

if current_day not in DAYS_KEYS:
    current_day = DAYS_KEYS[0]
    st.session_state.selected_day = current_day


# ============================================================
# CUSTOMER DATA
# ============================================================
cust_df = df_db[
    df_db["Customer"] == customer
].copy()


phone_num = (
    str(cust_df["Phone"].iloc[0])
    if not cust_df.empty
    else ""
)


price_per_reg = (
    int(cust_df["BasePrice"].iloc[0])
    if not cust_df.empty
    else 120
)


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <p style='
        color:#3B82F6;
        font-weight:bold;
        margin-bottom:0px;
    '>
        SEPTEMBER 2026
        <span style='
            color:#64748B;
            font-weight:normal;
        '>
            • Cycle Mapping frame: Sat → Fri
        </span>
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h2 style='
        margin-top:0px;
        color:white;
    '>
        Customer Cycle Mapping Invoice Generator
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <p style='
        color:#94A3B8;
        font-size:14px;
        margin-bottom:25px;
    '>
        Current profile:
        <span style='
            color:#FFF;
            font-weight:600;
        '>
            {customer}
        </span>

        • Base Price: {price_per_reg} Tk
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOTALS
# ============================================================
total_reg_meals = (
    int(cust_df["RegQty"].sum())
    if not cust_df.empty
    else 0
)

total_spec_meals = (
    int(cust_df["SpecQty"].sum())
    if not cust_df.empty
    else 0
)

total_extra_chicken = (
    int(cust_df["ExtraChicken"].sum())
    if not cust_df.empty
    else 0
)

special_total = (
    int(
        (
            cust_df["SpecQty"]
            * cust_df["SpecPrice"]
        ).sum()
    )
    if not cust_df.empty
    else 0
)

total_bill = (
    (total_reg_meals * price_per_reg)
    + special_total
    + (total_extra_chicken * EXTRA_CHICKEN_PRICE)
)


# ============================================================
# DAY GRID + SUMMARY
# ============================================================
col_main, col_summary = st.columns(
    [3, 1]
)


# ============================================================
# DAY CARDS
# ============================================================
with col_main:

    day_cols = st.columns(7)

    for idx, day_id in enumerate(DAYS_KEYS):

        with day_cols[idx]:

            day_name, day_num = day_id.split()

            day_row = cust_df[
                cust_df["Day"] == day_id
            ]

            reg_q = (
                int(day_row["RegQty"].iloc[0])
                if not day_row.empty
                else 0
            )

            spec_q = (
                int(day_row["SpecQty"].iloc[0])
                if not day_row.empty
                else 0
            )

            has_note = (
                bool(
                    str(
                        day_row["OrderNotes"].iloc[0]
                    ).strip()
                )
                if (
                    not day_row.empty
                    and "OrderNotes" in day_row.columns
                )
                else False
            )

            is_active = (
                current_day == day_id
            )

            active_class = (
                "active"
                if is_active
                else ""
            )

            # Build badges.
            if spec_q > 0:

                badge_html = (
                    f"<div class='badge-item badge-spec'>"
                    f"Spc {spec_q}"
                    f"</div>"
                )

            elif reg_q > 0:

                badge_html = (
                    f"<div class='badge-item badge-reg'>"
                    f"Reg {reg_q}"
                    f"</div>"
                )

            else:

                badge_html = (
                    "<div class='badge-empty'></div>"
                )

            if has_note:

                badge_html += (
                    "<div class='badge-item badge-note'>"
                    "📝 Note"
                    "</div>"
                )

            # Card.
            st.markdown(
                f"""
                <div class="day-node-card {active_class}">
                    <div class="day-name">
                        {day_name}
                    </div>

                    <div class="day-date">
                        {day_num}
                    </div>

                    {badge_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Invisible/compact selection button.
            if st.button(
                f"Select {day_id}",
                key=f"btn_click_{day_id}",
                use_container_width=True,
            ):

                st.session_state.selected_day = day_id
                st.rerun()


# ============================================================
# OWNER CUSTOMER / RATE CONTROLS
# ============================================================
if is_owner:

    c_p, c_r = st.columns(2)

    with c_p:

        chosen_customer = st.selectbox(
            "Customer Profile",
            options=customers_list,
            index=customers_list.index(customer),
        )

        if chosen_customer != customer:

            st.session_state.selected_customer_idx = (
                customers_list.index(chosen_customer)
            )

            st.rerun()

    with c_r:

        rate_idx = (
            AVAILABLE_RATES.index(price_per_reg)
            if price_per_reg in AVAILABLE_RATES
            else 2
        )

        new_rate = st.selectbox(
            "Per-Meal Price (Tk)",
            options=AVAILABLE_RATES,
            index=rate_idx,
            format_func=lambda x: f"{x} Tk",
        )

        if new_rate != price_per_reg:

            df_db.loc[
                df_db["Customer"] == customer,
                "BasePrice",
            ] = new_rate

            save_gsheet_data(df_db)

            st.rerun()


# ============================================================
# SUMMARY
# ============================================================
with col_summary:

    st.markdown(
        f"""
        <div class="summary-card">

            <h3 style="color:white;">
                Cycle Summary
            </h3>

            <p>
                Regular meals total:
                <b>{total_reg_meals} pcs</b>
            </p>

            <p>
                Special meals total:
                <b>{total_spec_meals} pcs</b>
            </p>

            <p>
                Extra Chicken protein:
                <b>{total_extra_chicken} pcs</b>
            </p>

            <p>
                Base rate applied:
                <b>{price_per_reg} Tk</b>
            </p>

            <hr>

            <h2 style="color:#10B981;">
                Total Bill: {total_bill} Tk
            </h2>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DAILY PARAMETERS
# ============================================================
st.markdown("---")

st.markdown(
    f"### 🛠️ Daily Parameters Grid • {current_day.upper()} Config"
)


day_mask = (
    (df_db["Customer"] == customer)
    & (df_db["Day"] == current_day)
)

active_row = df_db[day_mask]


# ============================================================
# CURRENT NOTE
# ============================================================
if (
    not active_row.empty
    and "OrderNotes" in active_row.columns
):

    raw_note = active_row[
        "OrderNotes"
    ].iloc[0]

    curr_note = (
        ""
        if pd.isna(raw_note)
        else str(raw_note)
    )

else:

    curr_note = ""


# ============================================================
# OWNER DAILY CONTROLS
# ============================================================
if is_owner:

    # --------------------------------------------------------
    # ORDER NOTE
    # --------------------------------------------------------
    st.markdown(
        "### 📝 Special Order Note Tool"
    )

    new_note = st.text_input(
        "Tap to write custom update notes for this client's day entry",
        value=curr_note,
        placeholder=(
            "e.g. Extra spicy, holiday cancel..."
        ),
        key=f"note_edit_{current_day}",
    )

    if (
        new_note != curr_note
        and not active_row.empty
    ):

        df_db.loc[
            day_mask,
            "OrderNotes",
        ] = new_note

        save_gsheet_data(df_db)

        st.rerun()


# ============================================================
# CUSTOMER NOTE DISPLAY
# ============================================================
elif curr_note.strip():

    st.markdown(
        f"""
        <div class="custom-section-box">
            📝 <b>OWNER ORDER NOTE</b><br><br>
            {curr_note}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# OWNER MEAL CONFIGURATION
# ============================================================
if is_owner:

    # --------------------------------------------------------
    # CURRENT VALUES
    # --------------------------------------------------------
    if not active_row.empty:

        curr_reg = int(
            active_row["RegQty"].iloc[0]
        )

        curr_spec = int(
            active_row["SpecQty"].iloc[0]
        )

        curr_spec_p = int(
            active_row["SpecPrice"].iloc[0]
        )

        curr_extra = int(
            active_row["ExtraChicken"].iloc[0]
        )

    else:

        curr_reg = 0
        curr_spec = 0
        curr_spec_p = DEFAULT_SPECIAL_PRICE
        curr_extra = 0


    # ========================================================
    # REGULAR MEALS
    # ========================================================
    st.markdown(
        "### 🍱 Regular Meals Config"
    )

    new_reg = st.number_input(
        "Quantity Regular",
        min_value=0,
        value=curr_reg,
        step=1,
        key=f"r_edit_{current_day}",
    )

    if (
        new_reg != curr_reg
        and not active_row.empty
    ):

        df_db.loc[
            day_mask,
            "RegQty",
        ] = new_reg

        # Regular and Special are mutually exclusive.
        if new_reg > 0:

            df_db.loc[
                day_mask,
                "SpecQty",
            ] = 0

        save_gsheet_data(df_db)

        st.rerun()


    # ========================================================
    # SPECIAL MEALS
    # ========================================================
    st.markdown(
        "### ⭐ Special Section Config"
    )

    c1, c2 = st.columns(2)

    with c1:

        new_spec = st.number_input(
            "Quantity Special",
            min_value=0,
            value=curr_spec,
            step=1,
            key=f"s_edit_{current_day}",
        )

        if (
            new_spec != curr_spec
            and not active_row.empty
        ):

            df_db.loc[
                day_mask,
                "SpecQty",
            ] = new_spec

            # Special and Regular are mutually exclusive.
            if new_spec > 0:

                df_db.loc[
                    day_mask,
                    "RegQty",
                ] = 0

            save_gsheet_data(df_db)

            st.rerun()

    with c2:

        new_spec_p = st.number_input(
            "Custom Special Price (Tk)",
            min_value=0,
            value=curr_spec_p,
            step=10,
            key=f"sp_edit_{current_day}",
        )

        if (
            new_spec_p != curr_spec_p
            and not active_row.empty
        ):

            df_db.loc[
                day_mask,
                "SpecPrice",
            ] = new_spec_p

            save_gsheet_data(df_db)

            st.rerun()


    # ========================================================
    # EXTRA CHICKEN
    # ========================================================
    st.markdown(
        "### 🍗 Extra Chicken Protein Add-Ons"
    )

    new_extra = st.number_input(
        "Quantity Extra",
        min_value=0,
        value=curr_extra,
        step=1,
        key=f"e_edit_{current_day}",
    )

    if (
        new_extra != curr_extra
        and not active_row.empty
    ):

        df_db.loc[
            day_mask,
            "ExtraChicken",
        ] = new_extra

        save_gsheet_data(df_db)

        st.rerun()


# ============================================================
# WHATSAPP INVOICE
# ============================================================
st.markdown("---")

st.markdown(
    "### 💬 Invoice / WhatsApp"
)


invoice_msg = (
    f"Catering Invoice - {customer}\n"
    f"• Regular Meals: {total_reg_meals} pcs\n"
    f"• Special Meals: {total_spec_meals} pcs\n"
    f"• Extra Chicken: {total_extra_chicken} pcs\n"
    f"Total Due: {total_bill} Tk"
)


st.text_area(
    "Live Message Payload Preview",
    value=invoice_msg,
    height=130,
    disabled=True,
)


# Clean phone number.
clean_phone = (
    phone_num
    .replace("+", "")
    .replace(" ", "")
    .replace("-", "")
    .replace("(", "")
    .replace(")", "")
)


if clean_phone:

    whatsapp_link = (
        f"https://wa.me/{clean_phone}"
        f"?text={urllib.parse.quote(invoice_msg)}"
    )

    st.markdown(
        f"""
        <a
            href="{whatsapp_link}"
            target="_blank"
            class="whatsapp-btn"
        >
            ➤ OPEN WHATSAPP
        </a>
        """,
        unsafe_allow_html=True,
    )

else:

    st.warning(
        "No phone number is available for this customer."
    )


# ============================================================
# CUSTOMER VIEW
# ============================================================
if not is_owner:

    st.markdown("---")

    st.markdown(
        "### 📊 Delivered Order Record for Today"
    )

    if not active_row.empty:

        reg_delivered = int(
            active_row["RegQty"].iloc[0]
        )

        spec_delivered = int(
            active_row["SpecQty"].iloc[0]
        )

        spec_price = int(
            active_row["SpecPrice"].iloc[0]
        )

        extra_delivered = int(
            active_row["ExtraChicken"].iloc[0]
        )

        st.markdown(
            f"""
            <div class="custom-section-box">

                <p>
                    🍱 Regular Meals Delivered:
                    <b>{reg_delivered} pcs</b>
                </p>

                <p>
                    ⭐ Special Meals Delivered:
                    <b>{spec_delivered} pcs</b>
                    <br>
                    <span style="color:#94A3B8;">
                        Price: {spec_price} Tk
                    </span>
                </p>

                <p>
                    🍗 Extra Chicken Pieces Added:
                    <b>{extra_delivered} pieces</b>
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "No order record exists for this day."
        )
