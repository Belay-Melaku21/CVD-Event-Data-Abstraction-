import streamlit as st
import pandas as pd
from datetime import datetime
# Change the import to this:
from streamlit_gsheets import GSheetsConnection

# ... (Authentication code remains the same) ...

if check_password():
    # ... (Intro text remains the same) ...

    # Update this connection logic:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # To read existing data (if needed for Excel headers):
    # existing_data = conn.read(worksheet="Sheet1")

    with st.form("cvd_form", clear_on_submit=True):
        # ... (Form fields remain the same) ...

        if submit:
            # Prepare the new row
            new_row = {
                "Health Center Name": hc_name, 
                "Patient MRN": mrn, 
                "Date of Extraction": str(extract_date),
                # ... add all other fields here ...
            }
            
            # Use the official update method
            try:
                conn.create(data=new_row)
                st.success("Data successfully submitted! The form has been reset.")
            except Exception as e:
                st.error(f"Error: {e}")
