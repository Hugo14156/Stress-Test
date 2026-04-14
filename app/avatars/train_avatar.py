from app.avatars.avatar import Avatar


class TrainAvatar(Avatar):
    """
    Avatar of a train.
    """

    def __init__(self, train_class):
        super.__init__()
        self._train_class = train_class

    def _load_config_file(self):
        pass
