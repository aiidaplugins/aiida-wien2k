from setuptools import setup

setup(
    name='aiida-wien2k',
    packages=['aiida_wien2k'],
    entry_points={
        'aiida.calculations': ["wien2k-x-sgroup = aiida_wien2k.calculations.x_sgroup:Wien2kXSgroup",
                            "wien2k-init_lapw = aiida_wien2k.calculations.init_lapw:Wien2kInitLapw",
                            "wien2k-run_lapw = aiida_wien2k.calculations.run_lapw:Wien2kRunLapw",
                            "wien2k-x-optimize = aiida_wien2k.calculations.x_optimize:Wien2kXOptimize",
                            "wien2k-run_lapw_clmextrapol = aiida_wien2k.calculations.run_lapw_clmextrapol:Wien2kRunLapwClmextrapol"],
        'aiida.parsers': ["wien2k-scf-parser = aiida_wien2k.parsers.scf:Wien2kScfParser",
                            "wien2k-sgroup-parser = aiida_wien2k.parsers.sgroup:Wien2kSgroupParser",
                            "wien2k-init_lapw-parser = aiida_wien2k.parsers.init_lapw:Wien2kInitLapwParser",
                            "wien2k-optimize-parser = aiida_wien2k.parsers.optimize:Wien2kOptimizeParser"],
        'aiida.workflows': ["wien2k.scf_wf = aiida_wien2k.workflows.scf_workchain:Wien2kScfWorkChain",
                            "wien2k.eos_wf = aiida_wien2k.workflows.eos_workchain:Wien2kEosWorkChain"],
    }
)
