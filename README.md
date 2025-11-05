# 🚨 Pump.fun Dump Tracker Bot

A real-time monitoring bot that tracks all tokens on pump.fun and automatically detects 95% price dumps, generating visual charts and posting alerts to Twitter/X.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Description

This bot connects to the PumpPortal WebSocket API to monitor all pump.fun token trades in real-time. When a token dumps 95% from its peak price, it automatically:

- 📊 Generates a price chart showing the dump
- 🐦 Posts an alert to Twitter/X with detailed statistics
- ⏱️ Tracks dump duration and token lifetime
- 📈 Monitors market cap changes in real-time

Perfect for running 24/7 on a Raspberry Pi or any Linux server.

## ✨ Features

- **Real-time monitoring** via WebSocket connection
- **Automatic dump detection** (95% drop from peak)
- **Visual chart generation** with price history
- **Twitter/X integration** for automated posting
- **Detailed statistics**: dump duration, token age, market cap changes
- **Test mode** for verifying setup
- **Automatic reconnection** on connection loss
- **Low resource usage** - perfect for Raspberry Pi

## 📦 Requirements

- Python 3.8 or higher
- Twitter/X Developer Account with API access (Basic tier or higher)
- Raspberry Pi or Linux server (recommended for 24/7 operation)

### Python Dependencies

```
tweepy>=4.14.0
pillow>=10.0.0
requests>=2.31.0
websockets>=11.0.0
```

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/lieless-x/pumpfun-dump-tracker.git
cd pumpfun-dump-tracker
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Twitter API credentials

Get your API credentials from the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard):

1. Create a new app (or use an existing one)
2. Ensure your app has **Read and Write** permissions
3. Generate API keys and tokens
4. **Note**: You need at least the **Basic tier** ($100/month) to post tweets via API

Edit the `start_bot.sh` script and add your credentials:

```bash
export TWITTER_API_KEY="your_api_key_here"
export TWITTER_API_SECRET="your_api_secret_here"
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
export TWITTER_ACCESS_TOKEN="your_access_token_here"
export TWITTER_ACCESS_SECRET="your_access_secret_here"
```

### 5. Make the start script executable

```bash
chmod +x start_bot.sh
```

## 🎮 Usage

### Test Mode

Run a test to verify your Twitter credentials and posting functionality:

```bash
./start_bot.sh --test
```

This will create a fake dump alert and post it to Twitter.

### Normal Mode

Start monitoring for real dumps:

```bash
./start_bot.sh
```

The bot will:
1. Connect to PumpPortal WebSocket
2. Subscribe to all token trades
3. Track price movements in real-time
4. Post alerts when 95% dumps are detected

### Manual Run (without start script)

If you prefer to run manually:

```bash
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_SECRET="your_access_secret"

python3 pumpfun_tracker.py
```

## 🔧 Configuration

Edit `pumpfun_tracker.py` to customize:

- **Dump threshold**: Change `dump_percentage >= 95` to any percentage
- **Status update interval**: Modify the 10-second timer in the WebSocket loop
- **Price history retention**: Adjust the 24-hour cutoff in `update_coin_from_trade()`

## 📱 Example Tweet

```
🚨 DUMP ALERT 🚨

The coin $TOKEN just got dumped by 95% 
in the last 15 minutes!

It lived for 2 days since its creation.

Peak MC: 105.50 SOL
Current MC: 5.25 SOL

#crypto #pumpfun #dump
```

## 🖥️ Running on Raspberry Pi

### Auto-start on boot (systemd)

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/pumpfun-bot.service
```

2. Add the following (adjust paths and credentials):

```ini
[Unit]
Description=Pump.fun Dump Tracker Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pumpfun-dump-tracker
Environment="TWITTER_API_KEY=your_key"
Environment="TWITTER_API_SECRET=your_secret"
Environment="TWITTER_BEARER_TOKEN=your_token"
Environment="TWITTER_ACCESS_TOKEN=your_access_token"
Environment="TWITTER_ACCESS_SECRET=your_access_secret"
ExecStart=/home/pi/pumpfun-dump-tracker/venv/bin/python3 /home/pi/pumpfun-dump-tracker/pumpfun_tracker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable pumpfun-bot
sudo systemctl start pumpfun-bot
sudo systemctl status pumpfun-bot
```

4. View logs:

```bash
sudo journalctl -u pumpfun-bot -f
```

## ⚠️ Important Notes

### Twitter API Limitations

- **Free tier does NOT support posting tweets** - you need at least Basic tier ($100/month)
- Rate limits apply - the bot is designed to stay within limits
- Ensure your app has "Read and Write" permissions

### PumpPortal API

- The bot uses the free [PumpPortal Data API](https://pumpportal.fun/api-docs)
- No API key required
- WebSocket connection is free and unlimited

## 🛠️ Troubleshooting

### "403 Forbidden" error
- Your Twitter API tier doesn't support posting
- Check if your app has "Read and Write" permissions
- Verify all credentials are correct

### "530" or connection errors
- The WebSocket will automatically reconnect
- Check your internet connection
- Ensure firewall allows WebSocket connections

### No dumps detected
- The bot only alerts on 95%+ dumps from peak price
- Token needs at least 5 data points to be evaluated
- Adjust the threshold if needed

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 🔗 Resources

- [PumpPortal API Documentation](https://pumpportal.fun/api-docs)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [Tweepy Documentation](https://docs.tweepy.org/)

## ⚡ Support

If you find this bot useful, consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 💡 Suggesting improvements

---

**Disclaimer**: This bot is for educational and informational purposes only. Always do your own research before making any investment decisions. The authors are not responsible for any financial losses.
