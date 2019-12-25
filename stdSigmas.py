from basf2 import B2ERROR
import modularAnalysis as ma

from stdPi0s import stdPi0s
from stdCharged import stdPr
from stdPhotons import stdPhotons

def stdSigmas(listtype = 'std', gammatype = 'pi0eff50', path = None):
    """
    Load standard ``Sigma+`` reconstructed from ``Sigma+ -> p+ [pi0 -> gamma gamma]```.
    The ``pi0`` is reconstructed using the specified gamma list and ``pi0``s in mass range
    ``100 ~ 160 MeV`` are combined the with protons from ``p+:loose`` list to form a ``Sigma+``.
    
    Tree fitter is used for the vertex fit with IP constraint and mass constraint on the ``pi0``.
    
    The particle list is named ``Sigma+:std`` with mass range ``1.66 ~ 1.22 GeV``.
    
    Parameters:
        gamma_type (str): the gamma list to use
        path (basf2.path): path to load the particle list
    """
  
    stdPhotons(gammatype, path = path)
    stdPr('loose', path = path)
    ma.reconstructDecay(f'pi0:for_sigma -> gamma:{gammatype} gamma:{gammatype}', '0.1 < M < 0.16', path = path)
    ma.reconstructDecay('Sigma+:std -> p+:loose pi0:for_sigma', '1.1 < M < 1.3', path = path)
    ma.vertexTree('Sigma+:std', 0, ipConstraint = True, massConstraint = [111], 
                   updateAllDaughters = False, path = path)
    ma.applyCuts('Sigma+:std', '1.16 < M < 1.22', path = path)

    if listtype == 'std':
        pass
    elif listtype == 'loose':
        vtx_cuts = 'cosaXY > 0.99 and dr > 0.12 and abs(dz) > 0.1 and chiProb > 0.001'
        ma.cutAndCopyList('Sigma+:loose', 'Sigma+:std', vtx_cuts, path = path)
    else:
        B2ERROR(f'stdSigmas: Invalid listtype ({listtype}. Choose from std, loose.')