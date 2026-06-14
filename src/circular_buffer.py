class CircularBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, value):
        self.buffer[self.tail] = value
        self.tail = (self.tail + 1) % self.capacity
        if self.count == self.capacity:
            self.head = (self.head + 1) % self.capacity
        self.count = min(self.count + 1, self.capacity)

    def pop_older_than(self, threshold):
        while self.count > 0 and self.buffer[self.head] <= threshold:
            self.head = (self.head + 1) % self.capacity
            self.count = self.count - 1

    def __len__(self):
        return self.count
