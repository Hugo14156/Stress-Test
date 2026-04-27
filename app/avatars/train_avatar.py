"""Train avatar base class for locomotive sprites and performance stats."""

from app.avatars.avatar import Avatar


class TrainAvatar(Avatar):
    """Base avatar for locomotives, including power and wear statistics."""

    def __init__(self):
        """Initialise the locomotive metadata to neutral defaults."""
        super().__init__()
        self._mass = 0  # in kg
        self._power_output = 0  # in watts
        self._year = 0
        self._power_type = ""
        self._condition_rating = 0  # In wear per second
        self._name = ""

    def get_max_speed(self, car_list):
        """
        Return the maximum speed of the train in km/h.

        Args:
            car_list: a list of cars attached to the locomotive

        Returns:
            max_speed: a double representing the maximum speed of the train in km/h
        """
        gravity = 9.81  # in m/s^2
        coeff_rolling = (
            0.0005  # rolling resistance coefficient for steel wheels on steel rails
        )

        carried_weight = 0
        for car in car_list:
            carried_weight += car.avatar.mass  # replace later

        max_speed = self._power_output / (
            coeff_rolling * (self._mass + carried_weight) * gravity
        )  # in m/s
        return max_speed * 3.6  # convert to km/h

    def get_acceleration(self, velocity, car_list):
        """
        Return the (maximum) acceleration rate of the train in km/h^2.

        Args:
            velocity: The current velocity of the train.
            car_list: A list of cars attached to the locomotive.

        Returns:
            acceleration: The calculated acceleration of the train in km/h^2
        """
        gravity = 9.81  # in m/s^2
        coeff_friction = 0.35  # coefficient of friction for steel wheels on steel rails

        carried_weight = 0
        for car in car_list:
            carried_weight += car.avatar.mass
        if velocity == 0:
            acceleration = coeff_friction * gravity  # in m/s^2
        else:
            acceleration = min(
                coeff_friction * gravity,
                self._power_output / ((self._mass + carried_weight) * velocity),
            )  # in m/s^2

        return acceleration  # * 12960 # convert to km/h^2

    def get_deceleration(self, velocity, car_list):
        """
        Return the (maximum) deceleration rate of the train in km/h^2.

        Args:
            velocity: The current velocity of the train.
            car_list: A list of cars attached to the locomotive.

        Returns:
            deceleration: The calculated deceleration of the train in km/h^2
        """
        deceleration = -self.get_acceleration(velocity, car_list)  # in km/h^2
        return deceleration

    def update_condition(self, dt):
        """Return the amount of condition lost during the given time step."""
        return self._condition_rating * dt
