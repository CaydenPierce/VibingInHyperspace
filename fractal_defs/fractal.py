"""
General fractal that defines the function of the fractal, how many modifiable parameters is will have, and the values that each of those modifiable parameters can take.

Child class should just define the self.param_limits which specifies the minimum and maximum value for each parameter (this is the artistic and human element - you have to spend some time playing with the fractals to choose the modulation space (the fractal vector) in order to achive the desired visual effect.
"""



class Fractal:
    def __init__(self):
        self.num_params = len(self.params_limits)
        self.params = [None] * self.num_params


