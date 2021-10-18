from aiida_common_workflows.workflows.relax.generator import ElectronicType, RelaxType
from aiida.engine import submit
from aiida_common_workflows.workflows.eos import EquationOfStateWorkChain

structure = load_node(255)
engines= {
    'x-sgroup': {
        'code': 'wien2k-x-sgroup@localhost'
    },
    'init_lapw': {
        'code': 'wien2k-init_lapw@localhost'
    },
    'relax': {
        'code': 'wien2k-run_lapw@localhost'
    }
}
inputs = {
    'structure': structure,
    'generator_inputs': {
        'engines': engines,
        'protocol': 'moderate',
        'relax_type': RelaxType.NONE,
        'electronic_type': ElectronicType.METAL,
    },
    'sub_process_class': 'common_workflows.relax.wien2k',
}
submit(EquationOfStateWorkChain,**inputs)