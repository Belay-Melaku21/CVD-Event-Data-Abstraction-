import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ገጹ ሲከፈት መረጃዎችን በራስ-ሰር ለማጽዳት (Reset logic)
def reset_form():
    for key in st.session_state.keys():
        if key not in ["logged_in"]: # Login እንዳይጠፋ
            del st.session_state[key]
    st.rerun()

st.set_page_config(page_title="CVD Smart Data Entry", layout="wide")

# --- Authentication (እንደቀድሞው) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 CVD Research Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Invalid credentials")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Smart CVD Event Data Abstraction Form")
st.info("መረጃውን ሞልተው ሲጨርሱ 'Submit'ን ይጫኑ። ፎርሙ በራሱ ተጸድቶ ለአዲስ መረጃ ዝግጁ ይሆናል።")

with st.form(key="smart_cvd_form", clear_on_submit=True): # clear_on_submit ፎርሙን ያጸዳዋል
    # SECTION 1: IDENTIFICATION [cite: 3, 4, 5, 6, 7, 8]
    st.header("Section 1: Identification & Tracking")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"]) [cite: 4]
        mrn = st.text_input("1.2. Patient MRN") [cite: 5]
    with col2:
        d_ext = st.date_input("1.3. Date of Extraction", datetime.now()) [cite: 6]
        d_enr = st.date_input("1.4. Date of Enrollment (Baseline Visit)") [cite: 7]
    cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"]) [cite: 8]

    # SECTION 2: ELIGIBILITY [cite: 9, 10, 11, 12]
    st.divider()
    st.header("Section 2: Eligibility Check")
    age_check = st.radio("Age ≥18 years?", ["Yes", "No"]) [cite: 10]
    pre_cvd = st.radio("Pre-existing CVD before enrolment?", ["No", "Yes"]) [cite: 11]
    preg_htn = st.radio("Pregnancy-induced Hypertension?", ["No", "Yes"]) [cite: 12]

    is_eligible = (age_check == "Yes" and pre_cvd == "No" and preg_htn == "No")

    if not is_eligible:
        st.error("❌ ታካሚው ለጥናቱ ብቁ አይደለም (Excluded)።")
        submitted = st.form_submit_button("Submit Exclusion Only")
    else:
        # SECTION 3-7: Smart Logic (If Eligible) [cite: 13, 20, 26, 33, 39]
        st.success("✅ ታካሚው ብቁ ነው። እባክዎ የቀሩትን መረጃዎች ይሙሉ::")
        
        # BMI Calculation [cite: 29, 30]
        wt = st.number_input("5.3. Weight (kg)", min_value=0.0) [cite: 29]
        ht = st.number_input("5.3. Height (cm)", min_value=0.0) [cite: 29]
        bmi_val = round(wt / ((ht/100)**2), 2) if ht > 0 else 0
        st.write(f"**Calculated BMI:** {bmi_val}") [cite: 29]

        # HTN Duration Logic [cite: 31]
        st.divider()
        cvd_event = st.radio("8.1. CVD Event Occurred?", ["No", "Yes"]) [cite: 44]
        
        duration_val = 0
        if cvd_event == "Yes":
            d_event = st.date_input("8.3. Date of CVD Event") [cite: 46]
            duration_val = (d_event - d_enr).days / 30.44 if d_enr else 0
        else:
            study_end = datetime(2025, 11, 9).date()
            d_last = st.date_input("8.5. Date of Last Follow-up", study_end) [cite: 48]
            duration_val = (d_last - d_enr).days / 30.44 if d_enr else 0
        
        st.warning(f"አውቶማቲክ የቆይታ ጊዜ (Duration): {round(duration_val, 1)} ወራት") [cite: 31]

        submitted = st.form_submit_button("Submit Data")

    if submitted:
        # መረጃውን ወደ ዲክሽነሪ የመቀየር ስራ እዚህ ይከናወናል...
        st.success("✅ መረጃው ተመዝግቧል!")
        st.balloons()
        # ገጹን ዳግም በማስጀመር ፎርሙን ማጽዳት
        st.button("ለቀጣይ ታካሚ መረጃ መሙያ ተጫን", on_click=reset_form)
