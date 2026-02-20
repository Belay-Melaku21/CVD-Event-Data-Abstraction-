import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Fix for NameError: Function defined before use
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] == "Belay Melaku" and st.session_state["password"] == "@Belay6669":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("Cardiovascular Disease Data Portal")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True

if check_password():
    st.title("CVD Event Data Abstraction Checklist")
    st.markdown("---")
    st.write("### Investigator Instructions")
    st.info("""Please ensure all clinical data is abstracted with the highest precision. 
    Maintaining patient confidentiality is our primary ethical duty. 
    Thank you for your dedication to accurate medical research.""")

    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_data_form", clear_on_submit=True):
        # Section 1
        st.subheader("SECTION 1: IDENTIFICATION")
        hc_name = st.selectbox("Health Center", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = st.text_input("Patient MRN")
        enroll_date = st.date_input("Date of Enrollment (Baseline Visit)")
        
        # Section 3: Lifestyle (With conditional logic)
        st.subheader("SECTION 3: LIFESTYLE")
        alcohol = st.selectbox("Alcohol Consumption", ["Non-user", "Current User"])
        avg_drinks = 0
        if alcohol == "Current User":
            avg_drinks = st.number_input("Average standard drinks/day", min_value=0.0, step=0.1)

        # Section 4: Clinical (With automatic calculations)
        st.subheader("SECTION 4: CLINICAL MEASUREMENTS")
        col1, col2 = st.columns(2)
        sbp = col1.number_input("SBP (mmHg)", min_value=50, max_value=250)
        dbp = col2.number_input("DBP (mmHg)", min_value=30, max_value=150)
        weight = col1.number_input("Weight (kg)", min_value=20.0)
        height = col2.number_input("Height (cm)", min_value=100.0)

        # Automatic BP Stage Logic
        bp_stage = "Normal"
        if sbp >= 160 or dbp >= 110: bp_stage = "Stage 3/4"
        elif 160 > sbp >= 160 or 109 >= dbp >= 100: bp_stage = "Stage 2"
        elif 159 >= sbp >= 140 or 99 >= dbp >= 91: bp_stage = "Stage 1"
        elif 139 >= sbp >= 121 or 89 >= dbp >= 81: bp_stage = "Pre-HTN"

        # Automatic BMI Logic
        bmi_val = round(weight / ((height/100)**2), 2)
        bmi_cat = "Normal"
        if bmi_val < 18.5: bmi_cat = "Underweight"
        elif 25 <= bmi_val <= 29.9: bmi_cat = "Overweight"
        elif bmi_val >= 30: bmi_cat = "Obese"

        # Section 7: Outcome
        st.subheader("SECTION 7: OUTCOME")
        cvd_occurred = st.radio("CVD Event Occurred?", ["No", "Yes"])
        event_type = "None"
        event_date = None
        if cvd_occurred == "Yes":
            event_type = st.selectbox("Event Type", ["Stroke", "Myocardial Infarction", "Heart Failure"])
            event_date = st.date_input("Date of CVD Event")

        # Automatic Duration Calculation
        end_date = event_date if cvd_occurred == "Yes" and event_date else datetime(2025, 11, 9).date()
        duration_months = (end_date.year - enroll_date.year) * 12 + (end_date.month - enroll_date.month)

        if st.form_submit_button("Submit Record to Database"):
            new_row = pd.DataFrame([{
                "HC Name": hc_name, "MRN": mrn, "Enroll Date": str(enroll_date),
                "Alcohol": alcohol, "Avg Drinks": avg_drinks, "SBP": sbp, "DBP": dbp,
                "BP Stage": bp_stage, "BMI": bmi_val, "BMI Category": bmi_cat,
                "Duration (Months)": duration_months, "CVD Event": cvd_occurred, 
                "Event Type": event_type, "Submit Email": "melakubelay93@gmail.com"
            }])
            try:
                conn.create(data=new_row)
                st.success("Record successfully added to Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Error connecting to Google Sheets: {e}")
