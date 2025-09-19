class BidirectionalIterator:
    """At this point, maybe I should've just extended UserList...
    """
    def __init__(self, collection: list = None):
        self._collection = collection if collection else []
        self._index = 0
        self.reset_iter()

    def __iter__(self):
        return self

    def __next__(self):
        if not self.hasnext():
            raise StopIteration
        self._index += 1
        return self._collection[self._index]
    
    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        return f"<BidirectionalIterator>(idx={self._index}, {self._collection})"
    
    def __add__(self, other):
        if isinstance(other, BidirectionalIterator):
            self._collection += other._collection
        elif isinstance(other, list): # don't feel like importing ANOTHER module just to support Iterable types I may not even plug in...
            self._collection += other
        else:
            self._collection.append(other)

    def __radd__(self, other):
        if isinstance(other, BidirectionalIterator):
            other._collection += self._collection
        elif isinstance(other, list):
            other += self._collection
        else:
            return NotImplemented

    def __getitem__(self, index):
        if isinstance(index, int): # Handle integer indexing
            return self._data[key]
        elif isinstance(index, slice): # Handle slicing
            return BidirectionalIterator(self._data[index])
        else:
            raise TypeError("Index must be an integer or a slice.")

    def __contains__ (self, item):
        return item in self._collection

    def __call__(self):
        return self._collection[self._index]

    def append(self, item):
        self._collection.append(item)

    def insert(self, item): # puts item at the start of the list
        self._collection.insert(0, item)

    def pop(self, index: int = -1):
        return self._collection.pop(index)

    def index(self, item):
        return self._collection.index(item)

    def next(self):
        return self.__next__()

    def prev(self):
        if not self.hasprev():
            raise StopIteration
        self._index -= 1
        return self._collection[self._index]
    
    def hasnext(self):
        return self._index + 1 < len(self._collection)

    def hasprev(self):
        return self._index - 1 >= 0

    def reset_iter(self):
        self._index = -1