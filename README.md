# StockVisionIQ

StockVisionIQ is a comprehensive stock analysis platform that allows users to access detailed financial insights, real-time news with sentiment analysis, analyst insights, stock comparisons, trading views, and future stock predictions, all in one place.

## Table of Contents

- [Project Overview](#project-overview)
- [Screenshots](#screenshots)
- [Setup](#setup)
- [Usage](#usage)
- [Features](#features)

## Project Overview

StockVisionIQ is built on Django for user registration, login, and authentication, and it connects to a Streamlit dashboard for the main analysis functionalities. The project provides users with a seamless way to analyze and understand stock trends and predictions through interactive charts and financial analysis.

## Screenshots

### Home Page
![Home](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_183534_127.0.0.1.jpeg)

### About Us Page
![About Us](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_183624_127.0.0.1.jpeg)

### FAQ Page
![FAQ](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_183644_127.0.0.1.jpeg)

### Login/Registration Page
![Login/Registration](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_183713_127.0.0.1.jpeg)

### Dashboard
![Dashboard](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_184614_127.0.0.1.jpeg)

### Analysis Page
![Analysis](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_185031_localhost.jpeg)

### Prediction Page
![Prediction](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_185457_localhost.jpeg)

### Stock Comparison Page
![Stock Comparison](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_18549_localhost.jpeg)

### TradingView Page
![TradingView](https://github.com/karthikkiran123/aa/blob/main/Project_Sreenshots/Screenshot_15-10-2024_185713_127.0.0.1.jpeg)

## Setup

Follow these steps to set up StockVisionIQ on your local machine.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/StockVisionIQ.git
   cd StockVisionIQ`


2. Install Requirements Make sure you have Python installed. Then, install the required libraries:
  ```bash
  pip install -r requirements.txt
```

3. Set Up the Database Initialize and apply migrations for the Django backend.

```bash
python manage.py migrate
```

4. Run the Streamlit Dashboard Open a new terminal window and navigate to the project directory, then run the final.py file in Streamlit to start the dashboard.
```bash
streamlit run final.py
```

5. Run the Django Development Server Start the Django server.
```bash
python manage.py runserver
```


Now, you can access the application directly through Django:

- **Access StockVisionIQ**: Once both the Django and Streamlit components are running, the entire application can be accessed through the main Django URL [http://127.0.0.1:8000](http://127.0.0.1:8000).

  The dashboard, including the Streamlit-integrated stock analysis and prediction features, will be available seamlessly through this URL.


## Usage

Once logged in, users can access a comprehensive set of stock analysis features within **StockVisionIQ**:

- **Stock Ticker Analysis**: Input a stock ticker to view a detailed analysis, including financial metrics, recent news, and analyst insights.
- **Financial Data & Comparisons**: Gain insights into individual stocks or compare multiple stocks.
- **Real-Time Charts**: Use the Trading View feature to visualize real-time stock data and technical charts.
- **AI-Powered Predictions**: Predict future stock prices with the Prophet-based AI forecasting model.

The intuitive dashboard allows users to interact with each feature seamlessly, ensuring a powerful and effective analysis experience.

## Features

- **Stock Analysis**: Access comprehensive financial details and up-to-date news on selected stocks.
- **Sentiment Analysis**: Assess market sentiment through VADER-powered news article analysis.
- **Stock Comparison**: Compare the performance and key indicators of multiple stocks.
- **Trading View**: Real-time stock charts for in-depth technical analysis.
- **Prediction Model**: Utilize the AI-powered Prophet model for future price predictions.

---
