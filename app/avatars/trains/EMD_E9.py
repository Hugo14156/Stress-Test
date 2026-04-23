"""
Test train visual component for debugging train movement and physics.

Provides a simple coloured rectangle sprite with stub physics values used
during development to verify speed, acceleration, and rotation behaviour.
"""

# pylint: disable=no-member
import pygame
from app.avatars.avatar import Avatar


class EMD_E9(Avatar):
    """
    A class to represent the EMD E9 locomotive.

    Attributes:
        surface: A pygame Surface object representing the visual appearance of the locomotive.
        mass: The mass of the locomotive in kilograms.
        power_output: The power output of the locomotive in watts.
        year: The year the locomotive was built.
        power_type: The type of power used by the locomotive (e.g., diesel-electric).
    """

    # Note to self: we may remove some of the attributes from the docstring since they are private
    def __init__(self):
        """
        Initialize the specifications of the EMD E9 locomotive, including its surface representation and physical properties.

        Args: nothing

        Returns: nothing
        """
        self.surface = pygame.Surface((30, 15), pygame.SRCALPHA)
        self.surface.fill((255, 0, 0))
        pygame.draw.rect(self.surface, (0, 0, 0), self.surface.get_rect(), 3)

        self._mass = 143000 # in kg
        self._power_output = 1790000 # in watts
        self._year = 1954
        self._power_type = "Diesel-electric"



    def get_max_speed(self, car_list):
        """
        Return the maximum speed of the train in km/h.

        Args:
            car_list: a list of cars attached to the locomotive

        Returns:
            max_speed: a double representing the maximum speed of the train in km/h
        """
        gravity = 9.81 # in m/s^2
        coeff_rolling = 0.0005 # rolling resistance coefficient for steel wheels on steel rails

        carried_weight = 0
        for car in car_list:
            carried_weight += car.mass # replace later
        
        max_speed = self._power_output / (coeff_rolling * (self._mass + carried_weight) * gravity) # in m/s
        return max_speed * 3.6 # convert to km/h
        

    def get_max_acceleration(self, velocity, car_list):
        """
        Return the maximum acceleration rate of the train in km/h^2.

        Args:
            velocity: The current velocity of the train.
            car_list: A list of cars attached to the locomotive.

        Returns:
            max_acceleration: The calculated acceleration of the train in km/h^2
        """
        gravity = 9.81 # in m/s^2
        coeff_friction = 0.35 # coefficient of friction for steel wheels on steel rails

        carried_weight = 0
        for car in car_list:
            carried_weight += car.mass # replace later
        
        max_acceleration = min(coeff_friction * gravity, self._power_output / ((self._mass + carried_weight) * velocity)) # in m/s^2

        return max_acceleration * 12960 # convert to km/h^2

    def get_max_deceleration(self, velocity, car_list):
        """
        Return the maximum deceleration rate of the train in km/h^2.

        Args:
            velocity: The current velocity of the train.
            car_list: A list of cars attached to the locomotive.

        Returns:
            max_deceleration: The calculated deceleration of the train in km/h^2
        """
        max_deceleration = -self.get_max_acceleration(velocity, car_list) # in km/h^2
        return max_deceleration

    def rotate(self, world_position, angle):
        """Rotate a surface while keeping its center.

        Args:
            world_position (tuple[int, int]): The (x, y) world coordinates of the train.
            angle (float): The rotation angle in degrees (counter-clockwise).

        Returns:
            tuple[pygame.Surface, tuple[int, int]]: The rotated surface and the
                top-left position to blit it at, preserving the train's visual centre.
        """
        rotated_image = pygame.transform.rotate(self.surface, angle)
        new_rect = rotated_image.get_rect(
            center=self.surface.get_rect(
                topleft=(world_position[0] - 20 // 2, world_position[1] - 10 // 2)
            ).center
        )
        return (rotated_image, new_rect.topleft)
