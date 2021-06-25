"""
Define a fractal
"""
from PySpace.pyspace.object import *
from PySpace.pyspace.coloring import *
from PySpace.pyspace.fold import *
from PySpace.pyspace.geo import *
from .fractal import Fractal

class BaseTreePlanetFractal(Fractal):
    def __init__(self):
        self.params_limits = []
        super().__init__()
        
    def fractal_func(self):
        obj = Object()
        obj.add(OrbitInitInf())
        for _ in range(30):
                obj.add(FoldRotateY('0'))
                obj.add(FoldAbs())
                obj.add(FoldMenger())
                obj.add(OrbitMinAbs((0.24,2.28,7.6)))
                obj.add(FoldScaleTranslate('1', (-2,-4.8,0)))
                obj.add(FoldPlane(('2',0,-1), 0))
        obj.add(Box(4.8, color='orbit'))
        return obj


