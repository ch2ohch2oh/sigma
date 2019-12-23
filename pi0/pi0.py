import basf2 as b2
import modularAnalysis as ma

import glob
import sys

from stdPi0s import stdPi0s
from stdCharged import stdPr
from stdPhotons import stdPhotons

from variables import variables as va
from variables.utils import create_aliases_for_selected

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
        outfile = 'pi0_2.root'
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2]
    print(f"Input = {infile}")
    print(f"Output = {outfile}")
    
    ma.inputMdstList('default', [infile], path = mp)

    stdPhotons('all', path = mp)
    ma.reconstructDecay('pi0:all -> gamma:all gamma:all', '0.1 < M < 0.17', path = mp)
#     ma.vertexTree('pi0:all', 0, ipConstraint = True, massConstraint = [111], path = mp)
    ma.matchMCTruth('pi0:all', path = mp)
    ntuple = ['M', 'p', 'mcP', 'isSignal']
    ma.variablesToNtuple('pi0:all', ntuple, treename = 'pi0_all', filename = outfile, path = mp)
    
    for eff in [20, 30, 40, 50, 60]:
        stdPhotons(f'pi0eff{eff}', path = mp)
        ma.reconstructDecay(f'pi0:pi0eff{eff} -> gamma:pi0eff{eff} gamma:pi0eff{eff}', '0.1 < M < 0.17', path = mp)
#         ma.vertexTree(f'pi0:pi0eff{eff}', 0, ipConstraint = True, massConstraint = [111], path = mp)
        ma.matchMCTruth(f'pi0:pi0eff{eff}', path = mp)
        ma.variablesToNtuple(f'pi0:pi0eff{eff}', ntuple, treename = f'pi0_eff{eff}', filename = outfile, path = mp)

    b2.process(path = mp)
    print(b2.statistics)