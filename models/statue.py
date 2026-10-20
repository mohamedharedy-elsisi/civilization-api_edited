class Statue:

    def __init__(
        self,
        id,
        name,
        location,
        description,
        image
    ):
        self.id = id
        self.name = name
        self.location = location
        self.description = description
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "image": self.image
        }