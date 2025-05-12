import pymongo

class MongoPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb+srv://sydneyevents:sydneyevents2410@cluster0.ilfuf.mongodb.net/sydneyevents?retryWrites=true&w=majority')
        self.db = self.client['sydneyevents']
        self.collection = self.db['events']
        self.collection.delete_many({})

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item