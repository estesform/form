import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

st.set_page_config(page_title="Equipment Inspection", layout="wide")
st.title("Equipment Inspection Check-In Sheet")


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

    header_cols = st.columns([3, 1, 2])
    with header_cols[0]:
        st.markdown("**Item**")
    with header_cols[1]:
        st.markdown("**Status**")
    with header_cols[2]:
        st.markdown("**Notes**")

    for item in items:
        col1, col2, col3 = st.columns([3, 1, 2])

        with col1:
            st.write(item)

        with col2:
            status = st.selectbox(
                f"Status for {item}",
                ["OK", "Needs Repair"],
                key=f"{section_title}_{item}_status",
                label_visibility="collapsed"
            )

        note = ""
        with col3:
            if status == "Needs Repair":
                note = st.text_input(
                    f"Notes for {item}",
                    key=f"{section_title}_{item}_note",
                    label_visibility="collapsed",
                    placeholder="Describe issue"
                )

        results[item] = {
            "status": status,
            "note": note
        }

    return results


def format_section_results(results):
    entries = []
    for item, data in results.items():
        if data["status"] == "Needs Repair":
            if data["note"].strip():
                entries.append(f"{item}: Needs Repair ({data['note']})")
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
