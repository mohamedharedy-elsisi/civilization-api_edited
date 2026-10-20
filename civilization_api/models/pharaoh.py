class Pharaoh:

    def __init__(
        self,
        id,
        name,
        dynasty,
        description,
        image
    ):
        self.id = id
        self.name = name
        self.dynasty = dynasty
        self.description = description
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dynasty": self.dynasty,
            "description": self.description,
            "image": self.image
        }