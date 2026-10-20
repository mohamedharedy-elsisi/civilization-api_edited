class Obelisk:
    def __init__(
        self,
        id,
        name,
        arabic_name,
        location,
        description,
        image
    ):
        self.id = id
        self.name = name
        self.arabic_name = arabic_name
        self.location = location
        self.description = description
        self.image = image

    def to_dict(self):
        return self.__dict__