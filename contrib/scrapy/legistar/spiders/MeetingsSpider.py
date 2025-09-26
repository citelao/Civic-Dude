from pathlib import Path

from legistar.items import LegislationAttachment, LegislationDetail, MeetingItem
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
        for item in items[:5]:
            link = item.xpath("link/text()").get()
            meeting_item = MeetingItem()
            meeting_item["title"] = item.xpath("title/text()").get()
            meeting_item["link"] = link
            meeting_item["guid"] = item.xpath("guid/text()").get()
            meeting_item["description"] = item.xpath("description/text()").get()
            meeting_item["category"] = item.xpath("category/text()").get()
            meeting_item["pubDate"] = item.xpath("pubDate/text()").get()

            # Don't do this: we yield the meeting item in parse_meeting.
            # yield meeting_item

            yield response.follow(url=link, callback=self.parse_meeting, cb_kwargs={"meeting_item": meeting_item})

    # uv tool run scrapy parse --spider meetings -c parse_meeting "https://bellevue.legistar.com/MeetingDetail.aspx?From=RSS&ID=1340044&GUID=08396C01-1563-4E18-B521-B489520E087A"
    # https://bellevue.legistar.com/Gateway.aspx?M=MD&amp;From=RSS&amp;ID=1340044&amp;GUID=08396C01-1563-4E18-B521-B489520E087A
    # https://bellevue.legistar.com/MeetingDetail.aspx?From=RSS&ID=1340044&GUID=08396C01-1563-4E18-B521-B489520E087A
    async def parse_meeting(self, response, meeting_item = None):
        # Parse the individual meeting page
        if meeting_item is None:
            meeting_item = MeetingItem()

        # Look for a link with an id that ends with `_hypAgenda` (e.g.
        # `ctl00_ContentPlaceHolder1_hypAgenda`)
        agenda_link = response.css("a[id$='_hypAgenda']::attr(href)").get()
        full_agenda_link = response.urljoin(agenda_link) if agenda_link else None
        meeting_item["agenda_link"] = full_agenda_link

        minutes_link = response.css("a[id$='_hypMinutes']::attr(href)").get()
        full_minutes_link = response.urljoin(minutes_link) if minutes_link else None
        meeting_item["minutes_link"] = full_minutes_link

        # if meeting item file_urls is not set, initialize it
        if "file_urls" not in meeting_item:
            meeting_item["file_urls"] = []

        if full_agenda_link:
            meeting_item["file_urls"].append(full_agenda_link)
        if full_minutes_link:
            meeting_item["file_urls"].append(full_minutes_link)

        # Extract the RSS feed URL
        # ```
        # window.open(\'https://bellevue.legistar.com/Feed.ashx?M=CalendarDetail&ID=1273104&GUID=3DF9966D-3E8D-44D3-9F1B-56A33F096E21&Title=City+of+Bellevue+-+Meeting+of+City+Council+Regular+Meeting+on+7%2f22%2f2025+at+6%3a00+PM\'); return false;WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$ButtonRSS", "", true, "", "", false, false))
        # ```
        full_script = response.css("input[id$='ButtonRSS']::attr(onclick)").get()
        if full_script:
            start = full_script.find("https://")
            end = full_script.find("');", start)
            if start != -1 and end != -1:
                rss_feed_url = full_script[start:end]
                meeting_item["meeting_rss_link"] = rss_feed_url

                # Follow the RSS feed URL to get more details
                yield response.follow(url=rss_feed_url, callback=self.parse_meeting_rss, cb_kwargs={"meeting_item": meeting_item})
            else:
                self.logger.warning("Could not extract RSS feed URL from script")
        else:
            self.logger.warning("No RSS feed URL found on meeting page")

        yield meeting_item

    # https://bellevue.legistar.com/Feed.ashx?M=CalendarDetail&ID=1273104&GUID=3DF9966D-3E8D-44D3-9F1B-56A33F096E21
    async def parse_meeting_rss(self, response, meeting_item = None):
        # A bunch of items with titles!
        items = response.xpath("//item")
        for item in items:
            title = item.xpath("title/text()").get()
            link = item.xpath("link/text()").get()
            # self.logger.info(f"Found legislation item: {title} - {link}")

            # Follow the link to get more details
            yield response.follow(url=link, callback=self.parse_legislation_detail, cb_kwargs={"meeting_item": meeting_item})

    # uv tool run scrapy parse --spider meetings -c parse_legislation_detail "https://bellevue.legistar.com/LegislationDetail.aspx?From=RSS&ID=7489964&GUID=96986566-4EF9-4510-8D93-09DD72DF8781"
    # https://bellevue.legistar.com/LegislationDetail.aspx?From=RSS&ID=7489964&GUID=96986566-4EF9-4510-8D93-09DD72DF8781
    async def parse_legislation_detail(self, response, meeting_item = None):
        legislation = LegislationDetail()
        legislation["title"] = response.css("table[id$='_tblTitle'] span[id$='_lblTitle2'] font::text").get()
        legislation["link"] = response.url
        legislation["fileNumber"] = response.css("span[id$='_lblFile2'] font::text").get()

        if meeting_item:
            legislation["meeting_guid"] = meeting_item.get("guid")

        # Look for attachments
        # legislation["attachments"] = []
        attachment_links = response.css("table[id$='_tblAttachments'] a")
        for link in attachment_links:
            text = link.css("::text").get()
            url = link.css("::attr(href)").get()
            full_link = response.urljoin(url)

            attachment = LegislationAttachment()
            attachment["title"] = text
            attachment["link"] = full_link
            attachment["file_urls"] = [full_link]

            attachment["detail_link"] = response.url
            if meeting_item:
                attachment["meeting_guid"] = meeting_item.get("guid")

            # legislation["attachments"].append(attachment)

            yield attachment

        yield legislation
