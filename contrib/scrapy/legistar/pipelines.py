# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from legistar.items import MeetingItem
from itemadapter import ItemAdapter


class LegistarPipeline:
    def process_item(self, item, spider):
        return item


class SqlitePipeline:
    def __init__(self):
        # Make a file SQLite database
       self.connection = sqlite3.connect("legistar.db")
       self.cursor = self.connection.cursor()
       self.create_tables()

    def create_tables(self):
       self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS meetings (
               id INTEGER PRIMARY KEY,
               title TEXT,
               pubDate TEXT
           )
       """)
       self.connection.commit()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, MeetingItem):
            self.cursor.execute("""
                INSERT INTO meetings (title, pubDate) VALUES (?, ?)
            """, (item['title'], item['pubDate']))
            self.connection.commit()

        return item