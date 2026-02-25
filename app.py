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
                st.rerun()
            else:
                st.error("Invalid credentials.")
        return False
    return True

def send_summary_email(data_dict):
    try:
        sender = st.secrets["email_sender"]
        pwd = st.secrets["email_password"]
        receiver = st.secrets["email_receiver"]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"CVD Submission: MRN {data_dict['Patient MRN']}"
        body = "\n".join([f"{k}: {v}" for k, v in data_dict.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
    except:
        pass

if check_password():
    st.title("📋 Cardiovascular Disease Data Abstraction")
    st.info("Study: Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients [cite: 2]")
    
    st.warning("Professional Disclaimer: Patient names must never be recorded. Use only Medical Record Numbers (MRN) and Study IDs[cite: 5, 6].")

    # --- CONNECTION BLOCK ---
    try:
        # We use the built-in connection which will pull from [connections.gsheets]
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.stop()

    with st.form("cvd_form", clear_on_submit=True):
        st.subheader("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("Study ID")
            facility = st.selectbox("Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("Patient MRN ")
        with col2:
            cohort = st.radio("Cohort Group", ["1=Exposed (Hypertensive)", "2=Unexposed (Normotensive)"])
            enroll_date = st.text_input("Enrollment Date (DD/MM/YYYY E.C.) [cite: 22]")
            fup_date = st.text_input("Follow-up End Date (DD/MM/YYYY E.C.) [cite: 23]")

        st.divider()
        st.subheader("Socio-Demographics & Lifestyle")
        c3, c4 = st.columns(2)
        with c3:
            age = st.number_input("Age (Years) [cite: 29]", min_value=18)
            sex = st.selectbox("Sex", ["1=Male", "2=Female"])
            alcohol = st.selectbox("Alcohol Consumption", ["1=Non-user", "2=Current User"])
            drink_count = "NA"
            if alcohol == "2=Current User":
                drink_count = st.number_input("Average drinks/day [cite: 37]", min_value=0.0)
        with c4:
            residence = st.selectbox("Residence", ["1=Urban", "2=Rural"])
            tobacco = st.selectbox("Tobacco Use", ["1=Never", "2=Current", "3=Previous"])
            activity = st.selectbox("Physical Activity", ["1=Active", "2=Inactive"])

        st.divider()
        st.subheader("Clinical & BMI")
        c5, c6 = st.columns(2)
        with c5:
            weight = st.number_input("Weight (kg)", min_value=1.0)
            height = st.number_input("Height (cm)", min_value=1.0)
            bmi_val = round(weight / ((height/100)**2), 2) if height > 0 else 0
            bmi_cat = "NA"
            if bmi_val > 0:
                if bmi_val < 18.5: bmi_cat = "1=Underweight"
                elif bmi_val < 25: bmi_cat = "2=Normal"
                elif bmi_val < 30: bmi_cat = "3=Overweight"
                else: bmi_cat = "4=Obese"
            st.info(f"BMI: {bmi_val} ({bmi_cat}) [cite: 44, 45]")
        with c6:
            sbp = st.number_input("SBP (mmHg)")
            dbp = st.number_input("DBP (mmHg)")
            htn_dur = st.text_input("HTN Duration (months)", "NA")

        st.divider()
        st.subheader("Outcome Data")
        cvd_event = st.radio("CVD Event Occurred? [cite: 59]", ["1=Yes", "2=No"])
        event_type = "NA"
        if cvd_event == "1=Yes":
            event_type = st.selectbox("Event Type", ["1=Stroke", "2=MI", "3=Heart Failure"])

        submitted = st.form_submit_button("Submit Data")

        if submitted:
            data = {
                "Study ID": study_id, "Facility": facility, "MRN": mrn, "Cohort": cohort,
                "Age": age, "BMI": bmi_val, "BMI Category": bmi_cat, "CVD Event": cvd_event,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                # Use current sheet URL from secrets
                df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
                updated_df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_df)
                send_summary_email(data)
                st.success("✅ Thank You! Data submitted and Sheet updated.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Data abstraction checklist version 1.0 [cite: 1]")
