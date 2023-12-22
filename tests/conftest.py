# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Module with test fixtures."""
from __future__ import annotations

import collections
import pathlib

import pytest
from aiida.common.folders import Folder
from aiida.common.links import LinkType
from aiida.engine.utils import instantiate_process
from aiida.manage.manager import get_manager
from aiida.orm import CalcJobNode, FolderData, StructureData, TrajectoryData
from aiida.plugins import ParserFactory
from ase.build import bulk

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]  # pylint: disable=invalid-name


@pytest.fixture
def filepath_tests() -> pathlib.Path:
    """Return the path to the tests folder."""
    return pathlib.Path(__file__).resolve().parent


@pytest.fixture
def generate_calc_job(tmp_path):
    """Return a factory to generate a :class:`aiida.engine.CalcJob` instance with the given inputs.

    The fixture will call ``prepare_for_submission`` and return a tuple of the temporary folder that was passed to it,
    as well as the ``CalcInfo`` instance that it returned.
    """

    def factory(process_class, inputs=None, return_process=False):
        """Create a :class:`aiida.engine.CalcJob` instance with the given inputs."""
        manager = get_manager()
        runner = manager.get_runner()
        process = instantiate_process(runner, process_class, **inputs or {})
        calc_info = process.prepare_for_submission(Folder(tmp_path))

        if return_process:
            return process

        return tmp_path, calc_info

    return factory


@pytest.fixture
def generate_calc_job_node(filepath_tests, aiida_localhost, tmp_path):
    """Create and return a :class:`aiida.orm.CalcJobNode` instance."""

    def flatten_inputs(inputs, prefix=""):
        """Flatten inputs recursively like :meth:`aiida.engine.processes.process::Process._flatten_inputs`."""
        flat_inputs = []
        for key, value in inputs.items():
            if isinstance(value, collections.abc.Mapping):
                flat_inputs.extend(flatten_inputs(value, prefix=prefix + key + "__"))
            else:
                flat_inputs.append((prefix + key, value))
        return flat_inputs

    def factory(
        entry_point: str,
        directory: str,
        test_name: str,
        inputs: dict = None,
        retrieve_temporary_list: list[str] | None = None,
    ):
        """Create and return a :class:`aiida.orm.CalcJobNode` instance."""
        node = CalcJobNode(
            computer=aiida_localhost, process_type=f"aiida.calculations:{entry_point}"
        )

        if inputs:
            for link_label, input_node in flatten_inputs(inputs):
                input_node.store()
                node.add_incoming(input_node, link_type=LinkType.INPUT_CALC, link_label=link_label)

        node.store()

        filepath_retrieved = filepath_tests / "parsers" / "fixtures" / directory / test_name

        retrieved = FolderData()
        retrieved.put_object_from_tree(filepath_retrieved)
        retrieved.add_incoming(node, link_type=LinkType.CREATE, link_label="retrieved")
        retrieved.store()

        if retrieve_temporary_list:
            for pattern in retrieve_temporary_list:
                for filename in filepath_retrieved.glob(pattern):
                    filepath = tmp_path / filename.relative_to(filepath_retrieved)
                    filepath.write_bytes(filename.read_bytes())

            return node, tmp_path

        return node

    return factory


@pytest.fixture(scope="session")
def generate_parser():
    """Fixture to load a parser class for testing parsers."""

    def factory(entry_point_name):
        """Fixture to load a parser class for testing parsers.

        :param entry_point_name: entry point name of the parser class
        :return: the `Parser` sub class
        """
        return ParserFactory(entry_point_name)

    return factory


@pytest.fixture
def generate_structure():
    """Return factory to generate a ``StructureData`` instance."""

    def factory(formula: str = "Si") -> StructureData:
        """Generate a ``StructureData`` instance."""
        atoms = bulk(formula)
        return StructureData(ase=atoms)

    return factory


@pytest.fixture
def generate_trajectory(generate_structure):
    """Return factory to generate a ``TrajectoryData`` instance."""

    def factory(formula: str = "Si") -> TrajectoryData:
        """Generate a ``TrajectoryData`` instance."""
        return TrajectoryData(structurelist=[generate_structure(formula=formula)])

    return factory
