import streamlit as st
import pathlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =========================
# LOAD CSS
# =========================


def load_css(file_path):
    with open(file_path, encoding="utf-8") as f:
        st.html(f"<style>{f.read()}</style>")


css_path = pathlib.Path("styles2.css")
load_css(css_path)

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
    "Tires & Wheels (Truck)",  # keeping exactly as you typed it
    "Brakes (Truck)",
    "Steering & Suspension (Truck)",
    "Fluid Levels (Truck)",
    "Horn & Mirrors (Truck)",
    "Safety Equipment (Truck)",
    "Cab & Exterior Cleanliness (Truck)",
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
    now = datetime.now()

    row_data = {col: "" for col in SHEET_COLUMNS}

    # top fields
    row_data["Driver Signature"] = st.session_state.get(
        "driver_signature", "").strip()
    row_data["Stamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
    row_data["Date"] = now.strftime("%Y-%m-%d")
    row_data["Time"] = now.strftime("%H:%M:%S")
    row_data["Route/Job #"] = st.session_state.get("route_number", "").strip()
    row_data["Corner Boards"] = st.session_state.get("corners_count", 0)
    row_data["Truck #"] = st.session_state.get("truck_number", "").strip()
    row_data["Trailer Unit #"] = st.session_state.get(
        "trailer_number", "").strip()
    row_data["Moffett Unit #"] = st.session_state.get(
        "moffett_number", "").strip()

    # roll-up repair notes
    row_data["Truck Repair Notes"] = collect_repair_notes("truck", truck_list)
    row_data["Trailer Repair Notes"] = collect_repair_notes(
        "trailer", trailer_list)
    row_data["Moffett Repair Notes"] = collect_repair_notes(
        "moffett", moffett_list)

    # inspection statuses
    for app_key, sheet_col in APP_TO_SHEET_MAP.items():
        row_data[sheet_col] = st.session_state.get(app_key, "")

    # convert dict to list in exact sheet order
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
        ("Corners Count", "corners_count")
    ]

    for label, key in required_fields:
        value = st.session_state.get(key)

        if value is None:
            errors.append(f"{label} is required")
        elif isinstance(value, str) and value.strip() == "":
            errors.append(f"{label} is required")
        elif key == "corners_count" and value == 0:
            errors.append("Corners Count must be greater than 0")

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
        "corners_count"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    for prefix, items in [("truck", truck_list), ("trailer", trailer_list), ("moffett", moffett_list)]:
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
                    row_values, value_input_option="USER_ENTERED")
                st.success("Inspection Submitted and saved to Google Sheets ✅")
                clear_form()
                st.rerun()
            except Exception as e:
                st.error(f"Could not save to Google Sheets: {e}")


if st.button("Test Sheet Tabs"):
    try:
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
        spreadsheet = client.open_by_key(sheet_id)

        st.write([ws.title for ws in spreadsheet.worksheets()])

    except Exception as e:
        st.error(e)


if st.button("TEST WRITE"):
    try:
        worksheet = get_worksheet()

        # Write "TEST" into cell A2 (first row under headers)
        worksheet.update("A2", "TEST")

        st.success("Wrote TEST to A2 ✅")

    except Exception as e:
        st.error(f"Write failed: {e}")
