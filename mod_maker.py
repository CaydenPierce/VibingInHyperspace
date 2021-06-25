"""
Receives raw data stream input (audio and BCI) as well as 1 number representing the number of modifiable parameters in the fractal function.

Calculates and outputs a modulation vector to feed into the fractal generator
"""


class ModMaker:
    def __init__(self, num_params):
        self.num_params = num_params
