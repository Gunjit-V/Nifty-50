from dotenv import load_dotenv
from datetime import datetime, timezone
import logging
import sys
import os
from pyotp import TOTP
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
SECRETS_PATH = "/home/ubuntu/Desktop/code/projects/nifty/src/api/secrets.env"


def to_epoch_seconds(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def fetch_ohlc_for_date_range(symbol_search: str = 'NIFTY INDEX', start_date: str = '2025-10-01') -> None:
    load_dotenv(SECRETS_PATH)
    from vendor.ShoonyaApi.api_helper import ShoonyaApiPy
    import pandas as pd
    api = ShoonyaApiPy()

    try:
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
            sys.exit(1)
        logger.info("Login successful")

        # Find token for the symbol
        search_resp = api.searchscrip(exchange='NSE', searchtext=symbol_search)
        if not search_resp or search_resp.get('stat') != 'Ok' or not search_resp.get('values'):
            logger.error(f"Failed to find symbol for search '{symbol_search}'")
            sys.exit(1)

        scrip = search_resp['values'][0]
        token = scrip.get('token')
        tradingsymbol = scrip.get('tsym') or scrip.get('symbol')
        logger.info(f"Found symbol: {tradingsymbol} token={token}")

        # Date range
        start_dt = datetime.strptime(
            start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        today = datetime.now(timezone.utc)
        num_days = (today.date() - start_dt.date()).days + 1

        for i in range(num_days):
            day = start_dt + pd.Timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=15, minute=31, second=0, microsecond=0)
            start_epoch = to_epoch_seconds(day_start)
            end_epoch = to_epoch_seconds(day_end)

            logger.info(
                f"Fetching {tradingsymbol} OHLC for {day_start.date()}...")
            interval = '1'
            ohlc = api.get_time_price_series(
                exchange='NSE',
                token=token,
                starttime=start_epoch,
                endtime=end_epoch,
                interval=interval
            )

            if not isinstance(ohlc, list):
                logger.warning(
                    f"No OHLC data for {day_start.date()} (response: {ohlc})")
                continue
            df = pd.DataFrame(ohlc)
            df = df.drop_duplicates(subset=['time'], keep='first')
            parquet_path = os.path.join(
                current_dir, f"{tradingsymbol}_ohlc_{day_start.date()}.parquet")
            df.to_parquet(parquet_path, index=False)
            logger.info(f"Saved OHLC data to {parquet_path} ({len(df)} rows)")

    except Exception as e:
        logger.error(f"Error while fetching OHLC: {str(e)}")
        sys.exit(1)
    finally:
        try:
            api.logout()
        except Exception:
            pass


if __name__ == '__main__':
    # Usage: python src/api/fetch_ohlc_1_minute.py [SYMBOL_SEARCH] [START_DATE]
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'NIFTY INDEX'
    start_date = sys.argv[2] if len(sys.argv) > 2 else '2025-09-01'
    fetch_ohlc_for_date_range(symbol, start_date)
