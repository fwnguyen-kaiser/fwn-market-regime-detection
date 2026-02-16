import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Global Application Configuration.
    Utilizes Pydantic for environment variable parsing, validation, and 
    type safety across the service lifecycle.
    """
    
    # Configuration to handle .env file loading and prevent namespace conflicts
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        protected_namespaces=()  # Suppresses Pydantic v2 protected namespace warnings
    )
    
    # --- API Configuration ---
    # Legacy FMP Key maintained for backward compatibility with older data adapters
    fmp_api_key: str = Field(default="", alias="FMP_API_KEY")
    
    # --- Persistence Configuration ---
    # Local filesystem path for caching financial datasets
    data_dir: str = Field(
        default=os.path.join(os.getcwd(), "data"), 
        alias="DATA_DIR"
    )
    
    @property
    def FMP_API_KEY(self) -> str:
        """Accessor for the Financial Modeling Prep API Key."""
        return self.fmp_api_key
    
    @property
    def DATA_DIR(self) -> str:
        """Provides the absolute path for the centralized data storage directory."""
        return self.data_dir

# Singleton instance initialized with environment variables
settings = Settings()

# --- Bootstrapping Logic ---
# Ensures the requisite storage infrastructure is available upon application startup
if not os.path.exists(settings.data_dir):
    try:
        os.makedirs(settings.data_dir, exist_ok=True)
        logging.info(f"System: Initialized storage directory at {settings.data_dir}")
    except Exception as e:
        logging.critical(f"System: Critical failure during directory initialization: {e}")