"""Tests for the :mod:`aiida_wien2k.parsers.scf123` module."""
from aiida_wien2k.calculations.run123_lapw import Wien2kRun123Lapw


def test_default(generate_calc_job_node, generate_parser, data_regression):
    """Test parsing of default calculation."""
    node = generate_calc_job_node('wien2k-run123_lapw', 'scf123', 'default')
    parser = generate_parser('wien2k-scf123-parser')
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    data_regression.check({'scf_grep': results['scf_grep'].get_dict()})


def test_failed_warning_converg(generate_calc_job_node, generate_parser, data_regression):
    """Test parsing of exit code ``WARNING_CONVERG``."""
    node = generate_calc_job_node('wien2k-run123_lapw', 'scf123', 'failed_warning_converg')
    parser = generate_parser('wien2k-scf123-parser')
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_failed, calcfunction.exit_status
    assert calcfunction.exit_status == Wien2kRun123Lapw.exit_codes.WARNING_CONVERG.status
    data_regression.check({'scf_grep': results['scf_grep'].get_dict()})


def test_failed_warning_other(generate_calc_job_node, generate_parser, data_regression):
    """Test parsing of exit code ``WARNING_OTHER``."""
    node = generate_calc_job_node('wien2k-run123_lapw', 'scf123', 'failed_warning_other')
    parser = generate_parser('wien2k-scf123-parser')
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_failed, calcfunction.exit_status
    assert calcfunction.exit_status == Wien2kRun123Lapw.exit_codes.WARNING_OTHER.status
    data_regression.check({'scf_grep': results['scf_grep'].get_dict()})


def test_failed_warning_qtl_b(generate_calc_job_node, generate_parser, data_regression):
    """Test parsing of exit code ``WARNING_QTL_B``."""
    node = generate_calc_job_node('wien2k-run123_lapw', 'scf123', 'failed_warning_qtl_b')
    parser = generate_parser('wien2k-scf123-parser')
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_failed, calcfunction.exit_status
    assert calcfunction.exit_status == Wien2kRun123Lapw.exit_codes.WARNING_QTL_B.status
    data_regression.check({'scf_grep': results['scf_grep'].get_dict()})
