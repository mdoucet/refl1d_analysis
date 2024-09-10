
"""
    Hydration model example
"""
import numpy
import os
from refl1d.names import *
from math import *
import numpy as np
import warnings
warnings.simplefilter('ignore', UserWarning)

# Maximum Q-value ##############################################################
q = np.logspace(np.log10(0.009), np.log10(0.18), num=150)
dq = 0.025 * q / 2.35

probe = QProbe(q, dq)

# Materials ####################################################################
Si = SLD(name='Si', rho=2.07, irho=0.0)
D2O = SLD(name='D2O', rho=6.13, irho=0.0)
Ti = SLD(name='Ti', rho=-1.238, irho=0.0)
Cu = SLD(name='Cu', rho=6.446, irho=0.0)
material = SLD(name='material', rho=-1.648, irho=0.1)
SEI = SLD(name='SEI', rho=4.581, irho=0.1)

# Film definition ##############################################################
sample = (  D2O(0, 43.77) | SEI(177.7, 23.04) | material(21.73, 18.22) | Cu(566.1, 9.736) | Ti(52.91, 12.7) | Si )


sample['Ti'].thickness.range(20.0, 60.0)
sample['Ti'].material.rho.range(-2.0, 0.0)
sample['Ti'].interface.range(1.0, 20.0)
sample['Cu'].thickness.range(10.0, 800.0)
sample['Cu'].interface.range(8.0, 15.0)
sample['material'].thickness.range(15.0, 100.0)
sample['material'].material.rho.range(-3.0, 8.0)
sample['material'].interface.range(1.0, 35.0)


sample['SEI'].thickness.range(100.0, 300.0)
sample['SEI'].interface.range(5.0, 25.0) 
base_sld = Parameter(value=3, name='base_sld').range(-3.0, 8.0)
solvent_penetration = Parameter(value=0.0, name='penetration').range(0, 1)
sample['SEI'].material.rho = base_sld*(1-solvent_penetration) + sample['THF'].material.rho*solvent_penetration

probe.intensity=Parameter(value=1.0, name='normalization')
probe.background.range(0.0, 1e-05)
sample['THF'].interface.range(25.0, 150.0)

################################################################################

expt = Experiment(probe=probe, sample=sample)
problem = FitProblem(expt)
