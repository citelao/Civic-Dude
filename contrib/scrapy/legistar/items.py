# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MeetingItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    guid = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    pubDate = scrapy.Field()

    agenda_link = scrapy.Field()
    minutes_link = scrapy.Field()
    meeting_rss_link = scrapy.Field()

    # TODO: custom name
    files = scrapy.Field()
    file_urls = scrapy.Field()

    # An array of LegislationDetail items
    details = scrapy.Field()

class LegislationDetail(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

    meeting_guid = scrapy.Field()

    fileNumber = scrapy.Field()
    attachments = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()

class LegislationAttachment(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

    detail_link = scrapy.Field()
    meeting_guid = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()