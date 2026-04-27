"""Standalone scratch script for exercising the EMD E8 avatar model."""

from EMD_E8 import EMD_E8


E8 = EMD_E8()


class excar:
    """Minimal stand-in car object used by the scratch script."""

    def __init__(self):
        self.mass = 50000  # in kg


car_list = [excar(), excar(), excar()]

E8.get_max_speed(car_list)
