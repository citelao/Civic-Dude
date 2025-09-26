# Using scrapy

```powershell
# uv tool run scrapy ...
uv tool run scrapy crawl meetings
uv tool run scrapy shell "https://bellevue.legistar.com/Feed.ashx?M=Calendar&ID=31515925&GUID=fe06a265-908f-4b2e-b0bf-5570c51f012c&Mode=All"

uv tool run scrapy parse "https://bellevue.legistar.com/MeetingDetail.aspx?From=RSS&ID=1340044&GUID=08396C01-1563-4E18-B521-B489520E087A" --spider meetings -c parse_meeting
```