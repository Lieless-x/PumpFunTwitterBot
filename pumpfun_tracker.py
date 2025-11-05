import os
import time
import json
import asyncio
import websockets
from datetime import datetime, timedelta
from collections import defaultdict
import tweepy
from PIL import Image, ImageDraw, ImageFont
import io

class PumpFunDumpTracker:
    def __init__(self, test_mode=False):
        # Twitter API credentials
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client (v2 API)
        self.twitter_client = tweepy.Client(
            bearer_token=self.twitter_bearer_token,
            consumer_key=self.twitter_api_key,
            consumer_secret=self.twitter_api_secret,
            access_token=self.twitter_access_token,
            access_token_secret=self.twitter_access_secret
        )
        
        # Initialize Twitter API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(
            self.twitter_api_key,
            self.twitter_api_secret,
            self.twitter_access_token,
            self.twitter_access_secret
        )
        self.twitter_api_v1 = tweepy.API(auth)
        
        # Track coins and their price history
        self.coin_data = defaultdict(lambda: {
            'prices': [],
            'timestamps': [],
            'creation_time': None,
            'peak_price': 0,
            'peak_mcap': 0,
            'alerted': False,
            'name': '',
            'symbol': '',
            'last_trade_time': None
        })
        
        self.websocket_url = "wss://pumpportal.fun/api/data"
        self.test_mode = test_mode
        
    def update_coin_from_trade(self, trade_data):
        """Update coin data from a trade event"""
        mint = trade_data.get('mint')
        if not mint:
            return None
            
        coin_info = self.coin_data[mint]
        current_time = datetime.now()
        
        # Initialize coin info if first time seeing it
        if not coin_info['creation_time']:
            coin_info['creation_time'] = current_time
            coin_info['name'] = trade_data.get('name', 'Unknown')
            coin_info['symbol'] = trade_data.get('symbol', 'UNKNOWN')
        
        # Get market cap in SOL
        market_cap_sol = float(trade_data.get('marketCapSol', 0))
        
        # Update price history
        coin_info['prices'].append(market_cap_sol)
        coin_info['timestamps'].append(current_time)
        coin_info['last_trade_time'] = current_time
        
        # Update peak
        if market_cap_sol > coin_info['peak_mcap']:
            coin_info['peak_mcap'] = market_cap_sol
            coin_info['peak_price'] = market_cap_sol
        
        # Keep only last 24 hours of data
        cutoff_time = current_time - timedelta(hours=24)
        while coin_info['timestamps'] and coin_info['timestamps'][0] < cutoff_time:
            coin_info['prices'].pop(0)
            coin_info['timestamps'].pop(0)
        
        return mint
    
    def create_test_dump_data(self):
        """Create fake dump data for testing"""
        # Generate fake price history showing a pump and dump
        base_time = datetime.now() - timedelta(hours=2)
        fake_history = []
        
        # Gradual rise
        for i in range(20):
            t = base_time + timedelta(minutes=i*3)
            price = 10 + (i * 5)  # Rise to 105 SOL
            fake_history.append((t, price))
        
        # Peak
        for i in range(5):
            t = base_time + timedelta(minutes=60 + i*2)
            fake_history.append((t, 105))
        
        # Sharp dump
        dump_prices = [105, 80, 50, 20, 8, 5.25]
        for i, price in enumerate(dump_prices):
            t = base_time + timedelta(minutes=70 + i)
            fake_history.append((t, price))
        
        return {
            'mint': 'TEST123456789',
            'name': 'Test Coin',
            'symbol': 'TEST',
            'dump_percentage': 95.0,
            'minutes_since_dump': 6,
            'days_since_creation': 0,
            'hours_since_creation': 2,
            'peak_price': 105.0,
            'current_price': 5.25,
            'price_history': fake_history
        }
    
    def test_twitter_post(self):
        """Test posting to Twitter with fake data"""
        print("🧪 TEST MODE: Creating test dump alert...")
        test_data = self.create_test_dump_data()
        
        try:
            success = self.post_to_twitter(test_data)
            if success:
                print("✅ Test post successful! Check your Twitter account.")
                return True
            else:
                print("❌ Test post failed. Check error messages above.")
                return False
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
    
        """Check if coin has been dumped by 95%"""
        coin_info = self.coin_data[mint]
        
        if coin_info['alerted'] or coin_info['peak_mcap'] == 0:
            return False
        
        # Need at least some price history
        if len(coin_info['prices']) < 5:
            return False
        
        current_price = coin_info['prices'][-1]
        dump_percentage = ((coin_info['peak_mcap'] - current_price) / coin_info['peak_mcap']) * 100
        
        if dump_percentage >= 95:
            # Calculate time since dump started
            dump_start_time = None
            for i in range(len(coin_info['prices']) - 1, -1, -1):
                if coin_info['prices'][i] >= coin_info['peak_mcap'] * 0.5:
                    dump_start_time = coin_info['timestamps'][i]
                    break
            
            minutes_since_dump = 0
            if dump_start_time:
                minutes_since_dump = int((datetime.now() - dump_start_time).total_seconds() / 60)
            
            # Calculate coin age
            creation_time = coin_info['creation_time']
            days_since_creation = (datetime.now() - creation_time).days
            hours_since_creation = int((datetime.now() - creation_time).total_seconds() / 3600)
            
            coin_info['alerted'] = True
            return {
                'mint': mint,
                'name': coin_info['name'],
                'symbol': coin_info['symbol'],
                'dump_percentage': dump_percentage,
                'minutes_since_dump': minutes_since_dump,
                'days_since_creation': days_since_creation,
                'hours_since_creation': hours_since_creation,
                'peak_price': coin_info['peak_mcap'],
                'current_price': current_price,
                'price_history': list(zip(coin_info['timestamps'], coin_info['prices']))
            }
        
        return False
    
    def create_chart_image(self, dump_data):
        """Create a simple price chart"""
        width, height = 800, 400
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        # Get price history
        history = dump_data['price_history']
        if len(history) < 2:
            return img
        
        prices = [p for _, p in history]
        max_price = max(prices)
        min_price = min(prices)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Draw chart area
        margin = 50
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin
        
        # Draw grid lines
        for i in range(5):
            y = margin + (chart_height / 4) * i
            draw.line([(margin, y), (width - margin, y)], fill='#333333', width=1)
        
        # Plot price line
        points = []
        for i, (_, price) in enumerate(history):
            x = margin + (i / (len(history) - 1)) * chart_width
            y = margin + chart_height - ((price - min_price) / price_range) * chart_height
            points.append((x, y))
        
        if len(points) > 1:
            draw.line(points, fill='#00ff00', width=3)
        
        # Mark the dump point (last point)
        if points:
            last_x, last_y = points[-1]
            draw.ellipse([last_x - 5, last_y - 5, last_x + 5, last_y + 5], fill='#ff0000')
        
        # Add labels
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        draw.text((width // 2 - 100, 10), "95% DUMP DETECTED", fill='#ff0000', font=font)
        draw.text((margin, height - 30), f"Peak: {max_price:.2f} SOL", fill='#ffffff', font=small_font)
        draw.text((width - margin - 150, height - 30), f"Current: {dump_data['current_price']:.2f} SOL", fill='#ffffff', font=small_font)
        
        return img
    
    def post_to_twitter(self, dump_data):
        """Post dump alert to Twitter with chart"""
        try:
            # Create tweet text
            time_unit = "days" if dump_data['days_since_creation'] > 0 else "hours"
            time_value = dump_data['days_since_creation'] if dump_data['days_since_creation'] > 0 else dump_data['hours_since_creation']
            
            tweet_text = (
                f"🚨 DUMP ALERT 🚨\n\n"
                f"The coin ${dump_data['symbol']} just got dumped by 95% "
                f"in the last {dump_data['minutes_since_dump']} minutes!\n\n"
                f"It lived for {time_value} {time_unit} since its creation.\n\n"
                f"Peak MC: {dump_data['peak_price']:.2f} SOL\n"
                f"Current MC: {dump_data['current_price']:.2f} SOL\n\n"
                f"#crypto #pumpfun #dump"
            )
            
            # Create chart image
            chart = self.create_chart_image(dump_data)
            
            # Save to bytes
            img_bytes = io.BytesIO()
            chart.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Upload media using v1.1 API
            media = self.twitter_api_v1.media_upload(filename="chart.png", file=img_bytes)
            
            # Post tweet with media using v2 API
            self.twitter_client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            print(f"✅ Posted dump alert for ${dump_data['symbol']}")
            return True
            
        except Exception as e:
            print(f"❌ Error posting to Twitter: {e}")
            return False
    
    async def connect_websocket(self):
        """Connect to PumpPortal WebSocket and listen for trades"""
        print(f"🔌 Connecting to {self.websocket_url}...")
        
        while True:
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    print("✅ Connected to PumpPortal WebSocket!")
                    
                    # Subscribe to all token trades
                    subscribe_message = {
                        "method": "subscribeTokenTrade",
                        "keys": ["all"]  # Subscribe to all tokens
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    print("📡 Subscribed to all token trades")
                    
                    # Also subscribe to new token creation
                    new_token_sub = {
                        "method": "subscribeNewToken"
                    }
                    await websocket.send(json.dumps(new_token_sub))
                    print("📡 Subscribed to new token creation")
                    
                    coins_tracked = set()
                    trades_processed = 0
                    last_status_time = time.time()
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            # Handle trade events
                            if 'mint' in data and 'marketCapSol' in data:
                                mint = self.update_coin_from_trade(data)
                                trades_processed += 1
                                
                                if mint:
                                    if mint not in coins_tracked:
                                        coins_tracked.add(mint)
                                    
                                    # Print status every 10 seconds
                                    current_time = time.time()
                                    if current_time - last_status_time >= 10:
                                        print(f"📊 Tracking {len(coins_tracked)} coins | {trades_processed} trades processed | Monitoring for dumps...")
                                        last_status_time = current_time
                                    
                                    # Check for dump
                                    dump_data = self.check_for_dump(mint)
                                    if dump_data:
                                        print(f"\n🚨 DUMP DETECTED: ${dump_data['symbol']} ({dump_data['name']})")
                                        print(f"   Peak: {dump_data['peak_price']:.2f} SOL → Current: {dump_data['current_price']:.2f} SOL")
                                        print(f"   Dumped {dump_data['dump_percentage']:.1f}% in {dump_data['minutes_since_dump']} minutes\n")
                                        self.post_to_twitter(dump_data)
                                        
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"⚠️ Error processing message: {e}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                print("⚠️ Connection closed. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ WebSocket error: {e}")
                print("🔄 Reconnecting in 10 seconds...")
                await asyncio.sleep(10)
    
    def run(self):
        """Main bot loop"""
        print("🤖 Pump.fun Dump Tracker Bot Started!")
        
        # Run test if in test mode
        if self.test_mode:
            print("🧪 Running in TEST MODE")
            print("━" * 50)
            self.test_twitter_post()
            print("━" * 50)
            print("\n✅ Test complete! Exiting...")
            return
        
        print("🎯 Monitoring for 95% dumps from peak prices")
        print("━" * 50)
        
        # Run async WebSocket connection
        asyncio.run(self.connect_websocket())

if __name__ == "__main__":
    import sys
    
    # Check if test mode requested
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    
    bot = PumpFunDumpTracker(test_mode=test_mode)
    bot.run()
