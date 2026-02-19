import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ገጹን ማዘጋጀት
st.set_page_config(page_title="Data Abstraction Checklist", layout="wide")

# የመግቢያ ገጽ (Login) 
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("የመግቢያ ገጽ")
    user = st.text_input("ተጠቃሚ ስም (User Name)")
    password = st.text_input("የይለፍ ቃል (Password)", type="password")
    
    if st.button("ግባ"):
        if user == "Belay Melaku" and password == "CVD2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("የተሳሳተ መረጃ ገብቷል!")
else:
    st.title("Data Abstraction Checklist")
    
    # የGoogle Sheet ግንኙነት
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("abstraction_form"):
        # Section 1: Administrative [cite: 3-9]
        st.header("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        study_id = col1.text_input("Study ID")
        facility = col1.selectbox("Facility Name", [1, 2, 3, 4, 5], 
                                  format_func=lambda x: {1:"Densa", 2:"Kotet", 3:"Work-Mawcha", 4:"Ahyo", 5:"Atrons"}[x])
        mrn = col2.text_input("Patient MRN")
        cohort = col2.selectbox("Cohort Group", [1, 2], format_func=lambda x: "Exposed" if x==1 else "Unexposed")
        enroll_date = st.text_input("Date of Enrollment (E.C.)")
        end_date = st.text_input("Follow-up End Date (E.C.)")

        # Section 2: Eligibility [cite: 10-13]
        st.header("Section 2: Eligibility Checklist")
        age_el = st.radio("Age ≥18 years?", [1, 2], format_func=lambda x: "Yes" if x==1 else "No")
        pre_cvd = st.radio("Pre-existing CVD?", [1, 2], format_func=lambda x: "Yes (Exclude)" if x==1 else "No")
        
        # Section 4: Clinical [cite: 21-29]
        st.header("Section 4: Clinical Predictors")
        sbp = st.number_input("SBP (mmHg)", min_value=0)
        dbp = st.number_input("DBP (mmHg)", min_value=0)
        bmi = st.number_input("Weight (kg)") / (st.number_input("Height (m)")**2 if st.number_input("Height (m)") > 0 else 1)
        
        # መረጃውን ለመላክ
        submitted = st.form_submit_button("መረጃውን መዝግብ")
        
        if submitted:
            # እዚህ ጋር ሁሉንም ዳታ ወደ DataFrame መቀየር እና ወደ Sheet መላክ ኮድ ይታከላል
            st.success("መረጃው በትክክል ተመዝግቧል!")
