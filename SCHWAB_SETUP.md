# Charles Schwab API Integration

This guide will walk you through setting up the Charles Schwab API integration for real-time market data.

## 🚀 Quick Setup

### 1. Prerequisites

- **Schwab Brokerage Account**: You need an active Charles Schwab brokerage account
- **Same Email**: Use the SAME email address for both your brokerage account and developer account

### 2. Create Schwab Developer Account

1. Go to [https://beta-developer.schwab.com/](https://beta-developer.schwab.com/)
2. Create an account using your **Schwab brokerage account email**
3. Verify your email and complete the registration

### 3. Create a Developer App

1. In your developer dashboard, click **"Create App"**
2. Choose **"Individual Developer App"**
3. Fill out the app details:
   - **App Name**: `FInsightAI Trading Agent`
   - **App Description**: `Autonomous trading agent with real-time market analysis`
   - **Callback URL**: `https://127.0.0.1`

### 4. Add API Products

**CRITICAL**: You must add BOTH API products:

1. **Accounts and Trading Production**
2. **Market Data Production**

### 5. Wait for Approval

- Your app status must be **"Ready for Use"**
- **"Approved - Pending" will NOT work**
- This can take 1-2 business days

### 6. Enable TOS (Thinkorswim)

- Log into your Schwab account
- Enable Thinkorswim (TOS) platform access
- This is required for API functionality

## 📝 Configuration

### 1. Run the Setup Script

```bash
cd backend
python setup_schwab.py
```

This interactive script will guide you through:
- Credential input validation
- Environment file creation
- Connection testing

### 2. Manual Setup (Alternative)

If you prefer manual setup:

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```env
   APP_KEY=your_32_character_app_key_here
   APP_SECRET=your_16_character_app_secret_here
   CALLBACK_URL=https://127.0.0.1
   ```

3. **Get your credentials:**
   - Log into [developer.schwab.com](https://beta-developer.schwab.com/)
   - Go to your app dashboard
   - Copy the **App Key** (32 characters)
   - Copy the **App Secret** (16 characters)

## 🧪 Testing

### 1. Test API Connection

```bash
cd backend
python -c "from app.schwab_api import test_schwab_connection; test_schwab_connection()"
```

### 2. Start the Backend

```bash
uvicorn app.main:app --reload
```

### 3. Test Endpoints

Visit these URLs to test the integration:

- **Connection Test**: http://localhost:8000/api/market/test-connection
- **API Documentation**: http://localhost:8000/docs
- **Get Quotes**: http://localhost:8000/api/market/quotes/AAPL,MSFT,TSLA

### 4. Frontend Testing

1. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

2. Visit http://localhost:3000
3. Click on the **"Market Data (Schwab API)"** tab
4. Test the connection and get real-time quotes

## 📊 Features

### Real-Time Market Data
- Live stock quotes with prices, volume, changes
- Support for multiple symbols simultaneously
- Real-time streaming data (WebSocket-based)
- Historical price data

### Account Integration
- View linked Schwab accounts
- Account balances and positions (when implemented)
- Trading capabilities (future enhancement)

### Data Management
- Automatic data saving to PostgreSQL database
- Historical data storage and retrieval
- Trading signals and analytics

## 🔧 API Endpoints

### Market Data
- `GET /api/market/test-connection` - Test Schwab API connection
- `GET /api/market/quotes/{symbols}` - Get real-time quotes
- `GET /api/market/history/{symbol}` - Get historical data
- `POST /api/market/stream/start` - Start real-time streaming
- `POST /api/market/stream/stop` - Stop real-time streaming
- `GET /api/market/accounts` - Get account information

### Database
- `GET /api/market/data/recent/{symbol}` - Get recent stored data
- `GET /api/market/signals/recent` - Get recent trading signals

## 🚨 Troubleshooting

### Common Issues

#### 1. "App status is Approved - Pending"
- **Solution**: Wait for status to change to "Ready for Use"
- This can take 1-2 business days
- The app must be fully approved, not just pending

#### 2. "Client not authorized" Error
- **Solution**: Make sure both API products are added to your app
- Check that your app status is "Ready for Use"
- Verify credentials are correct

#### 3. OAuth 2.0 Authentication Issues
- **Solution**: The schwabdev library handles OAuth automatically
- Follow the browser prompts during first authentication
- Tokens are saved automatically in `tokens.json`

#### 4. "Invalid credential lengths"
- **Solution**: Verify your credentials
- APP_KEY should be exactly 32 characters
- APP_SECRET should be exactly 16 characters

#### 5. SSL Certificate Issues (macOS)
- **Solution**: Install Python certificates
- Run: `/Applications/Python\ 3.12/Install\ Certificates.command`
- (Adjust Python version as needed)

### Getting Help

1. **Check the logs**: Backend logs show detailed error messages
2. **API Documentation**: Visit http://localhost:8000/docs for interactive testing
3. **Schwab Developer Support**: Contact traderapi@schwab.com
4. **Schwabdev Library Docs**: [https://tylerebowers.github.io/Schwabdev/](https://tylerebowers.github.io/Schwabdev/)

## 🔐 Security Notes

- **Never commit your `.env` file** - It's automatically added to `.gitignore`
- **Keep your credentials secure** - They provide access to your brokerage account
- **Use environment variables** - Never hardcode credentials in your code
- **Tokens expire** - Access tokens expire every 30 minutes, refresh tokens every 7 days
- **Automatic management** - The schwabdev library handles token refresh automatically

## 📈 Next Steps

Once you have the Schwab API working:

1. **Implement Trading Logic** - Add buy/sell order capabilities
2. **Advanced Analytics** - Implement technical indicators and analysis
3. **Risk Management** - Add position sizing and risk controls
4. **Backtesting** - Test strategies against historical data
5. **Notifications** - Add alerts for trading signals and account changes

## 🎯 Phase 2 Complete

With the Schwab API integration working, you've completed:
- ✅ Real-time market data integration
- ✅ OAuth 2.0 authentication (automated)
- ✅ Database storage for market data
- ✅ React frontend for data visualization
- ✅ Comprehensive API endpoints
- ✅ Error handling and troubleshooting

**Ready for Phase 3**: Advanced trading algorithms and strategy implementation!
