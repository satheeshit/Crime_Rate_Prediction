from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
import joblib
import matplotlib.pyplot as plt
import os

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- MySQL Configuration ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Satheesh14@sa'
app.config['MYSQL_DB'] = 'crime_prediction'
mysql = MySQL(app)

# --- Flask-Mail Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rsatheeshit@gmail.com'
app.config['MAIL_PASSWORD'] = 'jjzpdhcqzuioegji'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'
mail = Mail(app)

# --- Load Models & Data ---
ml_model = joblib.load("D:\crime_model_calibrated.pkl")
all_features = joblib.load("D:\model_features_calibrated.pkl")
forecast_models = joblib.load("D:\prophet_model_all_states.pkl")

data = pd.read_csv(r"D:\crime rate prediction\newtrial - Sheet 1 - 01_District_wise_crim 2.csv")
data.dropna(inplace=True)
data['YEAR'] = pd.to_datetime(data['YEAR'], format='%Y')
states = sorted(data['STATE/UT'].unique())
years = sorted(data['YEAR'].dt.year.unique())

# --- Routes ---
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html', states=states, years=years, features=all_features)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            cur.close()
            return "Email already registered!"

        cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed_pw))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):  # password_hash is in index 2
            session['user'] = email
            return redirect(url_for('home'))

        return "Invalid email or password!"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    state = request.form['state']
    year = int(request.form['year'])
    selected_feature = request.form['feature']
    value = int(request.form['value'])

    # ✅ Create input data with correct structure
    input_data = pd.DataFrame(columns=all_features)
    input_data.loc[0] = 0  # initialize all features to 0
    input_data.at[0, 'YEAR'] = year
    input_data.at[0, selected_feature] = value

    # ✅ Ensure feature order exactly matches model input
    input_data = input_data[ml_model.feature_names_in_]

    # ✅ Predict
    prediction = ml_model.predict(input_data)[0]

    # ✅ Interpret prediction
    if prediction < 200:
        label = "Low rate crime area"
    elif prediction < 500:
        label = "Moderate crime rate"
    else:
        label = "High crime rate area"

    # ✅ Send result via email
    msg = Message(f"Crime Prediction Result - {state}", recipients=[email])
    msg.body = f"""State: {state}
Year: {year}
Crime Feature: {selected_feature}
Entered Value: {value}
Predicted IPC Crimes: {int(prediction)}
Crime Level: {label}"""
    mail.send(msg)

    return render_template('result.html',
                           prediction=int(prediction),
                           label=label,
                           state=state,
                           year=year,
                           crime=selected_feature,
                           value=value)


@app.route('/forecast', methods=['POST'])
def forecast():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    state = request.form['forecast_state']
    model = forecast_models[state]

    df_state = data[data['STATE/UT'] == state]
    df_grouped = df_state.groupby('YEAR')['TOTAL IPC CRIMES'].sum().reset_index()
    df_grouped.rename(columns={'YEAR': 'ds', 'TOTAL IPC CRIMES': 'y'}, inplace=True)

    last_year = df_grouped['ds'].dt.year.max()
    years_to_forecast = 2030 - last_year
    future = model.make_future_dataframe(periods=years_to_forecast, freq='Y')
    forecast_df = model.predict(future)

    forecast_value = int(forecast_df['yhat'].max())
    next_year = forecast_df['ds'].dt.year.max()
    trend = "Increasing" if forecast_value > df_grouped['y'].max() else "Decreasing"

    msg = Message(f"Crime Forecast Result - {state}", recipients=[email])
    msg.body = f"""State: {state}
Forecast Year: {next_year}
Predicted Max Crimes: {forecast_value}
Trend: {trend}"""
    mail.send(msg)

    fig = model.plot(forecast_df)
    plt.title(f"Crime Forecast for {state}", fontsize=16, color="#00bfff")
    plt.xlabel("Year")
    plt.ylabel("Predicted Crimes")
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plot_path = os.path.join("static", "forecast_plot.png")
    plt.savefig(plot_path)
    plt.close()

    return render_template("forecast_result.html", state=state, plot_url=plot_path,
                           forecast_value=forecast_value, next_year=next_year,
                           trend_description=trend)

if __name__ == '__main__':
    app.run(debug=True)
