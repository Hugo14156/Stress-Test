"""
Train depot entity for Stress Test.

Defines the TrainDepot class, which acts as a hub for purchasing and
maintaining trains. Also manages unique ID assignment for all tracked
entity types associated with a player.
"""

from app.avatars.stations.depot_avatar import DepotAvatar
from app.entities.entity import Entity


class TrainDepot(Entity):
    """A depot that manages train ownership and entity ID tracking for a player.

    Serves as the registration point for all trains and related entities
    belonging to a player. Maintains ID sequences for each entity type
    to ensure unique identification across the game session.
    """

    def __init__(self, player, nodes):
        """Initialise the depot with a owning player and a world position.

        Args:
            player: The player who owns this depot.
            nodes (list[Node]): The nodes of the depot; first is the center node.
        """
        super().__init__()
        self.id = self.assign_id("Depot")
        self.owner = player
        self._player = player
        self.trains = []
        self.center_node = nodes[0]
        self.center_node.reference = self
        self.entry_node = nodes[1]
        self.avatar = DepotAvatar(self._player)

    def add_train(self, new_train):
        if new_train not in self.trains:
            self.trains.append(new_train)

    def remove_train(self, leaving_train):
        if leaving_train in self.trains:
            self.trains.remove(leaving_train)

    @property
    def player(self):
        return self._player
