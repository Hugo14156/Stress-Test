"""
Train depot entity for Stress Test.

Defines the TrainDepot class, which acts as a hub for purchasing and
maintaining trains. Also manages unique ID assignment for all tracked
entity types associated with a player.
"""

from app.avatars.stations.depot_avatar import DepotAvatar


class TrainDepot:
    """A depot that manages train ownership and entity ID tracking for a player.

    Serves as the registration point for all trains and related entities
    belonging to a player. Maintains ID sequences for each entity type
    to ensure unique identification across the game session.
    """

    ids = {
        "Cargo Station": ["cs", []],
        "Passenger Station": ["ps", []],
        "Cargo Car": ["cc", []],
        "Passenger Car": ["pc", []],
        "Cargo": ["c", []],
        "Passenger": ["p", []],
        "Train": ["t", []],
    }

    def __init__(self, player, nodes):
        """Initialise the depot with a owning player and a world position.

        Args:
            player: The player who owns this depot.
            position (tuple[float, float]): The (x, y) world coordinates of
                this depot.
            node (Node): The node of the depot.
        """
        self._player = player
        self.trains = []
        self.center_node = nodes[0]
        self.center_node.reference = self
        self.entry_node = nodes[1]
        self.avatar = DepotAvatar(self._player)

    def assign_id(self, kind):
        """Generate and register a new unique ID for an entity of the given type.

        Constructs an ID using the type's prefix and an incrementing integer
        based on the last assigned ID for that type. The new ID is appended
        to the type's ID list before being returned.

        Args:
            kind (str): The entity type key, must be one of the keys in the
                ids class variable (e.g. "Train", "Passenger", "Cargo Car").

        Returns:
            str: The newly assigned unique ID string, e.g. "t_player-3".
        """
        if self.ids[kind][1] == []:
            new_id = f"{self.ids[kind][0]}_{self._player}-{0}"
        else:
            new_id = f"{self.ids[kind][0]}_{self._player}-{int(self.ids[kind][1][-1].split("-")[-1]) + 1}"
        self.ids[kind][1].append(new_id)
        return new_id

    def add_train(self, new_train):
        if new_train not in self.trains:
            self.trains.append(new_train)

    def remove_train(self, leaving_train):
        if leaving_train in self.trains:
            self.trains.remove(leaving_train)

    @property
    def player(self):
        return self._player
