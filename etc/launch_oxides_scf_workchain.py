from aiida.engine import submit
from aiida import orm
from aiida_wien2k.workflows.scf_workchain import Wien2kScfWorkChain
import time
from aiida.plugins.factories import WorkflowFactory
from aiida.orm import QueryBuilder

def count_running_wchains():
    """
    Count number of running workchains with a given entry point

    Return:
    count (int) - number of workchains still running (status=waiting) 
    """
    workchain_entry_point = 'wien2k.scf_wf'
    Wien2kScfWorkChain = WorkflowFactory(workchain_entry_point)
    query = QueryBuilder()
    query.append(Wien2kScfWorkChain) # serach workflows that match workchain_entry_point
    query.all()
    count = 0
    for node in query.iterall():
        if(node[0].process_state.value == 'waiting'):
            count = count + 1 # count all waiting processes

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

elements = [
        'Si', 
        'Al', 
        'Fe', 
        'Eu'
]
configurations = ['X2O', 'XO', 'X2O3', 'X2O5', 'XO2', 'XO3']
#configurations = ['XO3']
nprocmax = 12
for node in Group.get(label='commonwf-oxides/set1/structures').nodes:
    element = list(node.extras.values())[1] # chemical element X
    configuration = list(node.extras.values())[2] # X2O, XO2, etc.
    if ( (element in elements) and (configuration in configurations) ):
        aiida_structure = node # get structure of SiO2
        print(node.extras) # info about chem. composition

        # run SCF workchain
        code1 = orm.load_code(label='wien2k-x-sgroup@localhost')
        code2 = orm.load_code(label='wien2k-init_lapw@localhost')
        code3 = orm.load_code(label='wien2k-run_lapw@localhost')
        inpdict1 = orm.Dict(dict={}) # x sgroup [param]
        inpdict2 = orm.Dict(dict={'-red':'3', '-prec':'2n', '-hdlo':True, '-fermit':'0.002'}) # init_lapw -b [param]
        inpdict3 = orm.Dict(dict={'-i':'100', '-ec':'0.0001', '-cc':'0.001'}) # run_lapw [param]
        result = submit(Wien2kScfWorkChain, aiida_structure=aiida_structure,\
                code1=code1, code2=code2, code3=code3, inpdict1=inpdict1,\
                inpdict2=inpdict2, inpdict3=inpdict3)
        print('result=', result)
        wait_to_limit_nproc(nprocmax, timeinterval=30) # limit number of concurent processes
