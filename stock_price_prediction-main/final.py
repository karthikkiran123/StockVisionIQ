import yfinance as yf
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from prophet import Prophet
import streamlit.components.v1 as components
from io import BytesIO
from streamlit_option_menu import option_menu


# Initialize NewsAPI and Sentiment Analyzer
news_api_key = 'News_Api_key'  # Replace with your NewsAPI key
newsapi = NewsApiClient(api_key=news_api_key)
NEWS_API_URL = 'https://newsapi.org/v2/everything'
analyzer = SentimentIntensityAnalyzer()

st.set_page_config(
    layout="wide"  # This should be set to "wide" for wide mode
)

# Function to fetch raw stock data
@st.cache_data
def fetch_stock_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

def get_company_name(stock):
    ticker = yf.Ticker(stock)
    return ticker.info.get('longName', 'Unknown Company')

def fetch_live_price(ticker):
    stock = yf.Ticker(ticker)
    live_price = stock.history(period="1d")["Close"].values[0]
    return live_price

def fetch_news(ticker):
    # Strip the .NS suffix for news API
    ticker_for_news = ticker.replace('.NS', '')
    today = datetime.today().strftime('%Y-%m-%d')
    last_week = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')

    params = {
        'q': ticker_for_news,
        'apiKey': news_api_key,
        'sortBy': 'popularity',  # Sort by latest news
        'from': last_week,        # Filter news from the past week
        'to': today,
        'language': 'en',          # Language of the news
        'pageSize': 10             # Limit to 10 articles
    }
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()
    if data['status'] == 'ok':
        return data['articles']
    else:
        st.error("Failed to fetch news.")
        return []
    

def analyze_sentiment(text):
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] > 0.05:
        return 'Positive'
    elif sentiment_score['compound'] < -0.05:
        return 'Negative'
    else:
        return 'Neutral'
    
# NASDAQ holidays for 2024
nasdaq_holidays = [
    '2024-01-01', '2024-01-15', '2024-02-19', '2024-03-29', '2024-05-27', 
    '2024-06-19', '2024-07-04', '2024-09-02', '2024-11-28', '2024-12-25'
]

# NSE holidays for 2024
nse_holidays = [
    '2024-01-22', '2024-01-26', '2024-03-08', '2024-03-25', '2024-03-29', 
    '2024-04-11', '2024-04-17', '2024-05-01', '2024-05-20', '2024-06-17', 
    '2024-07-17', '2024-08-15', '2024-10-02', '2024-11-01', '2024-11-15', 
    '2024-12-25'
]

# Function to fetch stock data
def fetch_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        st.error("Failed to fetch data. Please check the ticker symbol.")
        return pd.DataFrame()
    data['Close'].ffill(inplace=True)
    return data


# Function to filter out weekends and holidays
def filter_non_trading_days(future_dates, region):
    if region == "NASDAQ":
        market_holidays = pd.to_datetime(nasdaq_holidays)
    elif region == "NSE":
        market_holidays = pd.to_datetime(nse_holidays)
    else:
        market_holidays = []

    # Filter out weekends (Saturday = 5, Sunday = 6) and market-specific holidays
    return [date for date in future_dates if date.weekday() < 5 and date not in market_holidays]

# Stock prediction function optimized to avoid weekends and holidays
def predict_stock_advanced(ticker, days):
    # Determine region based on ticker
    region = "NSE" if ticker.endswith('.NS') else "NASDAQ"

    start_date = datetime.now() - timedelta(days=365)
    data = fetch_stock_data(ticker, start=start_date, end=datetime.now())

    if data.empty:
        return pd.DataFrame()

    # Prepare data for Prophet model
    df = data.reset_index()[['Date', 'Close', 'Volume']]
    df.columns = ['ds', 'y', 'Volume']

    # Initialize Prophet model and add volume as a regressor
    model = Prophet()
    model.add_regressor('Volume')
    model.fit(df)

    # Prepare future dates and filter out weekends and holidays
    future_dates = [datetime.now() + timedelta(days=i) for i in range(1, days + 1)]
    future_dates = filter_non_trading_days(future_dates, region)
    
    if not future_dates:
        st.error("No valid trading days available in the selected period.")
        return pd.DataFrame()

    future = pd.DataFrame({'ds': future_dates, 'Volume': df['Volume'].mean()})
    
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast.columns = ['Date', 'Predicted Price', 'Lower Bound', 'Upper Bound']
    
    return forecast

