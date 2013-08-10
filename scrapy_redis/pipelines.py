import redis

from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue"""

    def __init__(self, host, port, db):
        self.server = redis.Redis(host, port, db)
        self.encoder = ScrapyJSONEncoder()

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        db = setting.get('REDIS_DB', 0)
        return cls(host, port, db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = self.encoder.encode(item)
        self.server.rpush(key, data)
        return item

    def item_key(self, item, spider):
        """Returns redis key based on given spider"""
        return "%s:items" % spider.name
