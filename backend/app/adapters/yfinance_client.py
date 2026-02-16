import logging
import warnings
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

class YFinanceClient:
    """
    Yahoo Finance Infrastructure Adapter.
    Handles remote data ingestion with automated adjustments for corporate actions
    and structural normalization of financial time-series.
    """
    
    def __init__(self):
        # Suppress upstream library warnings to maintain clean system logs
        warnings.filterwarnings('ignore', category=FutureWarning)
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        
        # Silence yfinance logger to prevent console noise during high-frequency calls
        logging.getLogger('yfinance').setLevel(logging.CRITICAL)

    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieves historical OHLCV data from Yahoo Finance.

        Args:
            ticker (str): Market symbol identifier.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: Cleaned and normalized market data.
        """
        try:
            logger.info(f"Ingesting market data for {ticker} via Yahoo Finance API")
            
            # Fetch data with auto-adjustment for stock splits and dividends
            df = yf.download(
                ticker, 
                start=start_date, 
                end=end_date, 
                progress=False,
                auto_adjust=True,  # Critical: Ensures 'Close' is equivalent to 'Adjusted Close'
                multi_level_index=False
            )
            
            if df.empty:
                logger.warning(f"No market data returned for symbol: {ticker}")
                return pd.DataFrame()

            # Flatten MultiIndex columns if present (common in different yfinance versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Decouple 'Date' from index for downstream processing flexibility
            df = df.reset_index()
            
            # Standardize naming conventions for consistency across the engine
            df = df.rename(columns={
                'Date': 'Date',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })
            
            # Enforce numeric data types and coerce malformed values
            cols_to_numeric = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in cols_to_numeric:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Temporal alignment and chronological sorting
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date').reset_index(drop=True)
                
            # Final sanitization: Remove incomplete data records
            df = df.dropna()

            # Selection of core features required for the HMM Pipeline
            final_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            final_cols = [c for c in final_cols if c in df.columns]
            
            logger.info(f"Successfully ingested {len(df)} records for {ticker}")
            return df[final_cols]
        
        except Exception as e:
            logger.error(f"Inference Ingestion Failure: {e}", exc_info=True)
            return pd.DataFrame()