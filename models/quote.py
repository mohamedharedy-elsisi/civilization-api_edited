class Quote:

    def __init__(
        self,
        id,
        text,
        image
    ):
        self.id = id
        self.text = text
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "image": self.image
        }