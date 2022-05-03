
import os
import sqlite3
import sys
import zlib

MB_20 = 18 * 1024 * 1024

class Cache:
    def __init__(self):
        self.connection = sqlite3.connect("cache.db", check_same_thread=False)
        self.handler = self.connection.cursor()
        self.handler.execute('''CREATE TABLE IF NOT EXISTS CACHE (Path TEXT, Content BLOB, Frequency INT, Size INT);''')

    def hit(self, data):
        return data is not None

    def get_data(self, path):
        self.handler.execute("SELECT * FROM Cache WHERE Path = :Path", {"Path": path})
        data = self.handler.fetchone()
        if self.hit(data):
            content = zlib.decompress(data[1])
            frequency = data[2]
            frequency += 1
            self.handler.execute("UPDATE Cache SET Frequency =:Frequency WHERE Path=:Path",
                                 {"Frequency": frequency, "Path": path})
            self.connection.commit()
            return content

        #print("before insert", self.get_cache_size())

        return None

    def close(self):
        self.connection.commit()
        self.connection.close()

    def get_cache_size(self):
        cache_stat = os.stat('cache.db')
        cache_size = cache_stat.st_size
        return cache_size

    def over_size(self, data):
        cache_size = self.get_cache_size()

        return cache_size + sys.getsizeof(data) > MB_20

    def insert_data(self, path, data):
        compressed_data = zlib.compress(data)
        size = sys.getsizeof(compressed_data)
        frequency = 1
        if self.over_size(compressed_data):
            self.evict(sys.getsizeof(compressed_data))

        self.handler.execute("INSERT INTO Cache(Path,Content,Frequency,Size)VALUES(?,?,?,?)",
                             (path, compressed_data, frequency, size))
        self.connection.commit()

    def evict(self, file_size):
        cache_size = self.get_cache_size()
        while cache_size + file_size >= MB_20:
            self.handler.execute(
                "DELETE FROM Cache WHERE Path = (SELECT Path FROM Cache WHERE Frequency = (SELECT MIN(Frequency) FROM Cache))")
            self.connection.commit()
            self.handler.execute("VACUUM")
            cache_size = self.get_cache_size()
