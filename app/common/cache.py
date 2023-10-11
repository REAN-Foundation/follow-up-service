class Cache:
    def __init__(self):
        self.cache_data = {}

    def get(self, key):
        return self.cache_data.get(key, None)

    def set(self, key, value):
        self.cache_data[key] = value

    def delete(self, key):
        if key in self.cache_data:
            del self.cache_data[key]

    def clear(self):
        self.cache_data.clear()

#####################################################################

cache = Cache()

