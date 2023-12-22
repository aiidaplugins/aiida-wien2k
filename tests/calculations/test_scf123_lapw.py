"""Tests for the :mod:`aiida_wien2k.calculations.run123_lapw` module."""
from __future__ import annotations

import io
import typing as t

import pytest
from aiida.orm import Dict, SinglefileData
from aiida_wien2k.calculations.run123_lapw import Wien2kRun123Lapw


def recursive_merge(left: dict[t.Any, t.Any], right: dict[t.Any, t.Any]) -> None:
    """Recursively merge the ``right`` dictionary into the ``left`` dictionary.

    :param left: Base dictionary.
    :param right: Dictionary to recurisvely merge on top of ``left`` dictionary.
    """
    for key, value in right.items():
        if key in left and isinstance(left[key], dict) and isinstance(value, dict):
            recursive_merge(left[key], value)
        else:
            left[key] = value


@pytest.fixture
def generate_inputs(aiida_local_code_factory, generate_structure):
    """Return a dictionary of inputs for the ``Wien2kRun123Lapw`."""

    def factory(**kwargs):
        parameters = {}
        recursive_merge(parameters, kwargs.pop('parameters', {}))

        inputs = {
            'code': aiida_local_code_factory('wien2k-run123_lapw', '/bin/true'),
            'aiida_structure': generate_structure(),
            'parameters': Dict(dict=parameters),
            'metadata': {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1}}},
        }
        inputs.update(**kwargs)
        return inputs

    return factory


def test_default_structure(generate_calc_job, generate_inputs):
    """Test the plugin for default inputs with structure as ``StructureData``."""
    inputs = generate_inputs()
    _, calc_info = generate_calc_job(Wien2kRun123Lapw, inputs=inputs)

    assert calc_info.remote_copy_list == []
    assert sorted(calc_info.retrieve_list) == sorted(
        [
            ('case/*.scf0'),
            ('case/*.scf1'),
            ('case/*.scf2'),
            ('case/*.scfm'),
            ('case/*.scfc'),
            ('case/*.error*'),
            ('case/*.dayfile'),
            ('case/*.klist'),
            ('case/*.in0'),
            ('case/case.struct'),
        ]
    )

    assert len(calc_info.local_copy_list) == 1
    assert calc_info.local_copy_list[0][-1] == 'case/case.struct'


def test_default_singlefile(generate_calc_job, generate_inputs):
    """Test the plugin for default inputs with structure as ``SinglefileData``."""
    structure = SinglefileData(io.BytesIO(b'content'), filename='structure.wien2k').store()
    inputs = generate_inputs()
    inputs.pop('aiida_structure')
    inputs['wien2k_structure'] = structure
    _, calc_info = generate_calc_job(Wien2kRun123Lapw, inputs=inputs)

    assert calc_info.remote_copy_list == []
    assert sorted(calc_info.retrieve_list) == sorted(
        [
            ('case/*.scf0'),
            ('case/*.scf1'),
            ('case/*.scf2'),
            ('case/*.scfm'),
            ('case/*.scfc'),
            ('case/*.error*'),
            ('case/*.dayfile'),
            ('case/*.klist'),
            ('case/*.in0'),
            ('case/case.struct'),
        ]
    )

    assert len(calc_info.local_copy_list) == 1
    assert calc_info.local_copy_list[0] == (structure.uuid, 'structure.wien2k', 'case/case.struct')


def test_parameters(generate_calc_job, generate_inputs):
    """Test the ``parameters`` input."""
    parameters = {'-i': '100', '-p': True}
    inputs = generate_inputs(parameters=parameters)
    _, calc_info = generate_calc_job(Wien2kRun123Lapw, inputs=inputs)

    assert calc_info.codes_info[0].cmdline_params == ['-i', '100', '-p']
