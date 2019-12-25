#!/usr/bin/env python3

import os
import sys
import glob
from tqdm import tqdm
import logging
import multiprocessing as mpl
import time
import shutil
from termcolor import colored

data_dict = {
    8: ['4S', 'Continuum', 'Scan']
}

skim = 'hlt_hadron'
filetype = 'mdst'

def get_data(proc = 'proc9', exp = 8, datatype = 'Continuum', skim = 'hlt_hadron', filetype = 'mdst', verbose = 1):
    """
    Get list of root files for real data on KEK.
    """
    if proc == 'proc9':
        basedir = '/group/belle2/dataprod/Data/release-03-02-02/DB00000654/proc9'
        goodruns = glob.glob(os.path.join(basedir, "e%04d" % exp, datatype, 'GoodRuns', '*'))
        goodcount = len(goodruns)
        files = []
        for run in goodruns:
            files += glob.glob(os.path.join(run, 'skim', skim, filetype, 'sub00', '*.root'))
    else:
        raise Exception(f'Invalid data reprocessing {proc}')
    
    logging.info(f"proc = {proc} exp = {exp} datatype = {datatype} skim = {skim} filetype = {filetype}")
    logging.info(f'number of good runs = {len(goodruns)}')
    logging.info(f"number of root files in the list = {len(files)}")
    return files
    

def create_dir(path):
    """
    Create an directory. If the given directory already exists then will clear this directory
    per user request.
    """
    if os.path.isdir(path) and len(os.listdir(path)) > 0:
        choice = input('Output dir not empty. Clear or not? [y/n] ').strip().lower()
        if choice == '' or choice.startswith('y'):
            logging.info(f'Clearing the contents of {path}')
            shutil.rmtree(path)
    os.makedirs(path, exist_ok = True)

def create_jobs(outdir, script, infiles, q = 's', b2opt = ''):
    """
    Create bsub job submission cmd lines based on input files.
    
    Returns:
        A list of bsubs commands to be ran (using multiprocessing)
    """
    cmdlist = []
    for infile in files:
        base = os.path.basename(infile)
        logfile = os.path.join(outdir, base + '.log')
        outfile = os.path.join(outdir, 'ntuple.' + base)
        cmdlist += [f'bsub -q s -oo {logfile} basf2 {b2opt} {script} {infile} {outfile} >> bsub.log']

    logging.info(f"{len(cmdlist)} jobs created")
    logging.info(f"The first job: {cmdlist[0]}")
    return cmdlist

def fake_system(*args, **kwargs):
    """
    A fake os.system to test multiprocessing job submission.
    """
    time.sleep(1)
    return 0

def submit_jobs(cmdlist, nworkers = 8):
    """
    Submit all jobs in cmdlist in parallel using multiprocessing
    """
    pool = mpl.Pool(processes = nworkers)
    
    logging.info(f"{len(cmdlist)} jobs to submit")
    logging.info(f'Started to submit jobs with {nworkers} workers')
    
    bar = tqdm(total = len(cmdlist))
    results = []

    def log_result(result):
        results.append(result)
        bar.update()
    
    for cmd in cmdlist:
        pool.apply_async(os.system, [cmd], callback = log_result)
    pool.close()
    pool.join()
    
    logging.debug('Checking for failed jobs submission...')
    assert len(results) == len(cmdlist)
    failed = []
    for i in range(len(results)):
        if results[i] != 0:
            failed += cmdlist[i]
    if len(failed) == 0:
        logging.info(colored(f"{len(failed)} failed submission", 'green'))
    else:
        logging.info(colored(f"{len(failed)} failed submission", 'red'))
    if len(failed) > 0:
        logging.warning(f"The first failed submission: {failed[0]}")
    

if __name__ == '__main__':
    
    logging.basicConfig(format = '[%(levelname)s] %(funcName)s: %(message)s', level = logging.DEBUG, stream = sys.stdout)

    outdir = 'sigma_exp8_4S'
    script = 'test_stdSigmas_data.py'


    print(f'Output dir: {outdir}')
    print(f'Script: {script}')
    
    create_dir(outdir)
    
    assert os.path.exists(outdir), "Output dir does not exist!"
    assert os.path.exists(script), "The given script does not exists!"
    
    files = get_data(proc = 'proc9', exp = 8, datatype = '4S')
    
    cmdlist = create_jobs(outdir, script, files)
    
    submit_jobs(cmdlist)
    limit = 10
