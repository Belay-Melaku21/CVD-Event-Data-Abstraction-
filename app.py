import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# የገጽ መዋቅር
st.set_page_config(page_title="CVD Data Entry", layout="centered")

# --- LOGIN SECTION ---
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.subheader("የመግቢያ ገጽ (Login)")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pwd == "@Belay6669":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("የተሳሳተ የተጠቃሚ ስም ወይም የይለፍ ቃል!")
        return False
    return True

# --- EMAIL SENDING FUNCTION ---
def send_email(data_summary):
    sender_email = "melakubelay93@gmail.com"
    receiver_email = "melakubelay93@gmail.com"
    password = "your_app_password_here" # ከGoogle App Passwords የሚገኝ

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New CVD Data Entry Notification"
    
    body = f"አዲስ መረጃ ተመዝግቧል:\n\n{data_summary}"
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Email error: {e}")

# --- MAIN APP ---
if check_password():
    st.success(f"እንኳን ደህና መጣህ በላይ መላኩ!")
    st.title("CVD Data Abstraction Form")
    
    # ከGoogle Sheet ጋር ግንኙነት
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_form"):
        st.header("SECTION 1: IDENTIFICATION")
        h_center = st.text_input("Health Center Name")
        mrn = st.text_input("Patient MRN")
        date_ext = st.date_input("Date of Extraction")
        
        st.header("SECTION 2: DEMOGRAPHICS")
        age = st.number_input("Age", min_value=1, max_value=120)
        sex = st.selectbox("Sex", ["Male", "Female"])
        
        st.header("SECTION 7: OUTCOME")
        cvd_event = st.radio("CVD Event Occurred?", ["Yes", "No"])
        
        submit = st.form_submit_button("Save & Send Data")

        if submit:
            # መረጃውን ማደራጀት
            new_row = {
                "Full_Name": "Belay Melaku (Collector)",
                "MRN": mrn,
                "Age": age,
                "Sex": sex,
                "CVD_Status": cvd_event,
                "Submission_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # ወደ Google Sheet መላክ
            try:
                df = conn.read()
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=updated_df)
                
                # ኢሜል መላክ
                summary = f"MRN: {mrn}\nAge: {age}\nCVD Event: {cvd_event}"
                send_email(summary)
                
                st.success("መረጃው በስኬት ተቀምጧል! ወደ ኢሜልዎም ተልኳል።")
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል: {e}")

    if st.button("Log Out"):
        st.session_state["logged_in"] = False
        st.rerun()
