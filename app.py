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
            if patient_id in patients_df['PATIENT'].astype(str).values:
                st.session_state.logged_in = True
                st.session_state.patient_id = patient_id
                st.session_state.name = first_name + " " + last_name
                st.rerun()
            else:
                st.error("Invalid Patient ID. Please check your input.")
        else:
            st.warning("Please fill in all required fields!")

# ----------------------------
# Dashboard Page
else:
    st.title(f"Welcome {st.session_state.name}")
    st.subheader("Enter Health Metrics")

    patient_id = st.session_state.patient_id
    obs = observations_df[observations_df['PATIENT'] == patient_id]

    # Default values (can customize based on available data)
    weight = 70
    height = 170
    bp = 120
    heart_rate = 80
    smoking = 'No'

    # Health Metrics Inputs
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input('Weight (kg)', 30, 200, int(weight))
        height = st.number_input('Height (cm)', 100, 250, int(height))
        bmi_manual = st.number_input('BMI (optional)', 10.0, 50.0, step=0.1)
        smoking = st.selectbox('Smoking', ['No', 'Yes'], index=0 if smoking == 'No' else 1)

    with col2:
        bp = st.number_input('Blood Pressure (mm Hg)', 80, 200, int(bp))
        heart_rate = st.number_input('Heart Rate (bpm)', 40, 180, int(heart_rate))

    # ----------------------------
    # Calculate BMI
    if bmi_manual > 10:
        bmi = bmi_manual
    elif height > 0:
        bmi = weight / ((height / 100) ** 2)
    else:
        bmi = None

    st.write(f"**Calculated BMI:** {bmi:.2f}")

    # ----------------------------
    # Health Score Calculation
    score = 100

    if bmi:
        if bmi > 30 or bmi < 18:
            score -= 10

    if bp > 140:
        score -= 10

    if heart_rate > 100:
        score -= 5

    # Chronic conditions
    patient_conditions = conditions_df[conditions_df['PATIENT'] == patient_id]
    if len(patient_conditions) > 2:
        score -= 10

    # Allergy severity check
    patient_allergies = allergies_df[allergies_df['PATIENT'] == patient_id]
    if 'severity' in patient_allergies.columns:
        if 'Severe' in patient_allergies['severity'].values:
            score -= 5

    if smoking == 'Yes':
        score -= 5

    # ----------------------------
    # Health Score Gauge Visualization
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
    # Back Button to Login
    if st.button('Back to Login'):
        st.session_state.logged_in = False
        st.rerun()
