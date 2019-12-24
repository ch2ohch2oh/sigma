import basf2 as b2
import modularAnalysis as ma

import glob
import sys

from stdPi0s import stdPi0s
from stdCharged import stdPr
from stdPhotons import stdPhotons
from stdSigmas import stdSigmas
from variables import variables as va
from variables.utils import create_aliases_for_selected

import argparse

def print_env():
    """Print relevant env variables"""
    import os
    envlist = ['BELLE2_EXTERNALS_DIR', 'BELLE2_EXTERNALS_SUBSIR',
               'BELLE2_EXTERNALS_OPTION', 'BELLE2_EXTERNALS_VERSION',
               'BELLE2_LOCAL_DIR', 'BELLE2_OPTION', 'BELLE2_RELEASE', 
               'BELLE_POSTGRES_SERVER', 'USE_GRAND_REPROCESS_DATA',
               'PANTHER_TABLE_DIR', 'PGUSER']
    print('ENV START'.center(80, '='))
    for v in envlist:
        print("%30s = %s" % (v, os.getenv(v)))
    print('ENV END'.center(80, '='))
    
if __name__ == '__main__':
    
    mp = b2.create_path()
    
    print_env()
    
    if len(sys.argv) == 1:
        infile = '/ghi/fs01/belle2/bdata/MC/release-03-01-00/DB00000547/MC12b/prod00007426/s00/e1003/4S/r00000/ccbar/mdst/sub00'\
                 '/mdst_000001_prod00007426_task10020000001.root'
        outfile = 'test.root'
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2]
    
    print(f"Input = {infile}")
    print(f"Output = {outfile}")
    
    ma.inputMdstList('default', [infile], path = mp)

    eff = 60
    stdSigmas(f'pi0eff{eff}', path = mp)
    ma.matchMCTruth('Sigma+:std', path = mp)
    
    va.addAlias('cosa', 'cosAngleBetweenMomentumAndVertexVector')
    va.addAlias('cosaXY', 'cosAngleBetweenMomentumAndVertexVectorInXYPlane')
    va.addAlias('abs_dM', 'abs(dM)')
    va.addAlias('M_noupdate', 'extraInfo(M_noupdate)')
    va.addAlias('p_noupdate', 'extraInfo(p_noupdate)')
    
    ntuple = ['M', 'p', 'chiProb', 'cosa', 'cosaXY', 'dr', 'dz', 'distance', 'isSignal', 'genMotherPDG']
    ntuple += ['IPX', 'IPY', 'IPZ']
    ntuple += create_aliases_for_selected(['protonID', 'pionID', 'dr', 'dz', 'p', 'isSignal'],
                                          'Sigma+ -> ^p+ pi0', prefix = ['p'])
    ntuple += create_aliases_for_selected(['mcP', 'p', 'M', 'distance', 'isSignal', 'genMotherPDG', 'M_noupdate', 'p_noupdate'],
                                          'Sigma+ -> p+ ^pi0', prefix = ['pi0'])
    
    ma.variablesToNtuple('Sigma+:std', ntuple, treename = f'sigma_eff{eff}', filename = outfile, path = mp)
    
    ma.fillParticleListFromMC('Sigma+:gen', '', path = mp)
    ma.variablesToNtuple('Sigma+:gen', ['cosa', 'cosaXY', 'p', 'M'], treename = 'sigma_gen', filename = outfile, path = mp)
    
    b2.process(path = mp)
    print(b2.statistics)