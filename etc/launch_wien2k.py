# -*- coding: utf-8 -*-
"""Launch a calculation using the 'diff-tutorial' plugin"""
from pathlib import Path
from aiida import orm, engine
from aiida.common.exceptions import NotExistent
import ase.io
from ase.spacegroup import crystal
import os
from aiida.engine import calcfunction

@calcfunction
def aiida_struct2wien2k(aiida_structure):
    "prepare structure file for WIEN2k"
    ase_structure = aiida_structure.get_ase() # AiiDA -> ASE struct
    ase.io.write("case.struct",ase_structure) # ASE -> WIEN2k, write WIEN2k struct
    path_to_rm_folder = Path(__file__).resolve().parent # get path to folder
    path_to_rm_structfile = os.path.join(path_to_rm_folder, 'case.struct') # get path to struct file
    wien2k_structfile = orm.SinglefileData(file=path_to_rm_structfile) # get proper AiiDA type for a single file (otherwise you cannot return)
    return wien2k_structfile # orm.SinglefileData type (stored automatically in AiiDA database)

# Setting up crystal structure

# ASE structure
ase_structure = crystal('Si', [(0, 0, 0)], spacegroup=227,\
        cellpar=[5.43, 5.43, 5.43, 90, 90, 90])
# ASE -> AiiDA structure
aiida_structure = orm.StructureData(ase=ase_structure)
# Convert AiiDA structure to WIEN2k format
wien2k_structfile = aiida_struct2wien2k(aiida_structure)

# Load code@computer
computer = orm.load_computer('localhost')
code = orm.load_code(label='wien2k-x-sgroup@localhost')

# Set up inputs
builder1 = code.get_builder()
builder1.structfile_in = wien2k_structfile
builder1.parameters = orm.Dict(dict={}) # no additional arguments
builder1.metadata.description = 'run x sgroup'

# Run the calculation
result1 = engine.run(builder1)
print("result1=",result1)
print("work dir =", result1.get('remote_folder').get_attribute('remote_path'))
print("retrieved files=",result1.get('retrieved').list_object_names())
print('--')

# Load code@computer
computer = orm.load_computer('localhost')
code = orm.load_code(label='wien2k-init_lapw@localhost')

# Set up inputs
builder2 = code.get_builder()
builder2.structfile = result1.get('structfile_out') # pass structure from x sgroup
builder2.parameters = orm.Dict(dict={'-numk': '700'}) # total number of k-points
builder2.metadata.description = 'run init_lapw'

# Run the calculation
result2 = engine.run(builder2)
print("result2=",result2)
print("work dir =", result2.get('remote_folder').get_attribute('remote_path')) # pass previous calculation folder
print("retrieved files=",result2.get('retrieved').list_object_names())
print('--')

# Load code@computer
computer = orm.load_computer('localhost')
code = orm.load_code(label='wien2k-run_lapw@localhost')

# Set up inputs
builder3 = code.get_builder()
builder3.parent_folder = result2.get('remote_folder') # pass previous calculation folder
builder3.parameters = orm.Dict(dict={'-i': '1'}) # only 1 SCF iteration
builder3.metadata.description = 'run run_lapw'

# Run the calculation
result3 = engine.run(builder3)
print("result3=",result3)
print("work dir =", result3.get('remote_folder').get_attribute('remote_path'))
print("retrieved files=",result3.get('retrieved').list_object_names())
print(result3.get('scf_grep').get_dict())
print('--')