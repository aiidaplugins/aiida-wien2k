#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test workflow WIEN2k Si
"""
import os
import WIEN2k
from aiida.engine import calcfunction, workfunction
from aiida.orm import Dict
from ase.spacegroup import crystal

@calcfunction
def init_WIEN2k(inputdict):
    # initialize WIEN2k calculation
    execstring="init_lapw -b "
    print("inputdict=",inputdict)
    for key,value in inputdict.get_dict().items():
        execstring += " -"+key+" "+str(value)
    os.system(execstring)

@calcfunction
def run_WIEN2k(inputdict):
    # run WIEN2k SCF
    execstring="run_lapw "
    for key,value in inputdict.get_dict().items():
        execstring += " -"+key+" "+str(value)
    os.system(execstring)

@calcfunction
def res_WIEN2k():
    # process results
    res = Dict()
    enelist = WIEN2k.grep(":ENE") # get all energies in SCF run
    res['EtotRyd'] = enelist[-1] # store last one
    vollist = WIEN2k.grep(":VOL") # get all volumes in SCF run
    res['VolBohr3'] = vollist[-1] # store last one
    return res # stored automatically in AiiDA database

@workfunction
def fw_WIEN2k(initdic,rundic):
    # initialize WIEN2k SCF calculation
    init_WIEN2k(inputdict=initdic)
    # run WIEN2k SCF
    run_WIEN2k(inputdict=rundic)
    # read results (Etot, Vol) and return as a dictionary
    res = res_WIEN2k()
    return res # stored automatically in AiiDA database
    
# Setup structure in ASE internal format (later need to do it in CrystalData)
# TODO: store structure in AiiDA database
Si = crystal('Si', [(0, 0, 0)], spacegroup=227,\
             cellpar=[5.43, 5.43, 5.43, 90, 90, 90])
print("Si=",Si)
# write case.struct file
WIEN2k.writestruct(Si,sgroup=True)
# prep WIEN2k init parameters as AiiDA dictionary
W2Kinit = Dict()
W2Kinit['vxc'] = 13
W2Kinit['numk'] = 1000
W2Kinit.store() # store in AiiDA database
# prep WIEN2k init parameters as AiiDA dictionary
W2Krun = Dict()
W2Krun['ec'] = 0.0001
W2Krun['cc'] = 0.001
W2Krun.store() # store in AiiDA database
# call WIEN2k workflow
W2Kres = fw_WIEN2k(initdic=W2Kinit,rundic=W2Krun)
# print results
print(W2Kres.get_dict())