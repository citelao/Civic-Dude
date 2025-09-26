# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MeetingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    guid = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    pubDate = scrapy.Field()
    agenda_link = scrapy.Field()
    
    # TODO: custom name
    files = scrapy.Field()
    file_urls = scrapy.Field()