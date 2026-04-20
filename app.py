import streamlit as st
import pathlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import csv
import io
import pandas as pd

# =========================
# LOAD CSS
# =========================
def load_css(file_path):
    with open(file_path, encoding="utf-8") as f:
        st.html(f"<style>{f.read()}</style>")


css_path = pathlib.Path("styles2.css")
load_css(css_path)

# =========================
# ADMIN / MOBILE BUTTON STATE
# =========================
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if "show_admin_panel" not in st.session_state:
    st.session_state["show_admin_panel"] = False

if "admin_password_error" not in st.session_state:
    st.session_state["admin_password_error"] = ""

if "show_inspection_report" not in st.session_state:
    st.session_state["show_inspection_report"] = False

if "report_headers" not in st.session_state:
    st.session_state["report_headers"] = []

if "report_results" not in st.session_state:
    st.session_state["report_results"] = []

if "report_csv_data" not in st.session_state:
    st.session_state["report_csv_data"] = ""

if "report_mode" not in st.session_state:
    st.session_state["report_mode"] = "inspection"

# change this to your real password
ADMIN_PASSWORD = "1234"

# =========================
# INSPECTION LISTS
# =========================
truck_list = [
    "Lights & Reflectors",
    "Tires & Wheels",
    "Brakes",
    "Steering & Suspension",
    "Fluid Levels",
    "Horn & Mirrors",
    "Safety Equipement",
    "Cab & Exterior Cleanliness"
]

trailer_list = [
    "Trailer Swept & Clean",
    "Door & Hinges",
    "Lights & Electrical",
    "Tires & Wheels",
    "Brakes & Brake Lines",
    "Suspension & Undercarriage",
    "Reflective Tape & Markings",
    "Load Securement Equipement"
]

moffett_list = [
    "Mouting Secure",
    "Lights",
    "Tires & Guards",
    "Operational Controls",
    "Hydrolic/Fluid Leaks",
    "Clean of Mud/Debris"
]

# =========================
# SHEET COLUMN ORDER
# Must match your Google Sheet exactly
# =========================
SHEET_COLUMNS = [
    "Driver Signature",
    "Stamp",
    "Date",
    "Time",
    "Route/Job #",
    "Corner Boards",
    "Truck #",
    "Truck Repair Notes",
    "Trailer Unit #",
    "Trailer Repair Notes",
    "Moffett Unit #",
    "Moffett Repair Notes",
    "Lights & Reflectors (Truck)",
    "Tires & Wheels (Truck)",
    "Brakes (Truck)",
    "Steering & Suspension (Truck)",
    "Fluid Levels (Truck)",
    "Horn & Mirrors (Truck)",
    "Safety Equipment (Truck)",
    "Cab & Exterior Cleanliness (Truck)",
    "Number of Winches",
    "Number of Straps",
    "Floor Clean (Trailer)",
    "Doors/Hinges/Latches (Trailer)",
    "Trailer Lights/Electrical (Trailer)",
    "Tires & Wheels (Trailer)",
    "Brakes & Brake Lines (Trailer)",
    "Suspension & Undercarriage (Trailer)",
    "Reflective Tape & Markings (Trailer)",
    "Load Securement Equipment (Trailer)",
    "Mounting Secure (Moffett)",
    "All Lights Functional (Moffett)",
    "Tires & Guards (Moffett)",
    "Operational Controls (Moffett)",
    "Hydraulic/Fluid Leaks (Moffett)",
    "Cleanliness (Moffett)"
]

