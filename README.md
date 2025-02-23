# Stock Analysis Tool

## Overview
The **Stock Analysis Tool** is a web-based application that allows users to analyze and predict stock market trends. By connecting to Yahoo Finance, users can input a stock ticker to view an interactive dashboard displaying various graphs and statistics, such as price history, volume, and machine learning-based price predictions. This tool is designed for both novice investors and experienced traders.

## Features
- **Historical Data**: Fetch historical stock data for multiple time periods (e.g., 1 year, 5 years).
- **Real-Time Data**: Access real-time stock prices and updates.
- **Predictive Analysis**: Utilize machine learning models in PyTorch to predict future stock prices.
- **Graphical Visualizations**: Interactive line charts, candlestick charts, and bar charts for stock prices and volumes.
- **Customizable Dashboards**: Users can select and arrange different graphs and financial metrics for personalized views.
- **User Alerts**: Set up alerts for price thresholds and receive notifications.
- **Data Export**: Export data and analysis results to CSV/Excel files.
- **Portfolio Management**: Track the performance of investments in a user’s portfolio.

## Tech Stack
- **Front-End**: Dash, React, Plotly
- **Back-End**: Flask, yfinance, SQLAlchemy
- **Machine Learning**: PyTorch, Scikit-learn
- **Database**: SQLite (development), PostgreSQL (production)
- **Cloud Storage**: Google Cloud Storage, AWS S3
- **Deployment**: Heroku (development), AWS (production)


## Installation
To get started, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/stock-analysis-tool.git
```

## Dependencies
To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
Once the dependencies are installed, you can run the application by executing the following command:

```bash
python app.py
```

This will start a local web server, and you can view the application by visiting http://127.0.0.1:5000 in your browser.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
Thanks to Dash, React, Plotly, Flask, SQLAlchemy, PyTorch, Scikit-learn, SQLite, PostgreSQL, Google Cloud Storage, AWS S3, Heroku, and AWS for their open-source contributions to this project.