# Plotting predictions using a more advanced and user-friendly Plotly chart
def plot_predictions(predictions, ticker):
    fig = go.Figure()

    # Add predicted prices with scatter markers for clarity
    fig.add_trace(go.Scatter(
        x=predictions['Date'],
        y=predictions['Predicted Price'],
        mode='lines+markers',
        name='Predicted Price',
        line=dict(color='royalblue', width=3),  # Solid line for predicted price
        marker=dict(size=7, color='royalblue', symbol='circle'),  # Circular markers
        hovertemplate='<b>Date:</b> %{x}<br><b>Predicted Price:</b> $%{y:.2f}<extra></extra>'
    ))

    # Add confidence intervals with dashed lines
    fig.add_trace(go.Scatter(
        x=predictions['Date'],
        y=predictions['Lower Bound'],
        mode='lines',
        name='Lower Bound',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Lower Bound:</b> $%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=predictions['Date'],
        y=predictions['Upper Bound'],
        mode='lines',
        name='Upper Bound',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Upper Bound:</b> $%{y:.2f}<extra></extra>'
    ))

    # Fill area between the confidence bounds for better visualization
    fig.add_trace(go.Scatter(
        x=predictions['Date'].tolist() + predictions['Date'][::-1].tolist(),
        y=predictions['Upper Bound'].tolist() + predictions['Lower Bound'][::-1].tolist(),
        fill='toself',
        fillcolor='rgba(173, 216, 230, 0.3)',  # Light blue fill for the confidence area
        line=dict(color='rgba(255,255,255,0)'),  # Transparent line
        name='Confidence Interval',
        showlegend=False
    ))

    # Layout adjustments for improved aesthetics on a dark background
    fig.update_layout(
        title=f"{ticker} Price Prediction",
        title_font=dict(size=24, color='white'),
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.2)'),
        xaxis_rangeslider_visible=True,
        plot_bgcolor='black',  # Dark background
        height=600,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='white'))
    )

    # Show the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)




def format_market_cap(market_cap, currency='USD'):
    # Format market cap into billions or millions
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"  # Trillions
    if market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f}M"
    else:
        return f"${market_cap:.2f}K"


# Helper function to format large numbers as billions/millions
def format_currency(value):
    if value >= 1e12:
        return f"${value/1e12:.2f}T"  # Trillions
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"  # Billions
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"  # Millions
    else:
        return f"${value:,.2f}"  # Standard formatting

# Function to save Plotly figures as images
def save_plotly_figure_as_image(fig, file_name):
    img_bytes = fig.to_image(format="png")
    return img_bytes



# Currency symbol mapping
currency_mapping = {
    'USD': '$',  # US Dollar
    'INR': '₹',  # Indian Rupee
    'GBP': '£',  # British Pound
    'EUR': '€',  # Euro
    'JPY': '¥',  # Japanese Yen
}

# Sidebar with futuristic company name display
st.sidebar.markdown(
    "<h2 style='text-align: center; font-family: 'Courier New', monospace; color: #00FFCC; text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF;'>"
    "StockVision<span style='color: #FF6347;'>IQ</span></h2>",
    unsafe_allow_html=True
)

st.sidebar.markdown(
    "<p style='text-align: center; font-family: 'Courier New', monospace; color: #FFFFFF;'>"
    "Your trusted stock market insights<br>"
    "<span style='font-weight: bold;'>Empowering your investment journey</span>"
    "</p>",
    unsafe_allow_html=True
)
# st.sidebar.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)


