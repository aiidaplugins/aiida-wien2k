from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import Dict, RemoteData, Code, SinglefileData
import os

def _cli_options(parameters):
    """Return command line options for parameters dictionary.

    :param dict parameters: dictionary with command line parameters
    """
    options = []
    for key, value in parameters.items():
     # Could validate: is key a known command-line option?
     if isinstance(value, bool) and value:
        options.append(f'{key}')
     elif isinstance(value, str):
        # Could validate: is value a valid regular expression?
        options.append(f'{key}')
        options.append(value)

    return options

class Wien2kRunLapwClmextrapol(CalcJob):
    """AiiDA calculation plugin to initialize WIEN2k calculation using init_lapw
    with clmextrapol"""
    
    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(Wien2kRunLapwClmextrapol, cls).define(spec)

        # inputs/outputs
        spec.input('code', valid_type=Code, help='WIEN2k run_lapw')
        spec.input('parameters', valid_type=Dict, required=False, help='Dictionary of input arguments (if any)')
        spec.input('wien2k_structure', valid_type=SinglefileData, required=True, help='WIEN2k structure file')
        spec.input('parent_folder', valid_type=RemoteData, required=True,\
                   help='parent_folder passed from a previous calulation')
        spec.inputs['metadata']['options']['resources'].default = {
                                            'num_machines': 1,
                                            'num_mpiprocs_per_machine': 1,
                                            }
        spec.inputs['metadata']['options']['parser_name'].default = 'wien2k-scf-parser'

        spec.output('scf_grep', valid_type=Dict, help='WIEN2k SCF output dictionary')
        # exit codes
        spec.exit_code(300, 'ERROR_ITER_0',
                message='Unable to perform even a single SCF iteration.')
        spec.exit_code(301, 'ERROR_MISSING_OUTPUT_FILES',
                message='Calculation did not produce all expected output files.')
        spec.exit_code(302, 'WARNING_QTL_B',
                message='WARN: QTL-B in the last iteration.')
        spec.exit_code(303, 'WARNING_VK_COUL',
                message='WARN: VK-COUL is not well converged.')
        spec.exit_code(304, 'WARNING_INT',
                message='WARN: Integrated number of electrons is not consistent.')
        spec.exit_code(305, 'WARNING_CONVERG',
                message='WARN: SCF is not converged.')
        spec.exit_code(399, 'WARNING_OTHER',
                message='WARN: There is a warning in the last SCF iteration.')
        
    
    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        parameters = _cli_options(self.inputs.parameters.get_dict()) # command line args for run_lapw
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = parameters # x exec [parameters]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = 'run_lapw.log'
        
        # copy parent case folder
        path_from = os.path.join(self.inputs.parent_folder.get_remote_path(),'case')
        remote_copy_list = []
        remote_copy_list = [(
                self.inputs.parent_folder.computer.uuid,
                path_from, './')]

        #folder.get_subfolder('case', create=True) # create case subfolder

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        # copy input case.struct
        calcinfo.local_copy_list = [
                (self.inputs.wien2k_structure.uuid, self.inputs.wien2k_structure.filename, 'case.struct')
            ] # copy case.struct to the local folder (not into case dicectory!); it will be moved into it by the code definition prepend
        calcinfo.remote_copy_list = remote_copy_list
        calcinfo.retrieve_list = [('case/case.scf0'), ('case/case.scf1'), ('case/case.scf2'),\
                ('case/case.scfm'), ('case/case.scfc'), ('case/*.error*'), ('case/run_lapw.log')]

        return calcinfo