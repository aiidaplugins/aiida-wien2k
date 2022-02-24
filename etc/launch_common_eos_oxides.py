from aiida.engine import submit
import time
from aiida.plugins.factories import WorkflowFactory
from aiida.orm import QueryBuilder
from aiida.schedulers.datastructures import NodeNumberJobResource
from aiida_common_workflows.workflows.relax.generator import ElectronicType, RelaxType
from aiida.engine import submit
from aiida_common_workflows.workflows.eos import EquationOfStateWorkChain

def count_running_wchains():
    """
    Count number of running workchains with a given entry point

    Return:
    count (int) - number of workchains still running (status=waiting,created) 
    """
    workchain_entry_point = 'common_workflows.eos'
    WorkChain = WorkflowFactory(workchain_entry_point)
    query = QueryBuilder()
    query.append(WorkChain) # serach workflows that match workchain_entry_point
    query.all()
    count = 0
    for node in query.iterall():
        if((node[0].process_state.value == 'waiting') or\
                (node[0].process_state.value == 'created')):
            count = count + 1 # count all waiting processes
    print(f'Total of {count} {workchain_entry_point} workchains are waiting or created')

    return count # int

def wait_to_limit_nproc(nprocmax, timeinterval):
    """
    Check number of workchains running and compare to 'nprocmax'
    If the number of greater than 'nprocmax', wait 'timeinterval' sec 
    and check again. Othervise - return
    """
    time.sleep(15) # Delay for 15 second
    while( count_running_wchains()>=nprocmax ):
        time.sleep(timeinterval) # Delay for X seconds

    return

# Setting up crystal structure(s)
elements_all = ['H', \
        'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', \
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', \
        'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', \
        'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', \
        'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', \
            'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', \
        'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', \
            'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
#elements = elements_all[0:36] # H ... Kr
#elements = elements_all[36:65] # Rb ... Tb
#elements = elements_all[65: ] # Dy ... Og
#elements = ['Rb',] # custom
elements = elements_all
configurations = ['X2O', 'XO', 'X2O3', 'X2O5', 'XO2', 'XO3']
#configurations = ['XO3',] # custom
chemformulas_compleated = []
engines= {
    'relax': {
        'code': 'wien2k-run123_lapw@localhost'
    }
}
nprocmax = 15
res = NodeNumberJobResource(num_machines=1, num_mpiprocs_per_machine=1, num_cores_per_mpiproc=1) # set resources
counter = 0
for node in Group.get(label='commonwf-oxides/set2-bis/structures').nodes:
    aiida_structure = node # get structure of SiO2
    element = aiida_structure.extras['element'] # chemical element X
    configuration = aiida_structure.extras['configuration'] # X2O, XO2, etc.
    formula = element + '-' + configuration # H-XO3
    print(formula)
    if ( (element in elements) and (configuration in configurations) ):
        print(node.extras) # info about chem. composition
        chemformula = aiida_structure.get_formula()
        if (chemformula in chemformulas_compleated):
            continue # skip iteration
        # run common workflow EOS workchain
        inputs = {
            'structure': aiida_structure,
            'generator_inputs': {
                'engines': engines,
                'protocol': 'moderate',
                'relax_type': RelaxType.NONE,
                'electronic_type': ElectronicType.METAL,
            },
            'sub_process_class': 'common_workflows.relax.wien2k',
        }
        result = submit(EquationOfStateWorkChain,**inputs)
        print('result=', result)
        counter = counter+1
        print('counter=', counter)
        wait_to_limit_nproc(nprocmax, timeinterval=60) # limit number of concurent processes
