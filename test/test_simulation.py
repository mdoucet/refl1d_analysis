from __future__ import absolute_import, division, print_function
from refl1d.names import *

import numpy as np

def make_sample():
    Al2O3            = SLD(name="Al2O3",             rho=5.74,  irho=0.0)   
    Cr2O3            = SLD(name="Cr2O3",             rho=5.11,  irho=0.0)   
    Sb194Cr006Te300  = SLD(name="Sb194Cr006Te300",   rho=1.76,  irho=0.0)   
    Te               = SLD(name="Te",                rho=1.673, irho=0.0)   

    sample = Al2O3(0, 1.0) 
    sample = sample | Cr2O3(200 ,1.0)
    sample = sample | MagneticSlab(Sb194Cr006Te300(50.0, 1.0), rhoM=0.1, thetaM=270)
    sample = sample | Te(100.0, 0.1)
    sample = sample | air

    return sample


def make_experiment(sample, q_min=0, q_max=0.2, npoints=200):
    L=4.75
    dL=0.0475
    dT=0.01
    T = np.linspace(np.degrees(np.arcsin(q_min*L/4.0/np.pi)), np.degrees(np.arcsin(q_max*L/4.0/np.pi)), npoints)
    xs = [NeutronProbe(T=T, dT=dT, L=L, dL=dL) for _ in range(4)]
    probe = PolarizedNeutronProbe(xs)
    expt = Experiment(probe=probe, sample=sample, dz=0.1)
    return expt


def generate_data(expt, relative_err_min=5.0, relative_err_max=10.0):

    expt.simulate_data(noise=0)

    if isinstance(expt.probe, PolarizedNeutronProbe):
        for _xs in expt.probe.xs:
            indices = np.arange(len(_xs.R))
            _xs.dR = (relative_err_min + (relative_err_max - relative_err_min) / len(_xs.R) * indices) * _xs.R / 100.0
    else:
        indices = np.arange(len(expt.probe.R))
        expt.probe.dR = (relative_err_min + (relative_err_max - relative_err_min) / len(expt.probe.R) * indices) * expt.probe.R / 100.0

    expt.resynth_data()

sample=make_sample()
expt = make_experiment(sample)
r_0 = expt.reflectivity()
print(np.asarray(r_0).shape)
generate_data(expt)

avg_err = (expt.probe.xs[0].R - r_0[0][0])**2

for i in range(100):
    _r = generate_data(expt)
    avg_err += (expt.probe.xs[0].R - r_0[0][0])**2


_std_dev = (np.sqrt(avg_err)/100.0)
print(_std_dev/r_0[0][0])