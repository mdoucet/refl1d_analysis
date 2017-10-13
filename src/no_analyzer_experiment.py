#pylint: disable=invalid-name, multiple-statements, protected-access
"""
    Experiment class for the case where we have a polarized beam without a spin analyzer.
    In this case we are measuring two reflectivity curves: (++ and +-) and (-+ and --).

    To use this Experiment class, modify your refl1d model by importing the following:

        import sys
        sys.path.append("location of this file")

        from no_analyzer_experiment import Experiment as NoAnalyzerExperiment

    Additionally, you'll need to pass the probe objects twice, as follows:

        probe = PolarizedNeutronProbe([pp, pp, mm,mm], Aguide=270)
        expt = NoAnalyzerExperiment(probe=probe, sample=sample,dz=1.0)

"""
from __future__ import absolute_import, division, print_function
from refl1d.names import *
import refl1d.experiment
import numpy as np

class Experiment(refl1d.experiment.Experiment):
    """

        From the original code, we have the following options:

        _polarized_nonmagnetic() returns four cross sections filled with
           nuclear reflectivity in non-spin flip and zero in spin flip.

        _polarized_magnetic() returns a sum of all four cross sections.

        The order of the cross sections is: pp, pm, mp and mm

    """
    def residuals(self):
        """
            Compute the residuals.
        """
        if 'residuals' not in self._cache:
            if ((self.probe.polarized
                 and all(x is None or x.R is None for x in self.probe.xs))
                or (not self.probe.polarized and self.probe.R is None)):
                resid = numpy.zeros(0)
            else:
                QR = self.reflectivity()
                if self.probe.polarized:
                    resid = numpy.hstack([(self.probe.xs[0].R - QR[0][1])/self.probe.xs[0].dR,
                                          (self.probe.xs[3].R - QR[3][1])/self.probe.xs[3].dR])
                else:
                    resid = (self.probe.R - QR[1])/self.probe.dR
            self._cache['residuals'] = resid

        return self._cache['residuals']

    def reflectivity(self, resolution=True, interpolation=0):
        """
        Calculate predicted reflectivity.
        If *resolution* is true include resolution effects.

        This is a copy of the original code, where we added
        the option of turning off the spin analyzer.
        """
        key = ('reflectivity', resolution, interpolation)
        if key not in self._cache:
            Q, r = self._reflamp()
            R = _amplitude_to_magnitude(r,
                                        ismagnetic=self.ismagnetic,
                                        polarized=self.probe.polarized,
                                        has_analyzer=False)
            res = self.probe.apply_beam(Q, R, resolution=resolution,
                                        interpolation=interpolation)
            self._cache[key] = res
        return self._cache[key]


def _half_polarized_magnetic(R):
    """
        From the four cross-sections, we produce the sum of ++ and +-,
        and the sum of -+ and -- since those are the reflectivity curves
        we measure.
        Since refl1d needs the four cross-sections and the entries can't
        be None, we leave the spin-flip cross-sections untouched. They will
        not be used for residual calculations and will need to be ignored later.
    """
    return [np.add(R[0], R[1]), R[1], R[2], np.add(R[2], R[3])]

def _amplitude_to_magnitude(r, ismagnetic, polarized, has_analyzer=True):
    """
        Compute the reflectivity magnitude.
        This is a copy of the method in the original code, with the
        added option of not having a spin analyzer.

        :param bool ismagnetic: True is the model has magnetic layers
        :param bool polarized: True if polarizers are involved
        :param book has_analyzer: True if
    """
    if ismagnetic:
        R = [abs(xs)**2 for xs in r]
        if not polarized: R = refl1d.experiment._nonpolarized_magnetic(R)
        elif not has_analyzer: R = _half_polarized_magnetic(R)
    else:
        R = abs(r)**2
        if polarized: R = refl1d.experiment._polarized_nonmagnetic(R)
    return R
