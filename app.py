import streamlit as st
import pathlib
from datetime import date

# Load CSS


def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")


css_path = pathlib.Path("styles2.css")
load_css(css_path)

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
        errors = []

        # Check top required fields
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

        # Check all inspection sections
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

        # Show result
        if len(errors) == 0:
            st.success("Inspection Submitted ✅")
        else:
            st.error("Please fix the following:")
            for err in errors:
                st.write(f"- {err}")