# Create main page layout
# Sidebar with `option_menu` for navigation
with st.sidebar:
    selected_page = option_menu(
        "",
        ["Dashboard", "Analysis", "Stock Prediction", "TradingView Charts"],
        icons=["house", "graph-up", "calculator", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# Home Page
# Home Page
if selected_page == "Dashboard":
    st.markdown(
        """
        <style>
            body {
                background-color: #000;
                color: #fff;
            }
            .header {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 20px;
                color: #00ffff;
            }
            .intro {
                text-align: center;
                font-size: 1.2em;
                margin-bottom: 40px;
            }
            .feature-card {
                background-color: #000000;  /* Dark gray card color */
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 255, 255, 0.5);  /* Neon blue shadow for effect */
                padding: 30px;  /* Increased padding for larger cards */
                margin: 10px;
                transition: transform 0.3s;
                height: 180px;  /* Increased height for cards */
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 20px rgba(0, 255, 255, 0.9);  /* Neon blue shadow for effect */
            }
            .feature-title {
                color: #00ffff;
                font-size: 1.6em;  /* Slightly larger font for titles */
                margin-bottom: 10px;
            }
            .feature-description {
                color: #fff;
                font-size: 1em;
                height: 60px;  /* Set height for uniformity */
                overflow: hidden;  /* Hide overflow for uniform appearance */
            }
            .cta {
                text-align: center;
                margin-top: 50px;
                font-size: 1.2em;
            }
        </style>
        <div class="header">📈 Stock Analysis and Prediction Hub</div>
        <div class="intro">Your all-in-one companion for confident stock market navigation. Explore real-time data, expert insights, and advanced predictions!</div>
        """,
        unsafe_allow_html=True
    )

    # Feature Highlights
    features = {
        "🔍 Detailed Stock Information": "Track live prices, market cap, and company details to stay informed.",
        "📊 Expert Recommendations": "Get Buy, Hold, and Sell insights from top analysts.",
        "💰 Capital Allocation Insights": "Analyze how companies manage finances with clear visuals.",
        "📰 Latest Stock News": "Stay updated with real-time news and sentiment analysis.",
        "⚖️ Stock Comparisons": "Evaluate multiple stocks side-by-side for performance insights.",
        "🔮 Stock Predictions": "Utilize models to predict future stock prices based on data."
    }

    # Displaying Features in Cards
    cols = st.columns(3)  # Create a 3-column layout for features
    for index, (title, description) in enumerate(features.items()):
        with cols[index % 3]:  # Distribute cards across the columns
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-title">{title}</div>
                    <div class="feature-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Call to Action
    st.markdown(
        """
        <div class="cta">Select a stock ticker from the sidebar and begin your deep dive into analysis and predictions!</div>
        """,
        unsafe_allow_html=True
    )



# Analysis Page
elif selected_page == "Analysis":
    # Sidebar setup for ticker input
    st.sidebar.header("Stock Analysis Settings")
    default_ticker = st.sidebar.text_input('Enter a stock ticker (e.g. AAPL):', 'AAPL')


        # Function to validate the stock ticker using Yahoo Finance
    def is_valid_ticker(ticker):
        try:
            stock = yf.Ticker(ticker)
            # Check if 'longName' or 'shortName' exists in the stock info
            if 'longName' in stock.info or 'shortName' in stock.info:
                return True
            return False
        except:
            return False

    # Check if ticker is valid
    if not default_ticker:
        st.warning("Please enter a stock ticker.")
    elif not is_valid_ticker(default_ticker):
        st.warning("Invalid stock ticker. Please enter a valid stock ticker.")
    else:

        st.markdown(
            f"<h1 style='text-align: center; color: #00FFFF;font-size: 2.5em;'>Analysis for {default_ticker}</h1>", 
            unsafe_allow_html=True
        )
        # Create tabs for the Analysis page
        # Use option_menu instead of tabs
        analysis_option = option_menu(
            "", 
            ['Stock Info', 'Analyst Insights', 
            'Cap Allocation', 'Stock News', 'Compare Stocks'],
            icons=['info-circle', 'person-lines-fill', 'pie-chart', 'newspaper', 'graph-up-arrow'],
            menu_icon="bar-chart", 
            default_index=0,
            orientation="horizontal"
        )
        # Stock Info Tab
        if analysis_option == "Stock Info":
            st.header(f"{default_ticker} Stock Info")
            ticker_data = yf.Ticker(default_ticker)
            info = ticker_data.info

            currency_code = info.get('currency', 'USD')
            currency_symbol = currency_mapping.get(currency_code, '$')
            live_price = fetch_live_price(default_ticker)
            st.metric(label=f"Live {default_ticker} Price", value=f"{currency_symbol}{live_price:.2f}")

            col1, col2 = st.columns(2)
            col1.metric(label="Sector", value=info.get('sector', 'N/A'))
            col2.metric(label="Country", value=info.get('country', 'N/A'))

            st.subheader("More Details and Key Statistics")

            # Creating columns for More Details and Key Statistics
            col3, col4 = st.columns(2)
            
            # More Details
            with col3:
                st.subheader("More Details")
                st.write(f"**Market Cap:** {currency_symbol}{format_market_cap(info.get('marketCap', 0))}")
                st.write(f"**Website:** {info.get('website', 'N/A')}")
                st.write(f"**Beta:** {info.get('beta', 'N/A')}")
                
                dividend_yield = info.get('dividendYield', None)
                if dividend_yield is not None:
                    st.write(f"**Dividend Yield:** {dividend_yield*100:.2f}%")
                else:
                    st.write("**Dividend Yield:** N/A")

            # Key Statistics
            with col4:
                st.subheader("Key Statistics")
                st.markdown(
                    """
                    - **52-Week High:** {symbol}{high}
                    - **52-Week Low:** {symbol}{low}
                    - **PE Ratio:** {pe_ratio}
                    """.format(
                        symbol=currency_symbol,
                        high=info.get('fiftyTwoWeekHigh', 'N/A'),
                        low=info.get('fiftyTwoWeekLow', 'N/A'),
                        pe_ratio=info.get('trailingPE', 'N/A')
                    )
                )

            st.subheader("Industry Information")
            industry = info.get('industry', 'N/A')
            st.write(f"**Industry:** {industry if len(industry) <= 50 else industry[:47] + '...'}")

            st.subheader("Company Overview")
            st.write(f"**Description:** {info.get('longBusinessSummary', 'N/A')}")

            logo_url = info.get('logo_url', None)
            if logo_url:
                st.image(logo_url, caption=f"{default_ticker} Logo", use_column_width=True)


        # Stock Recommendations Tab
        elif analysis_option == "Analyst Insights":
            ticker_data = yf.Ticker(default_ticker)
            recommendations = ticker_data.recommendations
            

            if recommendations is not None and not recommendations.empty:
                st.subheader(f"{default_ticker} Stock Recommendations")
                st.write(
                    """
                    **Recommendations** are suggestions made by financial analysts based on their research and analysis of the stock. 
                    They typically fall into categories such as:
                    
                    - **Buy**: Analysts believe the stock is undervalued and expect it to increase in value.
                    - **Strong Buy**: Analysts are highly confident in the stock's potential and recommend buying it strongly.
                    - **Hold**: Analysts think the stock is fairly valued and recommend holding it in your portfolio.
                    - **Sell**: Analysts believe the stock is overvalued and recommend selling it.
                    - **Strong Sell**: Analysts strongly advise selling the stock due to expected significant declines.
                    """
                )

                st.write("### Latest Recommendations from Analysts")
                st.dataframe(recommendations)

                st.write(
                    """
                    **Notes on Recommendations:**
                    - Recommendations can vary among analysts and may change over time based on new information or market conditions.
                    - It’s important to consider multiple factors, including the stock's performance, industry trends, and broader market conditions, before making investment decisions.
                    - Analyst recommendations should be used as one of several tools to inform your investment strategy.
                    """
                )
            else:
                st.write(f"No recommendations data available for {default_ticker}.")

        # Capital Allocation Tab
        elif analysis_option == "Cap Allocation":
            st.header(f"{default_ticker} Capital Allocation Overview")
            st.write(f"The capital allocation breakdown of **{default_ticker}** provides insights into how the company manages its financial resources. Understanding these metrics helps evaluate the company's financial health and how effectively it uses its resources.")

            ticker_data = yf.Ticker(default_ticker).info

            market_cap = ticker_data.get('marketCap', np.nan)
            total_cash = ticker_data.get('totalCash', np.nan)
            total_debt = ticker_data.get('totalDebt', np.nan)
            debt_percentage = 0
            cash_percentage = 0
            operating_cashflow = ticker_data.get('operatingCashflow', np.nan)
            capital_expenditures = ticker_data.get('capitalExpenditures', np.nan)

                
            if not pd.isna(market_cap) and not pd.isna(total_cash):
                equity_value = market_cap + (total_debt if not pd.isna(total_debt) else 0) - total_cash
                debt_percentage = 100 * (total_debt if not pd.isna(total_debt) else 0) / equity_value
                cash_percentage = 100 * total_cash / equity_value

            # Display key metrics
            st.subheader("Key Metrics")
            st.write(f"**Market Capitalization:** {format_currency(market_cap)}\n"
                    "The total value of all outstanding shares of the company. It indicates the company's overall market value.")
            st.write(f"**Total Cash:** {format_currency(total_cash)}\n"
                    "The total cash and cash equivalents held by the company, reflecting its liquidity.")
            st.write(f"**Total Debt:** {format_currency(total_debt)}\n"
                    "The total amount of debt the company owes, including both short-term and long-term debt.")
            st.write(f"**Debt as Percentage of Equity:** {debt_percentage:.2f}%\n"
                    "The proportion of the company's debt relative to its equity. A measure of financial leverage.")
            st.write(f"**Cash as Percentage of Equity:** {cash_percentage:.2f}%\n"
                    "The proportion of the company's cash relative to its equity, indicating liquidity.")

            # Capital Expenditures and Cash Flow analysis
            if not pd.isna(operating_cashflow) and not pd.isna(capital_expenditures):
                capex_percentage = 100 * capital_expenditures / operating_cashflow
                st.write(f"**Operating Cash Flow:** {format_currency(operating_cashflow)}\n"
                        "Cash generated from the company's core business operations.")
                st.write(f"**Capital Expenditures (CapEx):** {format_currency(capital_expenditures)}\n"
                        "The amount spent on acquiring or maintaining physical assets.")
                st.write(f"**CapEx as Percentage of Cash Flow:** {capex_percentage:.2f}%\n"
                        "The proportion of operating cash flow used for capital expenditures, indicating investment in growth.")

            # Visualization: Cash and Debt Allocation with Plotly
            if not pd.isna(total_cash) and not pd.isna(total_debt):
                st.subheader("Capital Allocation Breakdown")
                labels = ['Total Cash', 'Total Debt']
                values = [total_cash, total_debt]

                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig.update_layout(
                    title_text='Cash vs Debt Allocation',
                    annotations=[dict(text=f'{default_ticker}', x=0.5, y=0.5, font_size=20, showarrow=False)]
                )

                st.plotly_chart(fig)
                    
                

            # Stock News Tab
        elif analysis_option == "Stock News":
            st.header(f"{default_ticker} Stock News")
            news_articles = fetch_news(default_ticker)

            if news_articles:
                for article in news_articles:
                    # Check if the title and description exist before rendering them
                    title = article.get('title', 'No title available')
                    description = article.get('description', 'No description available')
                    url = article.get('url', '#')

                    st.subheader(title)
                    st.write(description)
                    st.write(f"[Read more]({url})")
                    st.write(f"*Published at {article['publishedAt']}*")


                    # Only analyze sentiment if description exists and is not empty
                    if description and description != 'No description available':
                        sentiment = analyze_sentiment(description)
                        st.write(f"**Sentiment:** {sentiment}")
                    else:
                        st.write("**Sentiment:** Not available")

                    st.write("---")
            else:
                st.write("No news articles available.")

        #comparison section



        elif analysis_option == "Compare Stocks":
            st.header(f"Compare {default_ticker} with other stocks")

            # Input field for user-defined tickers
            additional_tickers = st.text_input(
                "Enter stock tickers to compare (separated by commas):", 
                value=""
            )


            # Process additional tickers
            user_tickers = [ticker.strip().upper() for ticker in additional_tickers.split(",") if ticker.strip()]
            comparison_tickers = [default_ticker] + user_tickers

            def get_exchange_rate(base_currency, target_currency):
                try:
                    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    data = response.json()
                    return data['rates'].get(target_currency, 1)
                except requests.RequestException as e:
                    st.error(f"Error fetching exchange rate: {e}")
                    return 1

            if comparison_tickers:
                # Date range selection
                start_date = st.date_input("Select start date", pd.to_datetime('2020-01-01'))
                end_date = st.date_input("Select end date", pd.to_datetime('today'))

                # Fetch and display comparison data
                st.subheader("Comparison of Key Metrics")

                # Prepare data for comparison
                comparison_data = []
                sector_industry_data = []
                market_caps = []
                dividend_yields = []
                currencies = {}

                for ticker in comparison_tickers:
                    try:
                        stock_info = yf.Ticker(ticker).info
                        market_cap = stock_info.get("marketCap", "N/A")
                        dividend_yield = stock_info.get("dividendYield", 0) * 100  # Convert to percentage
                        currency = stock_info.get("currency", 'USD')  # Default to USD if not provided
                        currencies[ticker] = currency
                        
                        comparison_data.append([
                            ticker,
                            stock_info.get("trailingPE", "N/A"),
                            f"{dividend_yield:.2f}%" if dividend_yield else "N/A",
                            f"{market_cap / 1e9:.2f} B" if market_cap != "N/A" else "N/A",  # Convert market cap to billions
                            stock_info.get("totalRevenue", "N/A"),
                            stock_info.get("returnOnEquity", "N/A"),
                            stock_info.get("debtToEquity", "N/A")
                        ])
                        sector_industry_data.append([
                            ticker,
                            stock_info.get("sector", "N/A"),
                            stock_info.get("industry", "N/A")
                        ])
                        market_caps.append(market_cap)
                        dividend_yields.append(dividend_yield)
                    except Exception as e:
                        st.write(f"Error fetching data for {ticker}: {e}")

                # Create DataFrame for key metrics
                columns = ["Ticker", "P/E Ratio", "Dividend Yield", "Market Cap", "Revenue", "ROE", "Debt to Equity"]
                df_comparison = pd.DataFrame(comparison_data, columns=columns)

                with st.expander("Key Metrics Comparison"):
                    st.dataframe(df_comparison, use_container_width=True)
                                                        # Download Comparison Data
                    st.download_button(
                        label="Download Comparison Data",
                        data=df_comparison.to_csv(index=False),
                        file_name="comparison_data.csv",
                        mime="text/csv"
                    )

                # Sector and Industry Information
                df_sector_industry = pd.DataFrame(sector_industry_data, columns=["Ticker", "Sector", "Industry"])
                with st.expander("Sector and Industry Information"):
                    st.dataframe(df_sector_industry, use_container_width=True)

                # Fetch historical data for plotting
                all_stock_data = {}
                base_currency = 'USD'
                for ticker in comparison_tickers:
                    try:
                        stock_data = yf.Ticker(ticker).history(start=start_date, end=end_date)
                        currency = currencies.get(ticker, base_currency)
                        if currency != base_currency:
                            rate = get_exchange_rate(currency, base_currency)
                            stock_data['Close'] = stock_data['Close'] * rate
                        all_stock_data[ticker] = stock_data
                    except Exception as e:
                        st.write(f"Error fetching data for {ticker}: {e}")

                # Plot comparative closing prices
                if all_stock_data:
                    fig_close = go.Figure()
                    for ticker, data in all_stock_data.items():
                        fig_close.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=ticker))
                    
                    fig_close.update_layout(
                        title='Comparative Closing Prices',
                        xaxis_title='Date',
                        yaxis_title='Closing Price (in USD)',
                        xaxis=dict(tickformat='%Y-%m-%d', rangeslider=dict(visible=False)),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_close)
                    img_close = save_plotly_figure_as_image(fig_close, "comparative_closing_prices.png")
                    st.download_button(
                        label="Download Comparative Closing Prices Chart",
                        data=img_close,
                        file_name="comparative_closing_prices.png",
                        mime="image/png"
                    )
                    st.markdown("**Note:** All closing prices are displayed in USD.")

                    # Plot moving averages
                    fig_moving_avg = go.Figure()
                    for ticker, data in all_stock_data.items():
                        fig_moving_avg.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(window=20).mean(), mode='lines', name=f'{ticker} 20-Day MA'))
                        fig_moving_avg.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(window=50).mean(), mode='lines', name=f'{ticker} 50-Day MA'))

                    fig_moving_avg.update_layout(
                        title='Moving Averages',
                        xaxis_title='Date',
                        yaxis_title='Price (in USD)',
                        xaxis=dict(tickformat='%Y-%m-%d', rangeslider=dict(visible=False)),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_moving_avg)
                    img_moving_avg = save_plotly_figure_as_image(fig_moving_avg, "moving_averages.png")
                    st.download_button(
                        label="Download Moving Averages Chart",
                        data=img_moving_avg,
                        file_name="moving_averages.png",
                        mime="image/png"
                    )

                    # Plot cumulative returns
                    fig_cumulative_returns = go.Figure()
                    for ticker, data in all_stock_data.items():
                        cumulative_returns = (data['Close'] / data['Close'].iloc[0]) - 1
                        fig_cumulative_returns.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns, mode='lines', name=ticker))

                    fig_cumulative_returns.update_layout(
                        title='Cumulative Returns',
                        xaxis_title='Date',
                        yaxis_title='Cumulative Return',
                        xaxis=dict(tickformat='%Y-%m-%d', rangeslider=dict(visible=False)),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_cumulative_returns)
                    img_cumulative_returns = save_plotly_figure_as_image(fig_cumulative_returns, "cumulative_returns.png")
                    st.download_button(
                        label="Download Cumulative Returns Chart",
                        data=img_cumulative_returns,
                        file_name="cumulative_returns.png",
                        mime="image/png"
                    )

                    # Plot market capitalization comparison
                    fig_market_cap = go.Figure()
                    for ticker, market_cap in zip(comparison_tickers, market_caps):
                        fig_market_cap.add_trace(go.Bar(x=[ticker], y=[market_cap], name=ticker))
                    
                    fig_market_cap.update_layout(title='Market Capitalization Comparison', xaxis_title='Ticker', yaxis_title='Market Cap (in Billion USD)')
                    st.plotly_chart(fig_market_cap)
                    img_market_cap = save_plotly_figure_as_image(fig_market_cap, "market_cap_comparison.png")
                    st.download_button(
                        label="Download Market Capitalization Chart",
                        data=img_market_cap,
                        file_name="market_cap_comparison.png",
                        mime="image/png"
                    )

                    # Pie chart for Market Cap distribution
                    fig_pie = go.Figure(data=[go.Pie(labels=comparison_tickers, values=market_caps)])
                    fig_pie.update_layout(title='Market Cap Distribution')
                    st.plotly_chart(fig_pie)
                    img_pie = save_plotly_figure_as_image(fig_pie, "market_cap_distribution.png")
                    st.download_button(
                        label="Download Market Cap Distribution Chart",
                        data=img_pie,
                        file_name="market_cap_distribution.png",
                        mime="image/png"
                    )

                    # Bar chart for Dividend Yield
                    fig_dividend_yield = go.Figure(data=[go.Bar(x=comparison_tickers, y=dividend_yields)])
                    fig_dividend_yield.update_layout(title='Dividend Yield Comparison', xaxis_title='Ticker', yaxis_title='Dividend Yield (%)')
                    st.plotly_chart(fig_dividend_yield)
                    img_dividend_yield = save_plotly_figure_as_image(fig_dividend_yield, "dividend_yield_comparison.png")
                    st.download_button(
                        label="Download Dividend Yield Chart",
                        data=img_dividend_yield,
                        file_name="dividend_yield_comparison.png",
                        mime="image/png"
                    )

                    # Volatility Comparison
                    volatility = {}
                    for ticker, data in all_stock_data.items():
                        returns = data['Close'].pct_change().dropna()
                        volatility[ticker] = returns.std()

                    fig_volatility = go.Figure(data=[go.Bar(x=list(volatility.keys()), y=list(volatility.values()))])
                    fig_volatility.update_layout(title='Volatility Comparison', xaxis_title='Ticker', yaxis_title='Volatility (Std Dev)')
                    st.plotly_chart(fig_volatility)
                    img_volatility = save_plotly_figure_as_image(fig_volatility, "volatility_comparison.png")
                    st.download_button(
                        label="Download Volatility Comparison Chart",
                        data=img_volatility,
                        file_name="volatility_comparison.png",
                        mime="image/png"
                    )


            else:
                st.write("Please enter at least one stock ticker to compare.")




