# -*- coding: utf-8 -*-
from aiida.engine import submit
from aiida_common_workflows.workflows.eos import EquationOfStateWorkChain
from aiida_common_workflows.workflows.relax.generator import ElectronicType, RelaxType

structure = load_node(73739)
engines = {"relax": {"code": "wien2k-run123_lapw@localhost"}}
inputs = {
    "structure": structure,
    "generator_inputs": {
        "engines": engines,
        "protocol": "moderate",
        "relax_type": RelaxType.NONE,
        "electronic_type": ElectronicType.METAL,
    },
    "sub_process_class": "common_workflows.relax.wien2k",
}
submit(EquationOfStateWorkChain, **inputs)
