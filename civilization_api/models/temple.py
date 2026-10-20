class Temple:

    def __init__(
        self,
        id,
        name,
        city,
        description,
        image
    ):
        self.id = id
        self.name = name
        self.city = city
        self.description = description
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "description": self.description,
            "image": self.image
        }