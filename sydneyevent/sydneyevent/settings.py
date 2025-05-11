BOT_NAME = 'sydneyevent'

SPIDER_MODULES = ['sydneyevent.spiders']
NEWSPIDER_MODULE = 'sydneyevent.spiders'

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2

ITEM_PIPELINES = {
    'sydneyevent.pipelines.EventScraperPipeline': 300,
}