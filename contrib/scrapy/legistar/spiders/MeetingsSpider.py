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


    # <item>
    #     <title>Arts Commission - 10/1/2025 (CANCELED)</title>
    #     <link>
    #         https://bellevue.legistar.com/Gateway.aspx?M=MD&amp;From=RSS&amp;ID=1340044&amp;GUID=08396C01-1563-4E18-B521-B489520E087A</link>
    #     <guid isPermaLink="false">08396C01-1563-4E18-B521-B489520E087A-2025-09-22-16-48-13</guid>
    #     <description />
    #     <category>Arts Commission</category>
    #     <pubDate>Mon, 22 Sep 2025 16:48:13 GMT</pubDate>
    # </item>
    async def parse(self, response):
        items = response.xpath("//item")
        for item in items:
            link = item.xpath("link/text()").get()
            yield {
                "title": item.xpath("title/text()").get(),
                "link": link,
                "guid": item.xpath("guid/text()").get(),
                "description": item.xpath("description/text()").get(),
                "category": item.xpath("category/text()").get(),
                "pubDate": item.xpath("pubDate/text()").get(),
            }

            yield response.follow(url=link, callback=self.parse_meeting)

    async def parse_meeting(self, response):
        # Parse the individual meeting page
        pass