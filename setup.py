from setuptools import setup

setup(
    name='aiida-wien2k',
    packages=['aiida_wien2k'],
    entry_points={
        'aiida.calculations': ["wien2k-run123_lapw = aiida_wien2k.calculations.run123_lapw:Wien2kRun123Lapw"],
        'aiida.parsers': ["wien2k-scf123-parser = aiida_wien2k.parsers.scf123:Wien2kScf123Parser"],
        'aiida.workflows': ["wien2k.scf123_wf = aiida_wien2k.workflows.scf123_workchain:Wien2kScf123WorkChain"],
    }
)
