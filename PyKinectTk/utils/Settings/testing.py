class test:

    def __init__(self):

        self.x = 10

    def __getslice__(self, i, j):
        return i * j * self.x

    def __getitem__(self, key):
        if type(key) is slice:
            return key.start, key.stop

a = range(10)
print a

print a[slice(*(None,))]

