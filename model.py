import joblib
from sklearn.preprocessing import StandardScaler


def predict(Grid_Voltage, Grid_Frequency, Cooling_Temperature, Cooling_Humidity,
            Error_Count, CPU_Usage, Memory_Usage, Network_Traffic,
            Network_Traffic_Breach, Firewall_Alerts):
    # Load the trained model and scaler
    model = joblib.load('noc.joblib')
    scaler = StandardScaler()

    # Create a dictionary from the input arguments
    input_data = {
        'Grid_Voltage': Grid_Voltage,
        'Grid_Frequency': Grid_Frequency,
        'Cooling_Temperature': Cooling_Temperature,
        'Cooling_Humidity': Cooling_Humidity,
        'Error_Count': Error_Count,
        'CPU_Usage': CPU_Usage,
        'Memory_Usage': Memory_Usage,
        'Network_Traffic': Network_Traffic,
        'Network_Traffic_Breach': Network_Traffic_Breach,  # 1 for breach, 0 for no breach
        'Firewall_Alerts': Firewall_Alerts,
    }

    # Convert the input data into a list that matches the order of your features
    input = [
        input_data['Grid_Voltage'],
        input_data['Grid_Frequency'],
        input_data['Cooling_Temperature'],
        input_data['Cooling_Humidity'],
        input_data['Error_Count'],
        input_data['CPU_Usage'],
        input_data['Memory_Usage'],
        input_data['Network_Traffic'],
        input_data['Network_Traffic_Breach'],
        input_data['Firewall_Alerts'],
    ]

    # Reshape input for scaling (it should be a 2D array)
    input_reshaped = [input]  # Make it a list of lists

    # Scale the input data
    scaled_input = scaler.fit_transform(input_reshaped)

    # Make a prediction
    prediction = model.predict(scaled_input)

    # Output the prediction
    return prediction[0]  # Will return 'Normal' or 'Abnormal'