# Stock Prediction Page
elif selected_page == "Stock Prediction":
    # Sidebar setup for ticker input
    st.sidebar.header("Stock Predictor Settings")
    default_ticker = st.sidebar.text_input('Enter a stock ticker (e.g. AAPL):', 'AAPL')
    st.sidebar.info("Note: Predictions are based on historical data and are not guaranteed to reflect future prices.")
        # Function to validate the stock ticker using Yahoo Finance
    def is_valid_ticker(ticker):
        try:
            stock = yf.Ticker(ticker)
            # Check if 'longName' or 'shortName' exists in the stock info
            if 'longName' in stock.info or 'shortName' in stock.info:
                return True
            return False
        except:
            return False

    # Check if ticker is valid
    if not default_ticker:
        st.warning("Please enter a stock ticker.")
    elif not is_valid_ticker(default_ticker):
        st.warning("Invalid stock ticker. Please enter a valid stock ticker.")
    else:
        st.markdown(f"<h1 style='text-align: center; color: #00FFFF;font-size: 2.5em;''>Stock Prediction for {default_ticker}</h1>", unsafe_allow_html=True)
        ticker = yf.Ticker(default_ticker)
        hist_data = ticker.history(period='5y')  # Fetch maximum available data

        # Check if historical data is available
        if not hist_data.empty:
            st.subheader(f"Closing Price of {default_ticker} from the earliest available date to today")
            
            # Create Plotly figure for closing prices
            fig_close = go.Figure()
            fig_close.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], mode='lines', name=default_ticker))
            
            fig_close.update_layout(
                title=f'{default_ticker} Closing Prices',
                xaxis_title='Date',
                yaxis_title='Closing Price (in your local currency)',
                xaxis=dict(tickformat='%Y-%m-%d', rangeslider=dict(visible=False)),
                hovermode='x unified'
            )
            
            # Show the Plotly chart in Streamlit
            st.plotly_chart(fig_close)
        else:
            st.error("No historical data available for this ticker.")
        days = st.slider("Number of Days for Prediction", min_value=1, max_value=10, value=7)

        # Add content explaining the prediction method
        st.markdown("""
        ### Prediction Methodology
        This stock prediction model utilizes the **Prophet** algorithm developed by Facebook, which is designed for forecasting time series data. The model analyzes historical stock prices and trading volumes to predict future price movements.

        #### How Predictions are Made:
        1. **Data Collection**: Historical stock price data is collected using the Yahoo Finance API.
        2. **Data Preparation**: The data is processed and formatted for the Prophet model, including the inclusion of trading volume as a regressor.
        3. **Model Training**: The Prophet model is trained on the historical data to learn patterns and trends.
        4. **Future Predictions**: Based on the trained model, future stock prices are predicted for a specified number of days, taking into account weekends and market-specific holidays.

        #### Data Used:
        - **Historical Prices**: The model uses daily closing prices for the stock.
        - **Volume**: Trading volume is also included to enhance prediction accuracy.
        """)

        
        # Display predictions
        predictions = predict_stock_advanced(default_ticker, days)

        if not predictions.empty:
            st.write("### Forecasted Prices")
            st.dataframe(predictions)
            plot_predictions(predictions, default_ticker)
        else:
            st.error("No predictions available.")













