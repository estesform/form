import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

st.set_page_config(page_title="Equipment Inspection", layout="wide")

# -----------------------------
# Google Sheets connection
# -----------------------------
@st.cache_resource
def get_worksheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(st.secrets["google_sheet"]["sheet_id"])
    worksheet = spreadsheet.worksheet("Inspections")
    return worksheet


def status_options():
    return ["", "OK", "Needs Repair"]


def inspection_field(prefix, label):
    col1, col2 = st.columns([1, 2])
    with col1:
        status = st.selectbox(
            f"{label} Status",
            status_options(),
            key=f"{prefix}_status"
        )
    with col2:
        notes = st.text_input(
            f"{label} Notes",
            key=f"{prefix}_notes",
            placeholder="Describe issue if needed"
        )
    return status, notes


st.title("Equipment Inspection Check-In Sheet")

with st.form("inspection_form"):
    st.subheader("General Information")
    g1, g2 = st.columns(2)

    with g1:
        company_name = st.text_input("Company Name")
        driver_name = st.text_input("Driver Name")
        inspection_date = st.date_input("Date", value=date.today())
        route_job = st.text_input("Route / Job #")

    with g2:
        time_recorded = st.text_input("Time")
        corner_boards = st.text_input("Corner Boards")
        driver_signature = st.text_input("Driver Signature")
        driver_signature_time = st.text_input("Driver Signature Time")

    supervisor_signature = st.text_input("Supervisor Signature")
    supervisor_signature_time = st.text_input("Supervisor Signature Time")

    st.divider()
    st.subheader("1. Truck Inspection")
    truck_unit_number = st.text_input("Truck Unit #")

    truck_lights_reflectors_status, truck_lights_reflectors_notes = inspection_field(
        "truck_lights_reflectors", "Lights & Reflectors"
    )
    truck_tires_wheels_status, truck_tires_wheels_notes = inspection_field(
        "truck_tires_wheels", "Tires & Wheels"
    )
    truck_brakes_status, truck_brakes_notes = inspection_field(
        "truck_brakes", "Brakes"
    )
    truck_steering_suspension_status, truck_steering_suspension_notes = inspection_field(
        "truck_steering_suspension", "Steering & Suspension"
    )
    truck_fluid_levels_status, truck_fluid_levels_notes = inspection_field(
        "truck_fluid_levels", "Fluid Levels"
    )
    truck_horn_mirrors_status, truck_horn_mirrors_notes = inspection_field(
        "truck_horn_mirrors", "Horn & Mirrors"
    )
    truck_safety_equipment_status, truck_safety_equipment_notes = inspection_field(
        "truck_safety_equipment", "Safety Equipment"
    )
    truck_cab_cleanliness_status, truck_cab_cleanliness_notes = inspection_field(
        "truck_cab_cleanliness", "Cab & Exterior Cleanliness"
    )

    st.divider()
    st.subheader("2. Trailer Inspection")
    trailer_unit_number = st.text_input("Trailer Unit #")

    trailer_interior_clean_status, trailer_interior_clean_notes = inspection_field(
        "trailer_interior_clean", "Trailer Interior Clean & Debris Free"
    )
    trailer_floor_clean_status, trailer_floor_clean_notes = inspection_field(
        "trailer_floor_clean", "Trailer Floor Swept & Clean"
    )
    trailer_doors_hinges_latches_status, trailer_doors_hinges_latches_notes = inspection_field(
        "trailer_doors_hinges_latches", "Doors, Hinges & Latches"
    )
    trailer_lights_electrical_status, trailer_lights_electrical_notes = inspection_field(
        "trailer_lights_electrical", "Trailer Lights & Electrical"
    )
    trailer_tires_wheels_status, trailer_tires_wheels_notes = inspection_field(
        "trailer_tires_wheels", "Tires & Wheels"
    )
    trailer_brakes_lines_status, trailer_brakes_lines_notes = inspection_field(
        "trailer_brakes_lines", "Brakes & Brake Lines"
    )
    trailer_suspension_undercarriage_status, trailer_suspension_undercarriage_notes = inspection_field(
        "trailer_suspension_undercarriage", "Suspension & Undercarriage"
    )
    trailer_reflective_tape_markings_status, trailer_reflective_tape_markings_notes = inspection_field(
        "trailer_reflective_tape_markings", "Reflective Tape & Markings"
    )
    trailer_load_securement_status, trailer_load_securement_notes = inspection_field(
        "trailer_load_securement", "Load Securement Equipment"
    )

    st.divider()
    st.subheader("3. Moffett Inspection")
    moffett_unit_number = st.text_input("Moffett Unit #")

    moffett_mounting_secure_status, moffett_mounting_secure_notes = inspection_field(
        "moffett_mounting_secure", "Mounting Secure"
    )
    moffett_lights_status, moffett_lights_notes = inspection_field(
        "moffett_lights", "All Lights Functional"
    )
    moffett_tires_guards_status, moffett_tires_guards_notes = inspection_field(
        "moffett_tires_guards", "Tires & Guards"
    )
    moffett_operational_controls_status, moffett_operational_controls_notes = inspection_field(
        "moffett_operational_controls", "Operational Controls"
    )
    moffett_hydraulic_leaks_status, moffett_hydraulic_leaks_notes = inspection_field(
        "moffett_hydraulic_leaks", "Hydraulic / Fluid Leaks"
    )
    moffett_cleanliness_status, moffett_cleanliness_notes = inspection_field(
        "moffett_cleanliness", "Cleanliness (Mud/Debris Free)"
    )

    submitted = st.form_submit_button("Submit Inspection")

    if submitted:
        try:
            worksheet = get_worksheet()

            row = [
                datetime.now().isoformat(),
                company_name,
                driver_name,
                inspection_date.isoformat() if inspection_date else "",
                route_job,
                time_recorded,
                corner_boards,

                truck_unit_number,
                truck_lights_reflectors_status, truck_lights_reflectors_notes,
                truck_tires_wheels_status, truck_tires_wheels_notes,
                truck_brakes_status, truck_brakes_notes,
                truck_steering_suspension_status, truck_steering_suspension_notes,
                truck_fluid_levels_status, truck_fluid_levels_notes,
                truck_horn_mirrors_status, truck_horn_mirrors_notes,
                truck_safety_equipment_status, truck_safety_equipment_notes,
                truck_cab_cleanliness_status, truck_cab_cleanliness_notes,

                trailer_unit_number,
                trailer_interior_clean_status, trailer_interior_clean_notes,
                trailer_floor_clean_status, trailer_floor_clean_notes,
                trailer_doors_hinges_latches_status, trailer_doors_hinges_latches_notes,
                trailer_lights_electrical_status, trailer_lights_electrical_notes,
                trailer_tires_wheels_status, trailer_tires_wheels_notes,
                trailer_brakes_lines_status, trailer_brakes_lines_notes,
                trailer_suspension_undercarriage_status, trailer_suspension_undercarriage_notes,
                trailer_reflective_tape_markings_status, trailer_reflective_tape_markings_notes,
                trailer_load_securement_status, trailer_load_securement_notes,

                moffett_unit_number,
                moffett_mounting_secure_status, moffett_mounting_secure_notes,
                moffett_lights_status, moffett_lights_notes,
                moffett_tires_guards_status, moffett_tires_guards_notes,
                moffett_operational_controls_status, moffett_operational_controls_notes,
                moffett_hydraulic_leaks_status, moffett_hydraulic_leaks_notes,
                moffett_cleanliness_status, moffett_cleanliness_notes,

                driver_signature,
                driver_signature_time,
                supervisor_signature,
                supervisor_signature_time,
            ]

            worksheet.append_row(row)
            st.success("Inspection submitted successfully.")

        except Exception as e:
            st.error(f"Error saving inspection: {e}")
