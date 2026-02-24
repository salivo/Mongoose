class Document:
    def __init__(self):
        self.file_path = ""
        self.file: str | None = None

    def create(self):
        pass

    def open(self, file_path):
        self.file_path = file_path
        file_obj = open(self.file_path, "r")
        if not file_obj:
            self.file = None
        else:
            self.file = file_obj.read()

    def update(self):
        pass

    def save(self):
        file_obj = open(self.file_path, "r+")
        if self.file is not None:
            file_obj.write(self.file)
        file_obj.close()


if __name__ == "__main__":
    document = Document()
    document.open("tests/1_points.mgs")
    print(document.file)
    if document.file:
        document.file += "\n gg\n"
    document.save()
