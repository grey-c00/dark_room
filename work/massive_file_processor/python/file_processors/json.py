import ijson

class JsonFileProcessor:
    def __init__(self, path: str):
        self.path = path

    def proces(self):
        for i in range(0,5):
            yield i
        pass



