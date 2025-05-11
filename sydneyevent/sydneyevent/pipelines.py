from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv
import os

load_dotenv()

class EventScraperPipeline:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            raise ValueError("MONGODB_URI not found in .env file")
        print(f"Connecting to MongoDB with URI: {mongo_uri}")
        try:
            self.client = MongoClient(mongo_uri)
            # Test the connection
            self.client.admin.command('ping')
        except OperationFailure as e:
            raise ValueError(f"Failed to connect to MongoDB Atlas: {str(e)}")
        self.db = self.client['sydney_events']
        self.collection = self.db['events']

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()