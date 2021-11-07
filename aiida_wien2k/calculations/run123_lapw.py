from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import Dict, SinglefileData, StructureData, Code
import ase.io
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

def aiida_struct2wien2k(aiida_structure):
    """prepare structure file for WIEN2k"""
    ase_structure = aiida_structure.get_ase() # AiiDA -> ASE struct
    ase.io.write("case.struct",ase_structure) # ASE -> WIEN2k, write WIEN2k struct
    path_to_rm_folder = os.getcwd() # get path to folder
    path_to_rm_structfile = os.path.join(path_to_rm_folder, 'case.struct') # get path to struct file
    wien2k_structfile = SinglefileData(file=path_to_rm_structfile) # get proper AiiDA type for a single file (otherwise you cannot return)
    return wien2k_structfile # orm.SinglefileData type (stored automatically in AiiDA database)

class Wien2kRun123Lapw(CalcJob):
    """AiiDA calculation plugin to run WIEN2k calculation using run123_lapw."""
    
    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(Wien2kRun123Lapw, cls).define(spec)

        # inputs/outputs
        spec.input('code', valid_type=Code, help='WIEN2k run123_lapw')
        spec.input('parameters', valid_type=Dict, required=False, help='Dictionary of input arguments (if any)')
        spec.input('wien2k_structure', valid_type=SinglefileData, required=False, help='WIEN2k input structure file case.struct')
        spec.input('aiida_structure', valid_type=StructureData, required=False, help='AiiDA input structure')
        spec.inputs['metadata']['options']['resources'].default = {
                                            'num_machines': 1,
                                            'num_mpiprocs_per_machine': 1,
                                            }
        spec.inputs['metadata']['options']['parser_name'].default = 'wien2k-scf123-parser'

        spec.output('scf_grep', valid_type=Dict, help='WIEN2k SCF output dictionary')
        # exit codes
        spec.exit_code(400, 'ERROR_ITER_0',
                message='Unable to perform even a single SCF iteration.')
        spec.exit_code(401, 'ERROR_MISSING_OUTPUT_FILES',
                message='Calculation did not produce all expected output files.')
        spec.exit_code(302, 'WARNING_QTL_B',
                message='WARN: QTL-B in the last iteration.')
        spec.exit_code(312, 'WARNING_QTL_B1',
                message='WARN: QTL-B in the last iteration prec1.')
        spec.exit_code(322, 'WARNING_QTL_B2',
                message='WARN: QTL-B in the last iteration prec2.')
        spec.exit_code(332, 'WARNING_QTL_B3',
                message='WARN: QTL-B in the last iteration prec3.')
        spec.exit_code(303, 'WARNING_VK_COUL',
                message='WARN: VK-COUL is not well converged.')
        spec.exit_code(313, 'WARNING_VK_COUL1',
                message='WARN: VK-COUL is not well converged prec1.')
        spec.exit_code(323, 'WARNING_VK_COUL2',
                message='WARN: VK-COUL is not well converged prec2.')
        spec.exit_code(333, 'WARNING_VK_COUL3',
                message='WARN: VK-COUL is not well converged prec3.')
        spec.exit_code(304, 'WARNING_INT',
                message='WARN: Integrated number of electrons is not consistent.')
        spec.exit_code(314, 'WARNING_INT1',
                message='WARN: Integrated number of electrons is not consistent prec1.')
        spec.exit_code(324, 'WARNING_INT2',
                message='WARN: Integrated number of electrons is not consistent prec2.')
        spec.exit_code(334, 'WARNING_INT3',
                message='WARN: Integrated number of electrons is not consistent prec3.')
        spec.exit_code(305, 'WARNING_CONVERG',
                message='WARN: SCF is not converged.')
        spec.exit_code(315, 'WARNING_CONVERG1',
                message='WARN: SCF prec1 is not converged.')
        spec.exit_code(325, 'WARNING_CONVERG2',
                message='WARN: SCF prec2 is not converged.')
        spec.exit_code(335, 'WARNING_CONVERG3',
                message='WARN: SCF prec3 is not converged.')
        spec.exit_code(309, 'WARNING_OTHER',
                message='WARN: There is a warning in the last SCF iteration.')
        spec.exit_code(319, 'WARNING_OTHER1',
                message='WARN: There is a warning in the last SCF iteration prec1.')
        spec.exit_code(329, 'WARNING_OTHER2',
                message='WARN: There is a warning in the last SCF iteration prec2.')
        spec.exit_code(339, 'WARNING_OTHER3',
                message='WARN: There is a warning in the last SCF iteration prec3.')
        
    
    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        parameters = _cli_options(self.inputs.parameters.get_dict()) # command line args for init_lapw
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = parameters # x exec [parameters]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = 'run123_lapw.log'

        # convert AiiDA structure -> WIEN2k
        if('aiida_structure' in self.inputs):
            aiida2wien_structfile = aiida_struct2wien2k(self.inputs.aiida_structure)
            aiida2wien_structfile.store()
        
        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        if('wien2k_structure' in self.inputs): # WIEN2k structure is given as input
            calcinfo.local_copy_list = [
                (self.inputs.wien2k_structure.uuid, self.inputs.wien2k_structure.filename, 'case/case.struct')
            ] # copy case.struct to the local folder as new.struct
        elif('aiida_structure' in self.inputs): # AiiDA structure is given as input
            calcinfo.local_copy_list = [
                (aiida2wien_structfile.uuid, aiida2wien_structfile.filename, 'case/case.struct')
            ] # copy case.struct to the local folder as new.struct
        calcinfo.remote_copy_list = [] # none
        calcinfo.retrieve_list = [('case/case.scf0'), ('case/case.scf1'), ('case/case.scf2'),\
                ('case/case.scfm'), ('case/case.scfc'), ('case/*.error*'), ('case/case.dayfile'),\
                ('case/prec1.scf0'), ('case/prec1.scf1'), ('case/prec1.scf2'),\
                ('case/prec1.scfm'), ('case/prec1.scfc'), ('case/prec1.dayfile'),\
                ('case/prec2.scf0'), ('case/prec2.scf1'), ('case/prec2.scf2'),\
                ('case/prec2.scfm'), ('case/prec2.scfc'), ('case/prec2.dayfile'),\
                ('case/prec3.scf0'), ('case/prec3.scf1'), ('case/prec3.scf2'),\
                ('case/prec3.scfm'), ('case/prec3.scfc'), ('case/prec3.dayfile')]

        return calcinfo