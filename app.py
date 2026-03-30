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

/* tighter spacing overall */
div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 0.35rem;
}

/* section item title */
.inspection-item-label {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.35rem;
    margin-bottom: 0.2rem;
}

/* custom floating-ish label */
.notes-floating-label {
    color: #6a00cc;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: -0.35rem;
    margin-left: 0.75rem;
    background: white;
    display: inline-block;
    padding: 0 0.3rem;
    position: relative;
    z-index: 10;
}

/* make select compact */
div[data-baseweb="select"] {
    min-width: 110px !important;
}

div[data-baseweb="select"] > div {
    min-height: 2.8rem !important;
    border-radius: 12px !important;
}

/* style text inputs more like your screenshot */
div[data-testid="stTextInput"] input {
    min-height: 2.8rem !important;
    border: 3px solid #6a00cc !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    padding-top: 0.9rem !important;
    padding-bottom: 0.45rem !important;
}

/* keep hidden labels from leaving awkward space */
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label {
    display: none !important;
}

/* placeholder styling */
div[data-testid="stTextInput"] input::placeholder {
    color: #999 !important;
    opacity: 1 !important;
}

/* tighten column alignment a bit */
div[data-testid="column"] {
    padding-top: 0 !important;
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


def checklist_section(section_title, items):
    st.subheader(section_title)
    results = {}

    for item in items:
        st.markdown(f'<div class="inspection-item-label">{item}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2.6], gap="small")

        with col1:
            status = st.selectbox(
                f"Status for {section_title} - {item}",
                ["OK", "Needs Repair"],
                key=f"{section_title}_{item}_status",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown('<div class="notes-floating-label">Label</div>', unsafe_allow_html=True)
            note = st.text_input(
                f"Notes for {section_title} - {item}",
                key=f"{section_title}_{item}_note",
                label_visibility="collapsed",
                placeholder="Input text"
            )

        results[item] = {
            "status": status,
            "note": note.strip()
        }

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    return results


def format_section_results(results):
    entries = []

    for item, data in results.items():
        status = data["status"]
        note = data["note"]

        if status == "Needs Repair":
            if note:
                entries.append(f"{item}: Needs Repair ({note})")
            else:
                entries.append(f"{item}: Needs Repair")

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
    truck_results = checklist_section("Truck Inspection", truck_items)

    st.markdown("---")
    trailer_results = checklist_section("Trailer Inspection", trailer_items)

    st.markdown("---")
    lift_results = checklist_section("Lift Inspection", lift_items)

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
