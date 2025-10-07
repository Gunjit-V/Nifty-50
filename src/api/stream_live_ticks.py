from dotenv import load_dotenv
import logging
import sys
import os
from pyotp import TOTP
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
SECRETS_PATH = "/home/ubuntu/Desktop/code/projects/nifty/src/api/secrets.env"


class TickDataHandler:
    def __init__(self):
        self.feed_opened = False
        self.subscription_counter = 0

    def event_handler_feed_update(self, tick_data):
        """Handle incoming tick data"""
        try:
            # Convert tick data to a more readable format with all available fields
            tick = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'symbol': tick_data.get('ts'),  # Trading Symbol
                'exchange': tick_data.get('e'),  # Exchange
                'last_traded_price': tick_data.get('lp'),  # LTP
                'last_trade_qty': tick_data.get('ltq'),  # Last Trade Quantity
                'last_trade_time': tick_data.get('ltt'),  # Last Trade Time
                'volume': tick_data.get('v'),  # Volume
                'avg_trade_price': tick_data.get('ap'),  # Average Trade Price
                'open': tick_data.get('o'),  # Open Price
                'high': tick_data.get('h'),  # High Price
                'low': tick_data.get('l'),  # Low Price
                'close': tick_data.get('c'),  # Close Price
                'total_buy_qty': tick_data.get('tbq'),  # Total Buy Quantity
                'total_sell_qty': tick_data.get('tsq'),  # Total Sell Quantity
                'market_depth': {
                    'buy': [{
                        'price': tick_data.get(f'bp{i}'),
                        'quantity': tick_data.get(f'bq{i}'),
                        'orders': tick_data.get(f'bo{i}')
                        # Best 5 Buy Prices, Quantities and Number of Orders
                    } for i in range(1, 6)],
                    'sell': [{
                        'price': tick_data.get(f'sp{i}'),
                        'quantity': tick_data.get(f'sq{i}'),
                        'orders': tick_data.get(f'so{i}')
                        # Best 5 Sell Prices, Quantities and Number of Orders
                    } for i in range(1, 6)]
                },
                'percent_change': tick_data.get('pc'),  # Percentage Change
                'open_interest': tick_data.get('oi'),  # Open Interest
                'previous_day_oi': tick_data.get('poi'),  # Previous Day OI
                'feed_time': tick_data.get('ft')  # Feed Time
            }
            print(json.dumps(tick, indent=2))
        except Exception as e:
            logger.error(f"Error processing tick data: {e}")

    def event_handler_order_update(self, order):
        """Handle order updates"""
        logger.info(f"Order Update: {order}")

    def open_callback(self):
        """Called when feed is opened"""
        self.feed_opened = True
        logger.info("Feed is opened")

    def close_callback(self):
        """Called when feed is closed"""
        self.feed_opened = False
        logger.info("Feed is closed")


def stream_live_data():
    load_dotenv(SECRETS_PATH)
    from vendor.ShoonyaApi.api_helper import ShoonyaApiPy

    # Initialize API and handler
    api = ShoonyaApiPy()
    tick_handler = TickDataHandler()

    try:
        # Login to Shoonya
        ret = api.login(
            userid=os.getenv('SHOONYA_USER_ID'),
            password=os.getenv('SHOONYA_PASSWORD'),
            twoFA=TOTP(os.getenv('SHOONYA_TOTP_KEY')).now(),
            vendor_code=os.getenv('SHOONYA_VENDOR_CODE'),
            api_secret=os.getenv('SHOONYA_API_KEY'),
            imei=os.getenv('SHOONYA_IMEI', 'default-imei')
        )

        if not ret or ret.get('stat') != 'Ok':
            logger.error(f"Login failed: {ret}")
            return

        logger.info("Login successful")

        # Start websocket with callbacks
        ret = api.start_websocket(order_update_callback=tick_handler.event_handler_order_update,
                                  subscribe_callback=tick_handler.event_handler_feed_update,
                                  socket_open_callback=tick_handler.open_callback,
                                  socket_close_callback=tick_handler.close_callback)

        # Wait for the feed to open
        while not tick_handler.feed_opened:
            pass  # Wait for feed to open

        # Subscribe to NIFTY INDEX (token: 26000) with full market depth
        ret = api.subscribe(['NSE|26000'], feed_type='d')  # 'd' for depth feed
        if ret:
            logger.info(
                "Successfully subscribed to NIFTY INDEX with full market depth")
        else:
            logger.error("Failed to subscribe to feed")

        # Keep the script running
        input("Press Enter to stop streaming...\n")

    except Exception as e:
        logger.error(f"Error in streaming data: {e}")
    finally:
        try:
            api.close_websocket()
            api.logout()
        except Exception:
            pass


if __name__ == '__main__':
    stream_live_data()
