from app.avatars.avatar import Avatar


class StationAvatar(Avatar):
    def __init__(self):
        super().__init__()
        self.player = None
