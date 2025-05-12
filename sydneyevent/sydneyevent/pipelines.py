import pymongo
import os

class MongoPipeline:
    def __init__(self):
        # Load MongoDB settings from environment variables (via Scrapy settings)
        mongodb_uri = os.getenv('MONGODB_URI')
        mongodb_db = os.getenv('MONGODB_DB')
        mongodb_collection = os.getenv('MONGODB_COLLECTION')

        # Validate that the settings are available
        if not mongodb_uri or not mongodb_db or not mongodb_collection:
            raise ValueError("MongoDB settings (MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION) are not set in environment variables")

        # Initialize MongoDB connection
        self.client = pymongo.MongoClient(mongodb_uri)
        self.db = self.client[mongodb_db]
        self.collection = self.db[mongodb_collection]
        self.collection.delete_many({})

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item