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


with st.form("inspection_form"):
    st.subheader("General Info")

    
    driver_name = st.text_input("Driver Name")
    inspection_date = st.date_input("Date", value=date.today())
    route_job = st.text_input("Route / Job #")
    truck_unit_number = st.text_input("Truck Unit #")
    trailer_unit_number = st.text_input("Trailer Unit #")
    moffett_unit_number = st.text_input("Moffett Unit #")
    driver_signature = st.text_input("Driver Signature")
    submitted = st.form_submit_button("Submit Inspection")


if submitted:
    try:
        worksheet = get_worksheet()

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            driver_name,
            inspection_date.isoformat(),
            route_job,
            time_recorded,
            truck_unit_number,
            trailer_unit_number,
            moffett_unit_number,
            driver_signature,
        ]

        next_row = get_next_row(worksheet)
        end_col_letter = chr(64 + len(row))  # 13 columns = M
        cell_range = f"A{next_row}:{end_col_letter}{next_row}"

        worksheet.update(cell_range, [row], value_input_option="USER_ENTERED")
        st.success("Inspection submitted successfully!")

    except Exception as e:
        st.exception(e)