# =========================
# APP FIELD -> SHEET COLUMN MAP
# =========================
APP_TO_SHEET_MAP = {
    "truck_item_0": "Lights & Reflectors (Truck)",
    "truck_item_1": "Tires & Wheels (Truck)",
    "truck_item_2": "Brakes (Truck)",
    "truck_item_3": "Steering & Suspension (Truck)",
    "truck_item_4": "Fluid Levels (Truck)",
    "truck_item_5": "Horn & Mirrors (Truck)",
    "truck_item_6": "Safety Equipment (Truck)",
    "truck_item_7": "Cab & Exterior Cleanliness (Truck)",

    "trailer_item_0": "Floor Clean (Trailer)",
    "trailer_item_1": "Doors/Hinges/Latches (Trailer)",
    "trailer_item_2": "Trailer Lights/Electrical (Trailer)",
    "trailer_item_3": "Tires & Wheels (Trailer)",
    "trailer_item_4": "Brakes & Brake Lines (Trailer)",
    "trailer_item_5": "Suspension & Undercarriage (Trailer)",
    "trailer_item_6": "Reflective Tape & Markings (Trailer)",
    "trailer_item_7": "Load Securement Equipment (Trailer)",

    "moffett_item_0": "Mounting Secure (Moffett)",
    "moffett_item_1": "All Lights Functional (Moffett)",
    "moffett_item_2": "Tires & Guards (Moffett)",
    "moffett_item_3": "Operational Controls (Moffett)",
    "moffett_item_4": "Hydraulic/Fluid Leaks (Moffett)",
    "moffett_item_5": "Cleanliness (Moffett)",
}

