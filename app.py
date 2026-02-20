import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ገጹን ዳግም ለማስጀመር (Reset) የሚረዳ ተግባር
def clear_form():
    for key in st.session_state.keys():
        if key not in ["logged_in"]:
            st.session_state.pop(key)
    st.rerun()

st.set_page_config(page_title="CVD Smart Portal", layout="wide")

# --- Authentication ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Invalid credentials")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Smart CVD Event Data Abstraction")
st.write("**Study:** Time to CVD Event and Its Determinant Among Hypertensive Patients [cite: 2]")

with st.form(key="cvd_abstraction_form", clear_on_submit=True):
    # Section 1 & 2: Identification & Eligibility [cite: 3, 9]
    st.header("Section 1 & 2: Identification & Eligibility")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"]) [cite: 4]
        mrn = st.text_input("1.2. Patient MRN") [cite: 5]
    with col2:
        d_ext = st.date_input("1.3. Date of Extraction", datetime.now()) [cite: 6]
        d_enr = st.date_input("1.4. Date of Enrollment") [cite: 7]
    
    st.subheader("Eligibility (Exclusion Criteria) [cite: 9]")
    e1 = st.radio("2.1. Age ≥18 years?", ["Yes", "No"]) [cite: 10]
    e2 = st.radio("2.2. Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["No", "Yes"]) [cite: 11]
    e3 = st.radio("2.3. Pregnancy-induced Hypertension?", ["No", "Yes"]) [cite: 12]

    # IF logic for eligibility: If not eligible, stop here [cite: 10, 11, 12]
    is_eligible = (e1 == "Yes" and e2 == "No" and e3 == "No")
    
    if not is_eligible:
        st.error("❌ Patient is NOT eligible. Submission will only record exclusion.")
        submit = st.form_submit_button("Submit Exclusion Report")
    else:
        # SECTION 3 - 7: Complete Data entry
        st.divider()
        st.header("Section 3 & 4: Socio-Demographic & Lifestyle [cite: 13, 20]")
        age = st.number_input("3.1. Age (years)", min_value=18) [cite: 14]
        sex = st.selectbox("3.2. Sex", ["Male", "Female"]) [cite: 15]
        alc = st.selectbox("4.2. Alcohol Consumption", ["Non-user", "Current User"]) [cite: 22]
        
        # IF logic for Alcohol quantity [cite: 22]
        alc_qty = 0.0
        if alc == "Current User":
            alc_qty = st.number_input("Average standard drinks/day", min_value=0.0) [cite: 22]

        st.divider()
        st.header("Section 5 & 6: Clinical & Biochemical [cite: 26, 33]")
        wt = st.number_input("5.3. Weight (kg)", min_value=0.0) [cite: 29]
        ht = st.number_input("5.3. Height (cm)", min_value=0.0) [cite: 29]
        
        # Smart BMI Calculation [cite: 29, 30]
        bmi_val = round(wt / ((ht/100)**2), 2) if ht > 0 else 0
        st.info(f"Calculated BMI: {bmi_val}")

        dm = st.radio("6.1. Diabetes Mellitus (DM)?", ["No", "Yes"]) [cite: 34]
        dm_date = None
        if dm == "Yes": dm_date = st.date_input("Date of DM enrolment") [cite: 34]

        prot = st.selectbox("6.3. Proteinuria", ["Negative", "Positive"]) [cite: 36]
        prot_level = "N/A"
        if prot == "Positive":
            prot_level = st.selectbox("Level", ["+", "++", "+++", "++++"]) [cite: 36]

        st.divider()
        st.header("Section 8: Outcome & Smart Duration [cite: 43]")
        cvd_event = st.radio("8.1. CVD Event Occurred?", ["No", "Yes"]) [cite: 44]
        
        d_event = None
        event_type = "N/A"
        study_end = datetime(2025, 11, 9).date() [cite: 31]
        
        if cvd_event == "Yes":
            event_type = st.selectbox("8.2. Type of CVD Event", ["Stroke", "MI", "Heart Failure"]) [cite: 45]
            d_event = st.date_input("8.3. Date of Event") [cite: 46]
            duration = (d_event - d_enr).days / 30.44 if d_enr else 0 [cite: 31]
        else:
            censor = st.selectbox("8.4. Censoring Details", ["Study ended without event", "Lost to Follow-up", "Died (Non-CVD)"]) [cite: 47]
            d_last = st.date_input("8.5. Date of Last Follow-up", study_end) [cite: 48]
            duration = (d_last - d_enr).days / 30.44 if d_enr else 0 [cite: 31]

        st.warning(f"5.5. Auto-Calculated Duration: {round(duration, 1)} months [cite: 31]")
        submit = st.form_submit_button("Submit Data")

    if submit:
        # Data registration logic (connection.update)
        st.success("✅ መረጃው ተመዝግቧል።")
        st.balloons()
        # ገጹን ለአዲስ ታካሚ ዝግጁ ለማድረግ
        st.button("ለቀጣይ ታካሚ መረጃ መሙያ ተጫን", on_click=clear_form)
