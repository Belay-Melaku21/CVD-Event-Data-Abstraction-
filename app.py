import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- ደህንነት እና መግቢያ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 CVD Research Portal Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pw == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        return False
    return True

# --- የኢሜል ማሳወቂያ ---
def send_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = "melakubelay93@gmail.com"
        msg['Subject'] = f"New Study Record: {details.get('1.1 Study ID')}"
        body = "\n".join([f"{k}: {v}" for k, v in details.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")

if check_password():
    st.title("Time to CVD Event & Determinants Study")
    st.info("Data Abstraction Checklist for Health Centers in Mehal Amhara Saynt District")

    # የGoogle Sheets ግንኙነት (PEM ስህተትን ለመከላከል የተጨመረ ማጽጃ)
    try:
        # በሴክሬትስ ውስጥ ያሉትን የ \n ምልክቶች ማስተካከል
        conn_params = st.secrets["connections"]["gsheets"].to_dict()
        if "private_key" in conn_params:
            conn_params["private_key"] = conn_params["private_key"].replace("\\n", "\n")
        
        conn = st.connection("gsheets", type=GSheetsConnection, **conn_params)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

    with st.form("research_form", clear_on_submit=True):
        # Section 1: Administrative
        st.header("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("1.3 Patient MRN")
        with col2:
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed (Hypertensive)", "2= Unexposed (Normotensive)"])
            enroll_date = st.text_input("1.5 Date of Enrollment (DD/MM/YYYY E.C.)")
            followup_end = st.text_input("1.6 Follow-up End Date (DD/MM/YYYY E.C.)")

        # Section 2: Eligibility Checklist
        st.header("Section 2: Eligibility Checklist")
        age_elig = st.radio("2.1 Age ≥18 years?", ["1 = Yes", "2 = No"])
        pre_cvd = st.radio("2.2 Pre-existing CVD before enrolment?", ["1 = Yes", "2 = No"])
        preg_htn = st.radio("2.3 Pregnancy-induced Hypertension?", ["1 = Yes", "2 = No"])

        # Section 3: Socio-Demographic
        st.header("Section 3: Socio-Demographic Characteristics")
        age = st.number_input("3.3 Age (years)", min_value=18, max_value=120)
        sex = st.radio("3.4 Sex", ["1 = Male", "2 = Female"])
        residence = st.radio("3.5 Residence", ["1 = Urban", "2 = Rural"])
        edu = st.selectbox("3.6 Educational Status", ["1 = No formal", "2 = Primary", "3 = Secondary", "4 = Higher"])
        occ = st.selectbox("3.7 Occupational Status", ["1 = Gov Employee", "2 = Merchant", "3 = Farmer", "4 = Unemployed", "5 = Other"])
        marital = st.selectbox("3.8 Marital Status", ["1 = Single", "2 = Married", "3 = Widowed", "4 = Divorced/Separated"])

        # Section 4: Lifestyle
        st.header("Section 4: Lifestyle & Behavioral Factors")
        tobacco = st.selectbox("4.1 Tobacco Use", ["1 = Never", "2 = Current", "3 = Previous"])
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["1 = Non-user", "2 = Current User"])
        alc_freq = "NA"
        if alcohol == "2 = Current User":
            alc_freq = st.text_input("4.2 Average drinks/day")
        
        khat = st.selectbox("4.3 Khat Chewing", ["1 = Never", "2 = Current", "3 = History"])
        activity = st.radio("4.4 Physical Activity (≥30 min/day)", ["1 = Physically Active", "2 = Inactive"])
        salt = st.radio("4.5 Salt Intake", ["1 = High", "2 = Normal/Low"])

        # Section 5: Clinical (BMI calculation)
        st.header("Section 5: Clinical & Physiological Measurements")
        col3, col4 = st.columns(2)
        with col3:
            sbp = st.number_input("5.1 Baseline SBP (mmHg)", min_value=50)
            dbp = st.number_input("5.1 Baseline DBP (mmHg)", min_value=30)
            htn_stage = st.selectbox("5.2 HTN Stage", ["1 = Pre-HTN", "2 = Stage 1", "3 = Stage 2", "4 = Stage 3/4"])
        with col4:
            weight = st.number_input("5.3 Weight (kg)", min_value=20.0)
            height = st.number_input("5.3 Height (cm)", min_value=50.0)
            
            # BMI Calculation
            bmi = round(weight / ((height/100)**2), 2)
            bmi_cat = "Normal"
            if bmi < 18.5: bmi_cat = "1 = Underweight"
            elif 18.5 <= bmi < 25: bmi_cat = "2 = Normal"
            elif 25 <= bmi < 30: bmi_cat = "3 = Overweight"
            else: bmi_cat = "4 = Obese"
            st.write(f"**BMI:** {bmi} ({bmi_cat})")

        htn_duration = st.text_input("5.5 Duration of HTN (months)")
        fam_history = st.radio("5.6 Family History of CVD/HTN", ["1 = Yes", "2 = No"])

        # Section 6: Biochemical
        st.header("Section 6: Biochemical & Comorbidity Profile")
        dm = st.radio("6.1 Diabetes Mellitus", ["1 = Yes", "2 = No"])
        ckd = st.radio("6.2 Chronic Kidney Disease", ["1 = Yes", "2 = No"])
        proteinuria = st.radio("6.3 Proteinuria", ["1 = Positive", "2 = Negative"])
        cholesterol = st.text_input("6.4 Total Cholesterol (mg/dL) - write NA if missing")
        complications = st.selectbox("6.5 Baseline Complications", ["1 = None", "2 = Prior Stroke", "3 = Prior Cardiac"])

        # Section 7: Treatment
        st.header("Section 7: Treatment & Management Factors")
        tx_type = st.selectbox("7.1 Med Type", ["1 = Monotherapy", "2 = Dual Therapy", "3 = Polytherapy"])
        tx_class = st.selectbox("7.2 Class", ["1 = ACEi/ARB", "2 = CCB", "3 = Diuretics", "4 = Beta-Blockers"])
        adherence = st.radio("7.3 Medication Adherence", ["1 = Good", "2 = Poor"])

        # Section 8: Outcome
        st.header("Section 8: Outcome & Survival Data")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["1 = Yes", "2 = No"])
        event_type = "NA"
        event_date = "NA"
        if cvd_event == "1 = Yes":
            event_type = st.selectbox("8.2 Type of Event", ["1 = Stroke", "2 = MI", "3 = Heart Failure"])
            event_date = st.text_input("8.3 Date of Event (DD/MM/YYYY)")

        censoring = st.selectbox("8.4 Censoring Details", ["1 = Lost to Follow-up", "2 = Died (Non-CVD)", "3 = Study ended without event"])
        last_visit = st.text_input("8.5 Date of Last Follow-up/Censoring")

        # Submit Button
        if st.form_submit_button("Submit Record"):
            data = {
                "1.1 Study ID": study_id, "1.3 MRN": mrn, "1.2 Facility": facility,
                "BMI": bmi, "BMI Cat": bmi_cat, "Alcohol Freq": alc_freq,
                "8.1 CVD Event": cvd_event, "8.2 Event Type": event_type,
                "8.3 Event Date": event_date, "8.5 Last Date": last_visit,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # ወደ Google Sheet መመዝገብ
                df = pd.DataFrame([data])
                conn.create(data=df)
                
                # ኢሜል ማሳወቂያ
                send_email(data)
                st.success("Record saved successfully! 🚀")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving data: {e}")
