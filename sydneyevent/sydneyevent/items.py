import scrapy

class EventItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    venue = scrapy.Field()
    description = scrapy.Field()
    ticket_url = scrapy.Field()