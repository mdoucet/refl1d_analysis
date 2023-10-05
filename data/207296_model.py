
import numpy
import os
from refl1d.names import *
from math import *
import warnings
warnings.simplefilter('ignore', UserWarning)

# Maximum Q-value ##############################################################
q_min = 0.0
q_max = 1.0

reduced_file = "REFL_207296_combined_data_auto.txt"

Q, R, dR, dQ = numpy.loadtxt(reduced_file).T
i_min = min([i for i in range(len(Q)) if Q[i]>q_min])
i_max = max([i for i in range(len(Q)) if Q[i]<q_max])+1

# SNS data is FWHM
dQ_std = dQ/2.35
probe = QProbe(Q[i_min:i_max], dQ_std[i_min:i_max], data=(R[i_min:i_max], dR[i_min:i_max]))

# Materials ####################################################################
Si = SLD(name='Si', rho=2.07, irho=0.0)
THF = SLD(name='THF', rho=6.13, irho=0.0)
Ti = SLD(name='Ti', rho=-1.238, irho=0.0)
Cu = SLD(name='Cu', rho=6.446, irho=0.0)
material = SLD(name='material', rho=-1.648, irho=0.1)
SEI = SLD(name='SEI', rho=4.581, irho=0.1)


# Film definition ##############################################################
sample = (  THF(0, 43.77) | SEI(177.7, 23.04) | material(21.73, 18.22) | Cu(566.1, 9.736) | Ti(52.91, 12.7) | Si )

sample['Ti'].thickness.range(20.0, 60.0)
sample['Ti'].material.rho.range(-2.0, 0.0)
sample['Ti'].interface.range(1.0, 20.0)
sample['Cu'].thickness.range(10.0, 800.0)
sample['Cu'].interface.range(8.0, 15.0)
sample['material'].thickness.range(15.0, 100.0)
sample['material'].material.rho.range(-3.0, 8.0)
sample['material'].interface.range(1.0, 35.0)
sample['SEI'].thickness.range(100.0, 300.0)
sample['SEI'].material.rho.range(3.0, 4.3)
sample['SEI'].interface.range(5.0, 25.0)



probe.intensity=Parameter(value=1.038,name='normalization')
probe.background.range(0.0, 1e-05)
sample['THF'].interface.range(25.0, 150.0)

################################################################################

expt = Experiment(probe=probe, sample=sample)
problem = FitProblem(expt)
