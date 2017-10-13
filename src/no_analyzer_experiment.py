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
                    #resid = numpy.hstack([(xs.R - QRi[1])/xs.dR
                    #                      for xs,QRi in zip(self.probe.xs, QR)
                    #                      if xs is not None and QRi is not None])
                else:
                    resid = (self.probe.R - QR[1])/self.probe.dR
            self._cache['residuals'] = resid
 
        return self._cache['residuals']
        
    def reflectivity(self, resolution=True, interpolation=0):
        """
        Calculate predicted reflectivity.
        If *resolution* is true include resolution effects.
        """
        key = ('reflectivity', resolution, interpolation)
        if key not in self._cache:
            Q, r = self._reflamp()
            R = _amplitude_to_magnitude(r,
                                        ismagnetic=self.ismagnetic,
                                        polarized=self.probe.polarized,
                                        has_analyzer_flipper=False)
            res = self.probe.apply_beam(Q, R, resolution=resolution,
                                        interpolation=interpolation)
            self._cache[key] = res
        return self._cache[key]


def _half_polarized_magnetic(R):
    return [np.add(R[0], R[1]), R[1], R[2], np.add(R[2], R[3])]

def _amplitude_to_magnitude(r, ismagnetic, polarized, has_analyzer_flipper=True):
    """
    Compute the reflectivity magnitude
    """
    if ismagnetic:
        R = [abs(xs)**2 for xs in r]
        if not polarized: R = _nonpolarized_magnetic(R)
        elif not has_analyzer_flipper: R = _half_polarized_magnetic(R)
    else:
        R = abs(r)**2
        if polarized: R = _polarized_nonmagnetic(R)
    return R

