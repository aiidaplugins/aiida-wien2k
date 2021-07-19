from setuptools import setup

setup(
    name='aiida-wien2k',
    packages=['aiida_wien2k'],
    entry_points={
        'aiida.calculations': ["wien2k-x-sgroup = aiida_wien2k.calculations.x_sgroup:Wien2kXSgroup",
                            "wien2k-init_lapw = aiida_wien2k.calculations.init_lapw:Wien2kInitLapw",
                            "wien2k-run_lapw = aiida_wien2k.calculations.run_lapw:Wien2kRunLapw"],
        'aiida.parsers': ["wien2k-scf-parser = aiida_wien2k.parsers.scf:Wien2kScfParser",
                            "wien2k-sgroup-parser = aiida_wien2k.parsers.sgroup:Wien2kSgroupParser"],
        'aiida.workflows': ["wien2k.scf_wf = aiida_wien2k.workflows.scf_workchain:Wien2kScfWorkChain"],
    }
)
