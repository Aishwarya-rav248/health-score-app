import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------
# Load CSV datasets
patients_df = pd.read_csv('patients.csv')
observations_df = pd.read_csv('observations.csv')
conditions_df = pd.read_csv('conditions.csv')
allergies_df = pd.read_csv('allergies.csv')

# Clean column names
patients_df.columns = patients_df.columns.str.strip()
observations_df.columns = observations_df.columns.str.strip()
conditions_df.columns = conditions_df.columns.str.strip()
allergies_df.columns = allergies_df.columns.str.strip()

# ----------------------------
# Session State for Navigation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------
# Login Page
if not st.session_state.logged_in:
    st.title("Login")
    col1, col2 = st.columns(2)

    with col1:
        patient_id = st.text_input('Patient ID')
        last_name = st.text_input('Last Name')
        dob = st.date_input('DOB')

    with col2:
        first_name = st.text_input('First Name')
        gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])

    if st.button('Submit'):
        # Validate fields
        if patient_id.strip() != "" and first_name.strip() != "" and last_name.strip() != "":
            # Check if Patient ID exists
            if patient_id in patients_df['Id'].astype(str).values:
                st.session_state.logged_in = True
                st.session_state.patient_id = patient_id
                st.session_state.name = first_name + " " + last_name
                st.rerun()
            else:
                st.error("Invalid Patient ID. Please check your input.")
        else:
            st.warning("Please fill in all required fields!")

# Add here at top of dashboard page:
if 'patient_id' not in st.session_state:
    st.warning("Please login first.")
    st.rerun()

# Load datasets AFTER checking:
observations_df = pd.read_csv('observations.csv')
patient_id = st.session_state.patient_id
patient_observations = observations_df[observations_df['PATIENT'] == patient_id]


# ----------------------------
# Dashboard UI
st.title(f"Welcome {patient_name}")
st.subheader("Enter Health Metrics")

# Show patient exists or not
patient_obs = observations_df[observations_df['PATIENT'] == patient_id]
if patient_obs.empty:
    st.error("No observation data found for this Patient ID.")
    st.stop()

# ----------------------------
# Manual input fields
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input('Weight (kg)', min_value=30.0, max_value=200.0, step=1.0)
    height = st.number_input('Height (cm)', min_value=100.0, max_value=250.0, step=1.0)
    bmi_manual = st.number_input('BMI (optional)', min_value=10.0, max_value=50.0, step=0.1)
    smoking = st.selectbox('Smoking', ['No', 'Yes'])

with col2:
    bp = st.number_input('Blood Pressure (mm Hg)', min_value=80, max_value=200, step=1)
    heart_rate = st.number_input('Heart Rate (bpm)', min_value=40, max_value=180, step=1)

# ----------------------------
# Calculate BMI
if bmi_manual > 10:
    bmi = bmi_manual
elif height > 0:
    bmi = weight / ((height / 100) ** 2)
else:
    bmi = None

if bmi:
    st.write(f"**Calculated BMI:** {bmi:.2f}")

# ----------------------------
# Calculate Health Score Button
if st.button('Calculate Health Score'):
    if weight == 0 or height == 0 or bp == 0 or heart_rate == 0:
        st.warning("Please fill all fields correctly!")
    else:
        score = 100

        # Apply scoring logic
        if bmi:
            if bmi > 30 or bmi < 18:
                score -= 10
        if bp > 140:
            score -= 10
        if heart_rate > 100:
            score -= 5
        if smoking == 'Yes':
            score -= 5

        # ----------------------------
        # Show Health Score Gauge Chart
        st.subheader("Health Score")

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green" if score >= 80 else "orange" if score >= 50 else "red"},
                   'steps': [
                       {'range': [0, 49], 'color': "red"},
                       {'range': [50, 79], 'color': "orange"},
                       {'range': [80, 100], 'color': "green"}
                   ]},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        st.plotly_chart(gauge)

        if score >= 80:
            st.success("Excellent")
        elif score >= 50:
            st.warning("Needs Improvement")
        else:
            st.error("Unhealthy: Immediate Action Required!")

        # ----------------------------
        # Preventive Measures
        st.subheader("Preventive Measures")
        if bmi:
            st.write(f"1. BMI Optimization (BMI: {bmi:.2f}) – Focus on balanced diet & exercise.")
        if heart_rate > 80:
            st.write(f"2. Heart Rate Management ({heart_rate} bpm) – Include stress reduction techniques.")
        st.write("3. Regular Monitoring – Track BP, cholesterol, glucose levels.")

# ----------------------------
# Back to Login Button
if st.button('Back to Login'):
    st.session_state.logged_in = False
    st.rerun()
