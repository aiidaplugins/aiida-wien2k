# -*- coding: utf-8 -*-
from aiida_common_workflows.workflows.relax.wien2k import Wien2kCommonRelaxWorkChain

inputgen = Wien2kCommonRelaxWorkChain.get_input_generator()
from aiida.engine import run, submit

builder = inputgen.get_builder(
    structure=load_node(73739), engines={"relax": {"code": "wien2k-run123_lapw@localhost"}}
)
run(builder)
