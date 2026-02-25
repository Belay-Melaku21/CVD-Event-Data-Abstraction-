import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- APP CONFIGURATION ---
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

# --- EMAIL FUNCTION ---
def send_summary_email(data_dict):
    sender = st.secrets["email_sender"]
    pwd = st.secrets["email_password"]
    receiver = st.secrets["email_receiver"]
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"New CVD Data Submission: MRN {data_dict['Patient MRN']}"
    
    body = "A new data abstraction form has been submitted.\n\nSummary:\n"
    for key, value in data_dict.items():
        body += f"{key}: {value}\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"Email could not be sent: {e}")

# --- MAIN APP ---
if check_password():
    st.title("📋 Cardiovascular Disease Data Abstraction")
    st.info("Study Title: Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients.")

    # Privacy Disclaimer
    with st.expander("⚖️ Data Privacy & Confidentiality Agreement"):
        st.warning("""
        **Confidentiality:** Patient names must NEVER be recorded. Use only Medical Record Numbers (MRN) 
        and Study IDs to ensure anonymity. Data is stored securely for research purposes only. [cite: 5, 6]
        """)

    # Google Sheets Connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Form initialization
    with st.form("cvd_form", clear_on_submit=True):
        # Section 1: Administrative
        st.subheader("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("Study ID")
            facility = st.selectbox("Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("Patient MRN")
        with col2:
            cohort = st.radio("Cohort Group", ["1=Exposed (Hypertensive)", "2=Unexposed (Normotensive)"])
            enroll_date = st.date_label = st.text_input("Date of Enrollment (DD/MM/YYYY E.C.)")
            followup_end = st.text_input("Follow-up End Date (DD/MM/YYYY E.C.)")

        st.divider()

        # Section 3 & 4: Demographics & Lifestyle
        st.subheader("Socio-Demographic & Lifestyle")
        c3, c4 = st.columns(2)
        with c3:
            age = st.number_input("Age (Years)", min_value=0, max_value=120)
            sex = st.selectbox("Sex", ["1=Male", "2=Female"])
            alcohol = st.selectbox("Alcohol Consumption", ["1=Non-user", "2=Current User"])
            
            # Dynamic Logic for Alcohol
            drink_count = "N/A"
            if alcohol == "2=Current User":
                drink_count = st.number_input("Average drinks/day", min_value=0.0)

        with c4:
            residence = st.selectbox("Residence", ["1=Urban", "2=Rural"])
            tobacco = st.selectbox("Tobacco Use", ["1=Never Smoker", "2=Current Smoker", "3=Previous Smoker"])
            activity = st.selectbox("Physical Activity", ["1=Physically Active", "2=Inactive"])

        st.divider()

        # Section 5: Clinical & BMI Calculation
        st.subheader("Section 5: Clinical & Physiological")
        c5, c6 = st.columns(2)
        with c5:
            weight = st.number_input("Weight (kg)", min_value=1.0)
            height = st.number_input("Height (cm)", min_value=1.0)
            
            # Automated BMI Calculation
            bmi_val = round(weight / ((height/100)**2), 2) if height > 0 else 0
            st.write(f"**Calculated BMI:** {bmi_val}")
            
            # Automated BMI Category
            if bmi_val < 18.5: bmi_cat = "1=Underweight"
            elif 18.5 <= bmi_val < 25: bmi_cat = "2=Normal"
            elif 25 <= bmi_val < 30: bmi_cat = "3=Overweight"
            else: bmi_cat = "4=Obese"
            st.write(f"**Category:** {bmi_cat}")

        with c6:
            sbp = st.number_input("SBP (mmHg)")
            dbp = st.number_input("DBP (mmHg)")
            htn_duration = st.number_input("Duration of HTN (months)")

        st.divider()

        # Section 8: Outcome
        st.subheader("Section 8: Outcome & Survival Data")
        cvd_event = st.radio("CVD Event Occurred?", ["1=Yes", "2=No"])
        
        event_type = "N/A"
        event_date = "N/A"
        if cvd_event == "1=Yes":
            event_type = st.selectbox("Type of CVD Event", ["1=Stroke", "2=Myocardial Infarction", "3=Heart Failure"])
            event_date = st.text_input("Date of CVD Event (DD/MM/YYYY)")

        # Submit Button
        submitted = st.form_submit_button("Submit Record")

        if submitted:
            # Prepare data row
            data = {
                "Study ID": study_id,
                "Facility": facility,
                "Patient MRN": mrn,
                "Cohort": cohort,
                "Enrollment Date": enroll_date,
                "Age": age,
                "Sex": sex,
                "Alcohol": alcohol,
                "Drinks/Day": drink_count,
                "BMI": bmi_val,
                "BMI Category": bmi_cat,
                "CVD Event": cvd_event,
                "Event Type": event_type,
                "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 1. Update Google Sheet
            try:
                existing_data = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_data, pd.DataFrame([data])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                # 2. Send Email
                send_summary_email(data)
                
                st.success("🎉 Thank you! Data submitted successfully and sheet updated.")
                st.balloons()
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Developed for Mehal Amhara Saynt District Health Centers Research.")