elif selected_page == "TradingView Charts":

    # Sidebar setup for ticker input
    st.sidebar.header("TradingView Settings")
    default_ticker1 = st.sidebar.text_input('Enter a stock ticker (e.g. AAPL):', 'AAPL')

    st.markdown(f"<h1 style='text-align: center; color: #00FFFF;font-size: 2.5em;'>TradingView Chart for {default_ticker1}</h1>", unsafe_allow_html=True)

    # Embed TradingView ticker tape widget (stock market overview)
    tradingview_widget = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
      </div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
        "symbols": [
        {"description": "Apple Inc", "proName": "NASDAQ:AAPL"},
        {"description": "Tesla", "proName": "NASDAQ:TSLA"},
        {"description": "Microsoft Corporation", "proName": "NASDAQ:MSFT"},
        {"description": "Amazon.com", "proName": "NASDAQ:AMZN"},
        {"description": "Nvidia Corporation", "proName": "NASDAQ:NVDA"},
        {"description": "Meta Platforms", "proName": "NASDAQ:META"},
        {"description": "Alphabet Inc (Class A)", "proName": "NASDAQ:GOOGL"},
        {"description": "Alphabet Inc (Class C)", "proName": "NASDAQ:GOOG"},
        {"description": "Advanced Micro Devices", "proName": "NASDAQ:AMD"},
        {"description": "Netflix Inc", "proName": "NASDAQ:NFLX"},
        {"description": "Intel Corporation", "proName": "NASDAQ:INTC"},
        {"description": "PayPal Holdings", "proName": "NASDAQ:PYPL"},
        {"description": "Cisco Systems", "proName": "NASDAQ:CSCO"},
        {"description": "PepsiCo Inc", "proName": "NASDAQ:PEP"},
        {"description": "Comcast Corporation", "proName": "NASDAQ:CMCSA"}
        ],
        "showSymbolLogo": true,
        "colorTheme": "dark",
        "isTransparent": false,
        "displayMode": "compact",
        "locale": "en"
      }
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tradingview_widget, height=100)

    # Embed TradingView advanced chart widget with dynamic ticker symbol
    chart_widget = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
      </div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
      {{
        "width": "1100",
        "height": "680",
        "symbol": "{default_ticker1}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "gridColor": "rgba(0, 0, 0, 0.06)",
        "locale": "en",
        "allow_symbol_change": true,
        "calendar": false
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(chart_widget, height=700)

    # Button to open TradingView chart in a new tab
    st.markdown(f"""
    [**Open {default_ticker1} on TradingView**](https://www.tradingview.com/chart/?symbol={default_ticker1})
    """, unsafe_allow_html=True)

    # Additional instructions for users
    st.markdown("""
    ---
    **TradingView Instructions:**
    - Use the toolbar at the top of the chart to select different chart types, timeframes, and technical indicators.
    - Hover over the chart to see detailed information about specific data points.
    - Zoom in or out using your mouse scroll wheel or the zoom controls.
    """)
