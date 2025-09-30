from typing import Dict, List, Optional
from datetime import datetime
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vendor/ShoonyaApi-py'))
from api_helper import ShoonyaApiPy

logger = logging.getLogger(__name__)


class ShoonyaClient:
    """Client for interacting with Shoonya API"""

    def __init__(self):
        """Initialize Shoonya API client"""
        self.api = ShoonyaApiPy()
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from environment variables"""
        self.user_id = os.getenv('SHOONYA_USER_ID')
        self.password = os.getenv('SHOONYA_PASSWORD')
        self.totp_key = os.getenv('SHOONYA_TOTP_KEY')  # For TOTP-based 2FA
        self.vendor_code = os.getenv('SHOONYA_VENDOR_CODE')
        self.api_key = os.getenv('SHOONYA_API_KEY')
        # Unique identifier
        self.imei = os.getenv('SHOONYA_IMEI', 'default-imei')

        if not all([self.user_id, self.password, self.vendor_code, self.api_key]):
            raise ValueError(
                "Missing required Shoonya API credentials in environment variables")

    def connect(self) -> bool:
        """Connect to Shoonya API and authenticate"""
        try:
            # Login to Shoonya API
            ret = self.api.login(
                userid=self.user_id,
                password=self.password,
                twoFA=self.totp_key,  # Will be used if TOTP is enabled
                vendor_code=self.vendor_code,
                api_secret=self.api_key,
                imei=self.imei
            )

            if ret.get('stat') == 'Ok':
                logger.info("Successfully connected to Shoonya API")
                return True
            else:
                logger.error(
                    f"Failed to connect to Shoonya API: {ret.get('emsg', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to Shoonya API: {str(e)}")
            raise

    def get_nifty_tick_data(self) -> List[Dict]:
        """Fetch real-time tick data for NIFTY50"""
        try:
            # Search for NIFTY50 symbol
            search_resp = self.api.searchscrip(
                exchange='NSE', searchtext='NIFTY50')

            if not search_resp or search_resp.get('stat') != 'Ok':
                logger.error("Failed to find NIFTY50 symbol")
                return []

            # Get the token for NIFTY50
            nifty_details = search_resp.get('values', [])[0]
            token = nifty_details.get('token')

            # Get tick data
            tick_data = self.api.get_time_price_series(
                exchange='NSE',
                token=token,
                starttime=int(datetime.now().timestamp()) -
                300  # Last 5 minutes
            )

            return tick_data if isinstance(tick_data, list) else []

        except Exception as e:
            logger.error(f"Error fetching NIFTY50 tick data: {str(e)}")
            return []

    def get_nifty_ohlc(self, interval: str = '1') -> List[Dict]:
        """
        Fetch OHLC data for NIFTY50

        Args:
            interval: Candle interval in minutes ('1', '5', '15', etc.)
        """
        try:
            # Search for NIFTY50 symbol
            search_resp = self.api.searchscrip(
                exchange='NSE', searchtext='NIFTY50')

            if not search_resp or search_resp.get('stat') != 'Ok':
                logger.error("Failed to find NIFTY50 symbol")
                return []

            # Get the token for NIFTY50
            nifty_details = search_resp.get('values', [])[0]
            token = nifty_details.get('token')

            # Get OHLC data
            ohlc_data = self.api.get_time_price_series(
                exchange='NSE',
                token=token,
                starttime=int(datetime.now().timestamp()) -
                86400,  # Last 24 hours
                interval=interval
            )

            return ohlc_data if isinstance(ohlc_data, list) else []

        except Exception as e:
            logger.error(f"Error fetching NIFTY50 OHLC data: {str(e)}")
            return []

    def start_streaming(self, on_tick_callback, on_connect_callback=None):
        """
        Start streaming real-time data

        Args:
            on_tick_callback: Callback function for tick data
            on_connect_callback: Callback function when connection is established
        """
        try:
            def _on_connect():
                logger.info("WebSocket connected")
                # Subscribe to NIFTY50
                search_resp = self.api.searchscrip(
                    exchange='NSE', searchtext='NIFTY50')
                if search_resp and search_resp.get('stat') == 'Ok':
                    nifty_details = search_resp.get('values', [])[0]
                    self.api.subscribe([f"NSE|{nifty_details.get('token')}"])

                if on_connect_callback:
                    on_connect_callback()

            # Start WebSocket connection
            self.api.start_websocket(
                subscribe_callback=on_tick_callback,
                socket_open_callback=_on_connect
            )

        except Exception as e:
            logger.error(f"Error starting data stream: {str(e)}")
            raise

    def stop_streaming(self):
        """Stop streaming data"""
        try:
            self.api.close_websocket()
        except Exception as e:
            logger.error(f"Error stopping data stream: {str(e)}")
            raise

    def disconnect(self):
        """Disconnect from Shoonya API"""
        try:
            self.api.logout()
        except Exception as e:
            logger.error(f"Error disconnecting from Shoonya API: {str(e)}")
            raise
