import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

class MongoDBPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.mongo_uri = settings.get('MONGODB_URI')
        self.mongo_db = settings.get('MONGODB_DB')
        self.collection_name = settings.get('MONGODB_COLLECTION')

        # Debug: Print the loaded settings
        print(f"MONGODB_URI: {self.mongo_uri}")
        print(f"MONGODB_DB: {self.mongo_db}")
        print(f"MONGODB_COLLECTION: {self.collection_name}")

        # Check if settings are missing
        if not self.mongo_uri or not self.mongo_db or not self.collection_name:
            raise ValueError("Missing MongoDB settings: MONGODB_URI, MONGODB_DB, or MONGODB_COLLECTION not set")

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(ItemAdapter(item).asdict())
            spider.logger.info(f"Inserted item into MongoDB: {item['title']}")
            return item
        except Exception as e:
            spider.logger.error(f"Failed to insert item into MongoDB: {e}")
            raise DropItem(f"Failed to insert item: {e}")