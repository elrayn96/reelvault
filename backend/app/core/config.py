import os

class Settings:
    PROJECT_NAME: str = "ReelVault"
    API_V1_STR: str = "/api"
    
    # Store temporary files in this directory
    TEMP_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
    
    # Rate limit and basic safety configuration
    RATE_LIMIT_DELAY: float = 1.5  # delay between successive scrapes
    ALLOW_FALLBACK: bool = True     # fallback to simulated responsive assets if IG rate-limits or blocks cloud Run IP

settings = Settings()

# Ensure temp directory exists
os.makedirs(settings.TEMP_DIR, exist_ok=True)
