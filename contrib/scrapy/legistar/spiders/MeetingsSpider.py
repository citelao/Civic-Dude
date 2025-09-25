from pathlib import Path

import scrapy

class MeetingSpider(scrapy.Spider):
    name = "meetings"

    async def start(self):
        urls = [
            # RSS feed URL for calendar events
            "https://bellevue.legistar.com/Feed.ashx?M=Calendar&ID=31515925&GUID=fe06a265-908f-4b2e-b0bf-5570c51f012c&Mode=All"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    async def parse(self, response):
        pass