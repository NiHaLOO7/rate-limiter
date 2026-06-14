class HashMap:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _hash(self, key):
        # Convert each key in a hash
        key = str(key)
        h = 0
        PRIME = 31
        for c in key:
            h = (h*PRIME + ord(c)) % self.capacity
        return h

    def put(self, key, value):
        hashkey = self._hash(key)
        for i, (k,v) in enumerate(self.buckets[hashkey]):
            if k == key:
                self.buckets[hashkey][i] = (key, value)
                return
        self.buckets[hashkey].append((key, value))

    def get(self, key, default = None):
        hashkey = self._hash(key)
        for (k,v) in self.buckets[hashkey]:
            if k == key:
                return v
        return default

    def delete(self, key):
        hashKey = self._hash(key)
        self.buckets[hashKey] = [(k,v) for (k,v) in self.buckets[hashKey] if k != key]
