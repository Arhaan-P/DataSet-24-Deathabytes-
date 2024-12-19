import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from model import predict

# Load environment variables from .env file
load_dotenv()

def configure_genai():
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key is None:
        raise ValueError("GOOGLE_API_KEY is not set in the .env file")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    return model

def create_database():
    conn = sqlite3.connect('system_reports.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  grid_voltage REAL,
                  grid_frequency REAL,
                  cooling_temp REAL,
                  cooling_humidity INTEGER,
                  file_integrity INTEGER,
                  error_count INTEGER,
                  cpu_usage INTEGER,
                  memory_usage INTEGER,
                  network_traffic REAL,
                  network_traffic_breach INTEGER,
                  firewall_alerts INTEGER,
                  status TEXT,
                  report_text TEXT)''')
    conn.commit()
    conn.close()

def generate_report_text(input_data, prediction):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""System Status Report - {timestamp}
    
Overall Status: {prediction}

Key Metrics:
- Grid Voltage: {input_data['Grid_Voltage']} V
- Grid Frequency: {input_data['Grid_Frequency']} Hz
- Cooling Temperature: {input_data['Cooling_Temperature']}°C
- CPU Usage: {input_data['CPU_Usage']}%
- Memory Usage: {input_data['Memory_Usage']}%

Alerts and Issues:
- Error Count: {input_data['Error_Count']}
- Firewall Alerts: {input_data['Firewall_Alerts']}
- Network Traffic Breach: {'Yes' if input_data['Network_Traffic_Breach'] == 1 else 'No'}

System Health Indicators:
- File Integrity: {'Pass' if input_data['File_Integrity'] == 1 else 'Fail'}
- Network Traffic: {input_data['Network_Traffic']} Mbps
"""
    return report

def save_report_to_db(input_data, prediction, report_text):
    conn = sqlite3.connect('system_reports.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO reports 
                 (timestamp, grid_voltage, grid_frequency, cooling_temp, 
                  cooling_humidity, file_integrity, error_count, cpu_usage,
                  memory_usage, network_traffic, network_traffic_breach,
                  firewall_alerts, status, report_text)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               input_data['Grid_Voltage'],
               input_data['Grid_Frequency'],
               input_data['Cooling_Temperature'],
               input_data['Cooling_Humidity'],
               input_data['File_Integrity'],
               input_data['Error_Count'],
               input_data['CPU_Usage'],
               input_data['Memory_Usage'],
               input_data['Network_Traffic'],
               input_data['Network_Traffic_Breach'],
               input_data['Firewall_Alerts'],
               prediction,
               report_text))
    
    conn.commit()
    conn.close()

def get_saved_reports():
    conn = sqlite3.connect('system_reports.db')
    reports = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return reports

def delete_report(report_id):
    conn = sqlite3.connect('system_reports.db')
    c = conn.cursor()
    c.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()

def show_prediction_tab():
    st.title("System Status Prediction")
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.header("Input Parameters")
        
        grid_voltage = st.number_input("Grid Voltage", min_value=0.0, max_value=500.0, value=220.0)
        grid_frequency = st.number_input("Grid Frequency (Hz)", min_value=0.0, max_value=100.0, value=50.0)
        cooling_temp = st.number_input("Cooling Temperature (°C)", min_value=0.0, max_value=100.0, value=25.0)
        cooling_humidity = st.slider("Cooling Humidity (%)", min_value=0, max_value=100, value=50)
        file_integrity = st.selectbox("File Integrity", options=[0, 1], format_func=lambda x: "Pass" if x == 1 else "Fail")
        error_count = st.number_input("Error Count", min_value=0, max_value=1000, value=0, step=1)
        cpu_usage = st.slider("CPU Usage (%)", min_value=0, max_value=100, value=50)
        memory_usage = st.slider("Memory Usage (%)", min_value=0, max_value=100, value=50)
        network_traffic = st.number_input("Network Traffic (Mbps)", min_value=0.0, max_value=10000.0, value=100.0)
        network_traffic_breach = st.selectbox("Network Traffic Breach", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        firewall_alerts = st.number_input("Firewall Alerts", min_value=0, max_value=1000, value=0, step=1)

    with right_col:
        st.header("Prediction Results")
        
        predict_button = st.button("Predict Status")
        if predict_button:
            input_data = {
                'Grid_Voltage': grid_voltage,
                'Grid_Frequency': grid_frequency,
                'Cooling_Temperature': cooling_temp,
                'Cooling_Humidity': cooling_humidity,
                'File_Integrity': file_integrity,
                'Error_Count': error_count,
                'CPU_Usage': cpu_usage,
                'Memory_Usage': memory_usage,
                'Network_Traffic': network_traffic,
                'Network_Traffic_Breach': network_traffic_breach,
                'Firewall_Alerts': firewall_alerts
            }
            
            result = predict(
                input_data['Grid_Voltage'],
                input_data['Grid_Frequency'],
                input_data['Cooling_Temperature'],
                input_data['Cooling_Humidity'],
                input_data['Error_Count'],
                input_data['CPU_Usage'],
                input_data['Memory_Usage'],
                input_data['Network_Traffic'],
                input_data['Network_Traffic_Breach'],
                input_data['Firewall_Alerts']
            )
            
            st.session_state.current_input_data = input_data
            
            prediction = "Normal" if all([ 
                cpu_usage < 80,
                memory_usage < 80,
                error_count < 10,
                network_traffic_breach == 0,
                firewall_alerts < 5
            ]) else "Abnormal"
            
            st.session_state.current_prediction = prediction
            
            st.markdown("### System Status: ")
            if prediction == "Normal":
                st.success("NORMAL")
            else:
                st.error("ABNORMAL")
            
            st.markdown("### Input Summary:")
            st.dataframe(pd.DataFrame([input_data]))
            
            generate_report = st.button("Generate Report")
            if generate_report:
                st.session_state.current_tab = "Report Generator"
                st.rerun()  # Using st.rerun() instead of experimental_rerun

def show_report_generator_tab():
    st.title("Report Generator")
    if st.session_state.current_input_data and st.session_state.current_prediction:
        report_text = generate_report_text(st.session_state.current_input_data, 
                                        st.session_state.current_prediction)
        
        edited_report = st.text_area("Edit Report", report_text, height=400)
        
        if st.button("Save Report"):
            save_report_to_db(st.session_state.current_input_data,
                            st.session_state.current_prediction,
                            edited_report)
            st.success("Report saved successfully!")
    else:
        st.warning("Please generate a prediction first!")

def show_reports_tab():
    st.title("Saved Reports")
    reports = get_saved_reports()
    
    # Add search and filter options
    search_term = st.text_input("Search reports by content:")
    status_filter = st.multiselect("Filter by status:", ["Normal", "Abnormal"])
    
    filtered_reports = reports
    if search_term:
        filtered_reports = filtered_reports[
            filtered_reports['report_text'].str.contains(search_term, case=False)]
    if status_filter:
        filtered_reports = filtered_reports[filtered_reports['status'].isin(status_filter)]
    
    # Display reports in an expandable format
    for _, report in filtered_reports.iterrows():
        with st.expander(f"Report from {report['timestamp']} - Status: {report['status']}"):
            st.text(report['report_text'])
            if st.button("Delete Report", key=f"delete_{report['id']}"):
                delete_report(report['id'])
                st.rerun()  # Using st.rerun() instead of experimental_rerun

def show_qa_tab(model):
    st.title("Q&A System")
    
    user_question = st.text_input("Ask a question about the system status:")
    
    if user_question:
        if st.session_state.current_input_data and st.session_state.current_prediction:
            system_context = f"""
            You are a helpful system monitoring assistant. Here is the current system information:
            
            System Status: {st.session_state.current_prediction}
            Grid Voltage: {st.session_state.current_input_data['Grid_Voltage']} V
            Grid Frequency: {st.session_state.current_input_data['Grid_Frequency']} Hz
            Cooling Temperature: {st.session_state.current_input_data['Cooling_Temperature']}°C
            Cooling Humidity: {st.session_state.current_input_data['Cooling_Humidity']}%
            File Integrity: {'Pass' if st.session_state.current_input_data['File_Integrity'] == 1 else 'Fail'}
            Error Count: {st.session_state.current_input_data['Error_Count']}
            CPU Usage: {st.session_state.current_input_data['CPU_Usage']}%
            Memory Usage: {st.session_state.current_input_data['Memory_Usage']}%
            Network Traffic: {st.session_state.current_input_data['Network_Traffic']} Mbps
            Network Traffic Breach: {'Yes' if st.session_state.current_input_data['Network_Traffic_Breach'] == 1 else 'No'}
            Firewall Alerts: {st.session_state.current_input_data['Firewall_Alerts']}

            The system is considered abnormal if any of these conditions are met:
            - CPU Usage >= 80%
            - Memory Usage >= 80%
            - Error Count >= 10
            - Network Traffic Breach detected
            - Firewall Alerts >= 5

            Please provide a natural, conversational response to this question: {user_question}
            """
            
            try:
                response = model.generate_content(system_context)
                cleaned_response = response.text.replace('*', '').strip()
                st.markdown("### Answer:")
                st.write(cleaned_response)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
        else:
            st.warning("Please generate a prediction first!")

def main():
    st.set_page_config(page_title="System Status Predictor", layout="wide")
    
    # Initialize session state
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Prediction"
    if 'current_input_data' not in st.session_state:
        st.session_state.current_input_data = None
    if 'current_prediction' not in st.session_state:
        st.session_state.current_prediction = None
    
    # Initialize database and model
    create_database()
    model = configure_genai()
    
    # Tab selection
    tab_options = ["Prediction", "Report Generator", "Q&A", "View Reports"]
    st.session_state.current_tab = st.radio("Navigation", tab_options, horizontal=True)
    
    # Show appropriate tab
    if st.session_state.current_tab == "Prediction":
        show_prediction_tab()
    elif st.session_state.current_tab == "Report Generator":
        show_report_generator_tab()
    elif st.session_state.current_tab == "Q&A":
        show_qa_tab(model)
    elif st.session_state.current_tab == "View Reports":
        show_reports_tab()

if __name__ == "__main__":
    main()