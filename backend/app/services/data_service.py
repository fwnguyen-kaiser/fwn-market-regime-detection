import os
import logging
import pandas as pd
from app.adapters.yfinance_client import YFinanceClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class DataService:
    """
    Handles data persistence and retrieval operations, interfacing between 
    external financial APIs and local storage.
    """
    
    def __init__(self):
        self.client = YFinanceClient()
        self.data_dir = settings.DATA_DIR
        
        # Ensure the storage directory exists upon service initialization
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_and_save(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        Retrieves historical market data and serializes it to a local CSV file.

        Args:
            ticker (str): The financial instrument symbol (e.g., 'AAPL', 'BTC-USD').
            start_date (str): ISO 8601 formatted start date.
            end_date (str): ISO 8601 formatted end date.

        Returns:
            str: The generated filename for the persisted dataset.

        Raises:
            ValueError: If the remote client returns an empty dataset.
        """
        df = self.client.get_historical_data(ticker, start_date, end_date)
        
        if df.empty:
            raise ValueError(f"No historical data found for symbol: {ticker}")

        # Construct a standardized filename for internal indexing
        filename = f"{ticker}_{start_date}_{end_date}.csv"
        file_path = os.path.join(self.data_dir, filename)
        
        # Persist to local storage (CSV format)
        df.to_csv(file_path, index=False)
        logger.info(f"Dataset persisted successfully at: {file_path}")
        
        return filename

    def list_datasets(self) -> list:
        """
        Scans the data directory for available CSV datasets.

        Returns:
            list: A collection of filenames currently available for processing.
        """
        try:
            return [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        except FileNotFoundError:
            logger.warning("Target data directory does not exist.")
            return []

    def load_dataset(self, filename: str) -> pd.DataFrame:
        """
        Loads a local dataset into a pandas DataFrame with preliminary sanitization.

        Args:
            filename (str): The name of the target file.

        Returns:
            pd.DataFrame: A chronologically sorted DataFrame with parsed temporal data.

        Raises:
            FileNotFoundError: If the requested resource is missing.
        """
        file_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Requested dataset not found: {filename}")
        
        logger.info(f"Ingesting dataset: {filename}")
        df = pd.read_csv(file_path)
        
        # Perform temporal parsing and chronological alignment
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            # NOTE: Index is not set here to maintain compatibility with 
            # downstream feature engineering modules.
        
        return df