import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

st.set_page_config(page_title="Equipment Inspection", layout="wide")
st.title("Equipment Inspection Check-In Sheet")

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

div[data-testid="stTextInput"] {
    margin-bottom: 0.35rem !important;
}

div[data-testid="stTextInput"] input {
    min-height: 2.6rem !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_worksheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scope
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(st.secrets["google_sheet"]["sheet_id"])
    worksheet = spreadsheet.worksheet(st.secrets["google_sheet"]["worksheet_name"])
    return worksheet


def get_next_row(worksheet):
    col_a = worksheet.col_values(1)
    return len(col_a) + 1


def init_prefilled_field(key, prefix):
    if key not in st.session_state:
        st.session_state[key] = prefix


def clean_prefilled_value(value, prefix):
    if not value:
        return ""

    if value == prefix:
        return ""

    if value.startswith(prefix):
        return value[len(prefix):].strip()

    return value.strip()


def inspection_text_section(section_title, items):
    st.subheader(section_title)
    results = {}

    for item in items:
        key = f"{section_title}_{item}_note"
        prefix = f"{item}: "

        init_prefilled_field(key, prefix)

        value = st.text_input(
            label="",
            key=key,
            placeholder=item
        )

        results[item] = {
            "full_text": value,
            "prefix": prefix,
            "note_only": clean_prefilled_value(value, prefix)
        }

    return results


def format_section_results(results):
    entries = []

    for item, data in results.items():
        note_only = data["note_only"]
        prefix = data["prefix"]

        if note_only:
            entries.append(f"{prefix}{note_only}")

    return " | ".join(entries) if entries else "PASS"


truck_items = [
    "Truck Unit #",
    "Lights & Reflectors",
    "Tires & Wheels",
    "Brakes",
    "Steering & Suspension",
    "Fluid Levels",
    "Horn & Mirrors",
    "Safety Equipment",
    "Cab & Exterior Cleanliness",
]

trailer_items = [
    "Trailer Unit #",
    "Trailer Interior Clean & Debris Free",
    "Trailer Floor Swept & Clean",
    "Doors, Hinges & Latches",
    "Trailer Lights & Electrical",
    "Tires & Wheels",
    "Brakes & Brake Lines",
    "Suspension & Undercarriage",
    "Reflective Tape & Markings",
    "Load Securement Equipment",
]

lift_items = [
    "Moffett Unit #",
    "Mounting Secure",
    "All Lights Functional",
    "Tires & Guards",
    "Operational Controls",
    "Hydraulic / Fluid Leaks",
    "Cleanliness (Mud/Debris Free)",
]


with st.form("inspection_form"):
    st.subheader("General Info")

    driver_name = st.text_input("Driver Name")
    inspection_date = st.date_input("Date", value=date.today())
    route_job = st.text_input("Route / Job #")
    truck_unit_number = st.text_input("Truck Unit #")
    trailer_unit_number = st.text_input("Trailer Unit #")
    moffett_unit_number = st.text_input("Moffett Unit #")
    driver_signature = st.text_input("Driver Signature")

    st.markdown("---")
    truck_results = inspection_text_section("Truck Inspection", truck_items)

    st.markdown("---")
    trailer_results = inspection_text_section("Trailer Inspection", trailer_items)

    st.markdown("---")
    lift_results = inspection_text_section("Lift Inspection", lift_items)

    submitted = st.form_submit_button("Submit Inspection")


if submitted:
    try:
        worksheet = get_worksheet()

        truck_summary = format_section_results(truck_results)
        trailer_summary = format_section_results(trailer_results)
        lift_summary = format_section_results(lift_results)

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            driver_name,
            inspection_date.isoformat(),
            route_job,
            truck_unit_number,
            trailer_unit_number,
            moffett_unit_number,
            driver_signature,
            truck_summary,
            trailer_summary,
            lift_summary,
        ]

        next_row = get_next_row(worksheet)
        end_col_letter = chr(64 + len(row))
        cell_range = f"A{next_row}:{end_col_letter}{next_row}"

        worksheet.update(cell_range, [row], value_input_option="USER_ENTERED")
        st.success("Inspection submitted successfully!")

    except Exception as e:
        st.exception(e)
