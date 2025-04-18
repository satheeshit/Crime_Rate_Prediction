#  Crime Rate Prediction & Forecasting App

This is a full-stack Flask web application that predicts and forecasts crime rates in Indian states using Machine Learning and Time Series analysis. Users can log in, enter crime-related inputs, view predictions, and receive personalized email reports. The system is designed with a modern dark-themed UI and real-time analysis features.

---

##  Features

-  **Crime Prediction** using Random Forest Regression
-  **Time Series Forecasting** up to 2030 using Facebook Prophet
-  **User Authentication** (Login/Register) with MySQL
-  **Gmail Alerts** with prediction and forecast results
- **Interactive UI** with stylish input forms and structured result tables
-  **Futuristic Background Image** and responsive design

---

##  Technologies Used

- **Python**, **Flask**, **pandas**, **scikit-learn**
- **Facebook Prophet** for time series modeling
- **MySQL** for user login system
- **Flask-Mail** for sending emails
- **HTML/CSS** (Jinja templates) for frontend
- **Matplotlib** for forecast plotting

---

##  Project Overview

1. **Prediction Model**: Uses features like state, year, and specific crime types to predict total IPC crimes.
2. **Forecasting Model**: Time series forecasting is implemented per state using Prophet to predict trends up to the year 2030.
3. **Authentication**: Users must register/login to access features.
4. **Email Integration**: Automatically sends results to the user’s Gmail account.
5. **Frontend**: Clean, responsive dark UI with input forms and forecast visualizations.

---
##  Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/crime-rate-prediction-app.git
   cd crime-rate-prediction-app
Create virtual environment and install dependencies
pip install -r requirements.txt

Set up MySQL database

Create a database: crime_prediction

Create a users table:
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    password_hash TEXT
);

Configure Gmail

Enable 2FA on your Gmail

Generate an App Password: https://myaccount.google.com/apppasswords

Replace your MAIL_USERNAME and MAIL_PASSWORD in crp.py

Run the app
python crp.py

Author
Satheesh .R – Aspiring Data Scientist
 rsatheeshit@gmail.com
https://github.com/satheeshit
https://www.linkedin.com/in/satheesh-r-0b3850246

🔗 




