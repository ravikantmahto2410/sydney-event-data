import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Scrapy settings
BOT_NAME = 'sydneyevent'

SPIDER_MODULES = ['sydneyevent.spiders']
NEWSPIDER_MODULE = 'sydneyevent.spiders'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 2

ITEM_PIPELINES = {
    'sydneyevent.pipelines.MongoPipeline': 300,
}

# MongoDB settings
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION')

# Debug: Print the loaded settings
print(f"Loaded MONGODB_URI: {MONGODB_URI}")
print(f"Loaded MONGODB_DB: {MONGODB_DB}")
print(f"Loaded MONGODB_COLLECTION: {MONGODB_COLLECTION}")

# Check for missing settings
if not MONGODB_URI or not MONGODB_DB or not MONGODB_COLLECTION:
    raise ValueError("One or more MongoDB settings are missing. Check your .env file.")