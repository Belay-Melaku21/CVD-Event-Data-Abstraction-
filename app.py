import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="CVD Data Abstraction", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Secure Data Entry Login")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and password == "@Belay6669":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
        return False
    return True

# --- EMAIL FUNCTION ---
def send_summary_email(data_dict):
    try:
        sender = st.secrets["email_sender"]
        pwd = st.secrets["email_password"]
        receiver = st.secrets["email_receiver"]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"New CVD Record: MRN {data_dict.get('Patient MRN', 'NA')}"
        body = "\n".join([f"{k}: {v}" for k, v in data_dict.items()])
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, pwd)
            server.send_message(msg)
    except:
        pass

if check_password():
    st.title("📋 Cardiovascular Disease Data Abstraction")
    [span_1](start_span)st.info("Study Title: Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients[span_1](end_span)")
    
    # [span_2](start_span)Professional Disclaimer[span_2](end_span)
    [span_3](start_span)st.warning("Professional Disclaimer: Patient names must never be recorded. Use only Medical Record Numbers (MRN) and Study IDs to ensure anonymity[span_3](end_span).")

    # --- CONNECTION ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.stop()

    with st.form("cvd_form", clear_on_submit=True):
        # [span_4](start_span)Section 1: Administrative[span_4](end_span)
        st.subheader("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("Study ID")
            facility = st.selectbox("Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("Patient MRN")
        with col2:
            cohort = st.radio("Cohort Group", ["1=Exposed (Hypertensive)", "2=Unexposed (Normotensive)"])
            enroll_date = st.text_input("Date of Enrollment (E.C.)")
            fup_end = st.text_input("Follow-up End Date (E.C.)")

        # [span_5](start_span)Section 4: Lifestyle[span_5](end_span)
        st.subheader("Section 4: Lifestyle & Behavioral Factors")
        c3, c4 = st.columns(2)
        with c3:
            tobacco = st.selectbox("Tobacco Use", ["1=Never Smoker", "2=Current Smoker", "3=Previous Smoker"])
            alcohol = st.selectbox("Alcohol Consumption", ["1=Non-user", "2=Current User"])
            # Dynamic Logic: Hide quantity if Non-user
            drink_qty = "NA"
            if alcohol == "2=Current User":
                drink_qty = st.number_input("Average drinks/day", min_value=0.0)
        with c4:
            activity = st.selectbox("Physical Activity", ["1=Physically Active (≥30 min/day)", "2=Inactive"])
            salt = st.selectbox("Salt Intake", ["1=High (Adds salt)", "2=Normal/Low"])

        # [span_6](start_span)Section 5: Clinical[span_6](end_span)
        st.subheader("Section 5: Clinical & Physiological Measurements")
        c5, c6 = st.columns(2)
        with c5:
            weight = st.number_input("Weight (kg)", min_value=1.0)
            height = st.number_input("Height (cm)", min_value=1.0)
            # [span_7](start_span)Automated BMI Calculation[span_7](end_span)
            bmi_val = round(weight / ((height/100)**2), 2) if height > 0 else 0
            if bmi_val < 18.5: bmi_cat = "1=Underweight"
            elif 18.5 <= bmi_val < 25: bmi_cat = "2=Normal"
            elif 25 <= bmi_val < 30: bmi_cat = "3=Overweight"
            else: bmi_cat = "4=Obese"
            [span_8](start_span)st.info(f"Automatically Calculated BMI: {bmi_val} kg/m² ({bmi_cat})[span_8](end_span)")
        with c6:
            sbp = st.number_input("Baseline SBP (mmHg)")
            dbp = st.number_input("Baseline DBP (mmHg)")
            htn_duration = st.text_input("Duration of HTN (months)", "NA")

        # [span_9](start_span)Section 8: Outcome[span_9](end_span)
        st.subheader("Section 8: Outcome & Survival Data")
        cvd_event = st.radio("CVD Event Occurred?", ["1=Yes", "2=No"])
        event_type = "NA"
        if cvd_event == "1=Yes":
            event_type = st.selectbox("Type of CVD Event", ["1=Stroke", "2=Myocardial Infarction", "3=Heart Failure"])

        if st.form_submit_button("Submit Data"):
            # [span_10](start_span)Handling Missing Data: write "NA" if not found[span_10](end_span)
            record = {
                "Study ID": study_id if study_id else "NA",
                "Patient MRN": mrn if mrn else "NA",
                "Facility": facility,
                "Cohort": cohort,
                "BMI": bmi_val,
                "BMI Category": bmi_cat,
                "CVD Event": cvd_event,
                "Event Type": event_type,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
                updated_df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_df)
                send_summary_email(record)
                [span_11](start_span)st.success("Thank you for your commitment to this vital research[span_11](end_span)!")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
[span_12](start_span)st.caption("You are the 'foundation and eyes' of this study; our quality depends on your precision[span_12](end_span).")