# =========================
# GOOGLE SHEETS CONNECTION
# =========================
@st.cache_resource
def get_worksheet():
    creds_info = dict(st.secrets["gcp_service_account"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        creds_info, scopes=scopes
    )
    client = gspread.authorize(credentials)

    sheet_id = st.secrets["google_sheet"]["sheet_id"]
    worksheet_name = st.secrets["google_sheet"]["worksheet_name"]

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet

# =========================
# REPORT HELPERS
# =========================
def get_inspection_report_rows(start_date, finish_date, mode="inspection"):
    worksheet = get_worksheet()
    all_rows = worksheet.get_all_values()

    report_rows = []

    if mode == "inspection":
        wanted_indexes = [0, 1, 4, 5, 6, 7, 8, 9, 10, 11]

        report_headers = [
            "Driver Signature",
            "Stamp",
            "Route/Job #",
            "Corner Boards",
            "Truck #",
            "Truck Repair Notes",
            "Trailer Unit #",
            "Trailer Repair Notes",
            "Moffett Unit #",
            "Moffett Repair Notes"
        ]

        for row in all_rows[1:]:
            if len(row) < 12:
                continue

            raw_date = row[2].strip()

            try:
                row_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except Exception:
                continue

            if not (start_date <= row_date <= finish_date):
                continue

            filtered_row = [row[i] if i < len(row) else "" for i in wanted_indexes]
            report_rows.append(filtered_row)

        return report_headers, report_rows

    elif mode == "repairs":
        report_headers = [
            "Driver Signature",
            "Stamp",
            "Category",
            "Unit #",
            "Repair Notes"
        ]

        truck_rows = []
        trailer_rows = []
        moffett_rows = []

        for row in all_rows[1:]:
            if len(row) < 12:
                continue

            raw_date = row[2].strip()

            try:
                row_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except Exception:
                continue

            if not (start_date <= row_date <= finish_date):
                continue

            driver_signature = row[0].strip() if len(row) > 0 else ""
            stamp = row[1].strip() if len(row) > 1 else ""

            truck_unit = row[6].strip() if len(row) > 6 else ""
            truck_notes = row[7].strip() if len(row) > 7 else ""

            trailer_unit = row[8].strip() if len(row) > 8 else ""
            trailer_notes = row[9].strip() if len(row) > 9 else ""

            moffett_unit = row[10].strip() if len(row) > 10 else ""
            moffett_notes = row[11].strip() if len(row) > 11 else ""

            if truck_notes:
                truck_rows.append([
                    driver_signature,
                    stamp,
                    "Truck",
                    truck_unit,
                    truck_notes
                ])

            if trailer_notes:
                trailer_rows.append([
                    driver_signature,
                    stamp,
                    "Trailer",
                    trailer_unit,
                    trailer_notes
                ])

            if moffett_notes:
                moffett_rows.append([
                    driver_signature,
                    stamp,
                    "Moffett",
                    moffett_unit,
                    moffett_notes
                ])

        report_rows = truck_rows + trailer_rows + moffett_rows
        return report_headers, report_rows


def build_report_csv_from_dataframe(df):
    return df.to_csv(index=False)

# =========================
# ADMIN DIALOG
# =========================
@st.dialog("Admin Access")
def admin_password_dialog():
    st.write("Enter password to continue.")

    password_value = st.text_input(
        "Password",
        type="password",
        key="admin_password_input"
    )

    if st.session_state.get("admin_password_error"):
        st.error(st.session_state["admin_password_error"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="admin_cancel_btn"):
            st.session_state["admin_password_error"] = ""
            st.rerun()

    with col2:
        if st.button("Enter", key="admin_enter_btn"):
            if password_value == ADMIN_PASSWORD:
                st.session_state["admin_authenticated"] = True
                st.session_state["show_admin_panel"] = True
                st.session_state["admin_password_error"] = ""
                st.rerun()
            else:
                st.session_state["admin_password_error"] = "Incorrect password."
                st.rerun()

# =========================
# ADMIN SCROLL LOCK
# =========================
def inject_admin_scroll_lock():
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            overflow: hidden !important;
            height: 100vh !important;
        }

        [data-testid="stMainBlockContainer"] {
            height: 100vh !important;
            overflow: hidden !important;
            padding-bottom: 0 !important;
        }

        .st-key-admin_panel_section {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            overflow-y: auto !important;
            background: white !important;
            z-index: 99999 !important;
            padding: 1rem 1rem 2rem 1rem !important;
            margin: 0 !important;
        }

        .st-key-admin_panel_section hr {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# REPORT SCROLL LOCK
# =========================
def inject_report_scroll_lock():
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            overflow: hidden !important;
            height: 100vh !important;
        }

        [data-testid="stMainBlockContainer"] {
            height: 100vh !important;
            overflow: hidden !important;
            padding-bottom: 0 !important;
        }

        .st-key-inspection_report_section {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            overflow-y: auto !important;
            background: white !important;
            z-index: 100000 !important;
            padding: 1rem 1rem 2rem 1rem !important;
            margin: 0 !important;
        }

        .st-key-inspection_report_section hr {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# FORM BUILDERS
# =========================
def inspection_rows(items, prefix):
    for i, label in enumerate(items):
        key = f"{prefix}_item_{i}"

        value = st.radio(
            label,
            ["OK", "Needs Repair"],
            index=None,
            horizontal=True,
            key=key,
        )

        if value == "Needs Repair":
            st.text_input(
                "Repairs:",
                key=f"{key}_notes"
            )

# =========================
# HELPERS
# =========================
def collect_repair_notes(prefix, items):
    notes_list = []

    for i, label in enumerate(items):
        key = f"{prefix}_item_{i}"
        value = st.session_state.get(key)

        if value == "Needs Repair":
            note = st.session_state.get(f"{key}_notes", "").strip()

            if note:
                notes_list.append(f"{label}: {note}")
            else:
                notes_list.append(f"{label}: Needs repair")

    return " | ".join(notes_list)


def build_row_data():
    tz = pytz.timezone("America/Chicago")
    now = datetime.now(tz)

    row_data = {col: "" for col in SHEET_COLUMNS}

    # top fields
    row_data["Driver Signature"] = str(
        st.session_state.get("driver_signature", "")
    ).strip()
    row_data["Stamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
    row_data["Date"] = now.strftime("%Y-%m-%d")
    row_data["Time"] = now.strftime("%H:%M:%S")
    row_data["Route/Job #"] = str(
        st.session_state.get("route_number", "")
    ).strip()
    row_data["Corner Boards"] = st.session_state.get("corners_count", 0)
    row_data["Truck #"] = str(
        st.session_state.get("truck_number", "")
    ).strip()
    row_data["Trailer Unit #"] = str(
        st.session_state.get("trailer_number", "")
    ).strip()
    row_data["Number of Winches"] = st.session_state.get("winches_count", 0)
    row_data["Number of Straps"] = st.session_state.get("straps_count", 0)
    row_data["Moffett Unit #"] = str(
        st.session_state.get("moffett_number", "")
    ).strip()

    # roll-up repair notes
    row_data["Truck Repair Notes"] = collect_repair_notes("truck", truck_list)
    row_data["Trailer Repair Notes"] = collect_repair_notes("trailer", trailer_list)
    row_data["Moffett Repair Notes"] = collect_repair_notes("moffett", moffett_list)

    # inspection statuses
    for app_key, sheet_col in APP_TO_SHEET_MAP.items():
        row_data[sheet_col] = st.session_state.get(app_key, "")

    row_values = [row_data[col] for col in SHEET_COLUMNS]
    return row_values


def validate_form():
    errors = []

    required_fields = [
        ("Driver Signature", "driver_signature"),
        ("Route/Job #", "route_number"),
        ("Truck #", "truck_number"),
        ("Trailer #", "trailer_number"),
        ("Moffett #", "moffett_number"),
        ("Corners Count", "corners_count"),
        ("Number of Winches", "winches_count"),
        ("Number of Straps", "straps_count")
    ]

    for label, key in required_fields:
        value = st.session_state.get(key)

        if value is None:
            errors.append(f"{label} is required")
        elif isinstance(value, str) and value.strip() == "":
            errors.append(f"{label} is required")

    sections = [
        ("truck", truck_list),
        ("trailer", trailer_list),
        ("moffett", moffett_list)
    ]

    for prefix, items in sections:
        for i, label in enumerate(items):
            key = f"{prefix}_item_{i}"
            value = st.session_state.get(key)

            if value is None:
                errors.append(f"{label} is not selected")
            elif value == "Needs Repair":
                notes_key = f"{key}_notes"
                notes = st.session_state.get(notes_key, "")
                if isinstance(notes, str) and notes.strip() == "":
                    errors.append(f"{label} needs repair notes")

    return errors


def clear_form():
    keys_to_clear = [
        "driver_signature",
        "route_number",
        "truck_number",
        "trailer_number",
        "moffett_number",
        "corners_count",
        "winches_count",
        "straps_count"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    for prefix, items in [
        ("truck", truck_list),
        ("trailer", trailer_list),
        ("moffett", moffett_list)
    ]:
        for i, _ in enumerate(items):
            key = f"{prefix}_item_{i}"
            notes_key = f"{key}_notes"

            if key in st.session_state:
                del st.session_state[key]
            if notes_key in st.session_state:
                del st.session_state[notes_key]

# =========================
# UI
# =========================
with st.container(key="header_title"):
    st.subheader("Equipement Inspection Check-In")

with st.container(key="top_inputs_section"):
    st.text_input("Driver Signature", key="driver_signature")
    st.text_input("Route/Job #", key="route_number")
    st.text_input("Truck #", key="truck_number")
    st.text_input("Trailer #", key="trailer_number")
    st.text_input("Moffett #", key="moffett_number")
    st.number_input("Corners Count", min_value=0, step=1, key="corners_count")

with st.container(key="title_section_truck"):
    st.subheader("Truck Inspection")

with st.container(key="inspection_section_truck"):
    inspection_rows(truck_list, "truck")

with st.container(key="title_section_trailer"):
    st.subheader("Trailer Inspection")

with st.container(key="inspection_section_trailer"):
    st.number_input("Winch Count", min_value=0, step=1, key="winches_count")
    st.number_input("Strap Count", min_value=0, step=1, key="straps_count")
    inspection_rows(trailer_list, "trailer")

with st.container(key="title_section_moffett"):
    st.subheader("Moffett Inspection")

with st.container(key="inspection_section_moffett"):
    inspection_rows(moffett_list, "moffett")

with st.container(key="submit_section"):
    if st.button("Submit"):
        errors = validate_form()

        if errors:
            st.error("Please fix the following:")
            for err in errors:
                st.write(f"- {err}")
        else:
            try:
                row_values = build_row_data()
                worksheet = get_worksheet()
                worksheet.append_row(
                    row_values,
                    value_input_option="USER_ENTERED"
                )

                st.session_state["save_success"] = True
                clear_form()
                st.rerun()

            except Exception as e:
                import traceback
                st.error("Could not save to Google Sheets.")
                st.write("Exception type:", type(e).__name__)
                st.write("Exception repr:", repr(e))
                st.code(traceback.format_exc())

if st.session_state.get("save_success"):
    st.success("Inspection Submitted and saved to Google Sheets ✅")
    del st.session_state["save_success"]

# =========================
# MOBILE BOTTOM ADMIN BUTTON
# =========================
with st.container(key="mobile_admin_wrap"):
    if st.button("Open Admin", key="mobile_admin_open", use_container_width=True):
        admin_password_dialog()

# =========================
# ADMIN PANEL
# =========================
if st.session_state.get("show_admin_panel") and st.session_state.get("admin_authenticated"):
    inject_admin_scroll_lock()

    with st.container(key="admin_panel_section"):
        st.subheader("Admin Panel")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        with col1:
            if st.button("Inspection Report", key="admin_btn_1", use_container_width=True):
                st.session_state["report_mode"] = "inspection"
                st.session_state["show_inspection_report"] = True
                st.rerun()

        with col2:
            if st.button("Repairs Report", key="admin_btn_2", use_container_width=True):
                st.session_state["report_mode"] = "repairs"
                st.session_state["show_inspection_report"] = True
                st.rerun()

        with col3:
            st.button("Button 3", key="admin_btn_3", use_container_width=True)

        with col4:
            st.button("Button 4", key="admin_btn_4", use_container_width=True)

        st.button("Button 5", key="admin_btn_5", use_container_width=True)

        if st.button("Close Admin Panel", key="close_admin_panel", use_container_width=True):
            st.session_state["show_admin_panel"] = False
            st.session_state["admin_authenticated"] = False
            st.session_state["admin_password_error"] = ""
            st.session_state["show_inspection_report"] = False
            st.session_state["report_headers"] = []
            st.session_state["report_results"] = []
            st.session_state["report_csv_data"] = ""
            st.session_state["report_mode"] = "inspection"
            st.rerun()

# =========================
# INSPECTION REPORT SCREEN
# =========================
if st.session_state.get("show_inspection_report"):
    inject_report_scroll_lock()

    with st.container(key="inspection_report_section"):
        mode = st.session_state.get("report_mode", "inspection")
        title = "Inspection Report" if mode == "inspection" else "Repairs Report"
        st.subheader(title)

        start_date = st.date_input("Start", key="report_start_date")
        finish_date = st.date_input("Finish", key="report_finish_date")

        if st.button("Generate Report", key="generate_report_btn", use_container_width=True):
            if start_date > finish_date:
                st.error("Start date cannot be after finish date.")
                st.session_state["report_headers"] = []
                st.session_state["report_results"] = []
                st.session_state["report_csv_data"] = ""
            else:
                try:
                    headers, rows = get_inspection_report_rows(start_date, finish_date, mode)
                    st.session_state["report_headers"] = headers
                    st.session_state["report_results"] = rows

                    if rows:
                        df = pd.DataFrame(rows, columns=headers)
                        st.session_state["report_csv_data"] = build_report_csv_from_dataframe(df)
                    else:
                        st.session_state["report_csv_data"] = ""

                    st.rerun()
                except Exception as e:
                    import traceback
                    st.error("Could not generate report.")
                    st.write("Exception type:", type(e).__name__)
                    st.write("Exception repr:", repr(e))
                    st.code(traceback.format_exc())

        report_headers = st.session_state.get("report_headers", [])
        report_results = st.session_state.get("report_results", [])
        report_csv_data = st.session_state.get("report_csv_data", "")

        if report_results:
            df = pd.DataFrame(report_results, columns=report_headers)
            st.dataframe(df, use_container_width=True)

            file_name = f"{mode}_report_{start_date}_{finish_date}.csv"

            st.download_button(
                label="Download CSV",
                data=report_csv_data,
                file_name=file_name,
                mime="text/csv",
                key="download_report_csv_btn",
                use_container_width=True,
                on_click="ignore"
            )

        elif st.session_state.get("report_results") == [] and st.session_state.get("report_headers"):
            st.info("No rows found in that date range.")

        if st.button("Back to Admin Panel", key="back_to_admin_panel_btn", use_container_width=True):
            st.session_state["show_inspection_report"] = False
            st.session_state["report_headers"] = []
            st.session_state["report_results"] = []
            st.session_state["report_csv_data"] = ""
            st.session_state["report_mode"] = "inspection"
            st.rerun()
