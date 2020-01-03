import basf2 as b2
import modularAnalysis as ma
import b2biiConversion as b2c
import b2biiMonitors as b2m

import glob
import sys

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
    if len(sys.argv) == 1:
        infile = '/group/belle/bdata_b/dstprod/dat/e000055/HadronBJ/0127/on_resonance/00/HadronBJ-e000055r000003-b20090127_0910.mdst'
        outfile = 'sigma_std_belle.root'
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2]
    
    print(f"Input = {infile}")
    print(f"Output = {outfile}")
    
    b2c.setupB2BIIDatabase(isMC = True)
        
    print_env()
    
    mp = b2.create_path()
    b2c.convertBelleMdstToBelleIIMdst(infile, path = mp)
    
    va.addAlias('cosa', 'cosAngleBetweenMomentumAndVertexVector')
    va.addAlias('cosaXY', 'cosAngleBetweenMomentumAndVertexVectorInXYPlane')
    va.addAlias('abs_dM', 'abs(dM)')
    va.addAlias('abs_dr', 'abs(dr)')
    va.addAlias('pid_ppi', 'atcPIDBelle(4,2)')
    va.addAlias('pid_pk', 'atcPIDBelle(4,3)')
    va.addAlias('pid_kpi', 'atcPIDBelle(3,2)')
    va.addAlias('ppi0_angle', 'daughterAngle(0, 1)')
    va.addAlias('p_decayAngle', 'decayAngle(0)')
    va.addAlias('pi0_decayAngle', 'decayAngle(1)')
    
    ma.fillParticleList('p+:good', 'pid_ppi > 0.6 and pid_pk > 0.6', path = mp)
#     ma.vertexTree('pi0:mdst', ipConstraint = True, massConstraint = ['pi0'], path = mp)
    ma.reconstructDecay('Sigma+:std -> p+:good pi0:mdst', '1.1 < M < 1.3', path = mp)
    ma.vertexTree('Sigma+:std', 0, ipConstraint = True, updateAllDaughters = True, path = mp)
    # Select good pi0 based on mass and gamma energy
    ma.applyCuts('Sigma+:std', 'daughter(1, daughter(0, E)) > 0.04 and daughter(1, daughter(1, E)) > 0.04 and daughter(1, abs(dM)) < 0.2', path = mp)
    ma.vertexTree('Sigma+:std', 0, ipConstraint = True, massConstraint = ['pi0'], path = mp)
    # 100 MeV mass window for Sigma+ should be large enough
    ma.applyCuts('Sigma+:std', 'cosaXY > 0 and daughter(1, p) > 0.1 and 1.14 < M < 1.24', path = mp)
    ma.matchMCTruth('Sigma+:std', path = mp)
    
    ntuple = ['M', 'p', 'chiProb', 'cosa', 'cosaXY', 'dr', 'dz', 'distance', 'isSignal', 'genMotherPDG']
    ntuple += ['ppi0_angle', 'p_decayAngle', 'pi0_decayAngle']
    ntuple += ['IPX', 'IPY', 'IPZ']
    
    ntuple += create_aliases_for_selected(['pid_ppi', 'pid_pk', 'pid_kpi', 'dr', 'dz', 'p', 'isSignal'],
                                          'Sigma+ -> ^p+ pi0', prefix = ['p'])
    ntuple += create_aliases_for_selected(['mcP', 'p', 'M', 'distance', 'isSignal', 'genMotherPDG'],
                                          'Sigma+ -> p+ ^pi0', prefix = ['pi0'])
    ntuple += create_aliases_for_selected(['E', 'theta', 'phi'],
                                          'Sigma+ -> p+ [pi0 -> ^gamma ^gamma]', prefix = ['gamma1', 'gamma2'])
    
    ma.variablesToNtuple('Sigma+:std', ntuple, treename = 'sigma_std', filename = outfile, path = mp)
    
    ma.fillParticleListFromMC('Sigma+:gen', '', path = mp)
    ma.variablesToNtuple('Sigma+:gen', ['distance', 'p', 'M'], treename = 'sigma_gen', filename = outfile, path = mp)
    
    b2.process(path = mp)
    print(b2.statistics)