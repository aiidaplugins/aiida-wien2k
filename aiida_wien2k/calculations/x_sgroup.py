from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import SinglefileData, Dict, RemoteData, Code, Str, FolderData
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

class Wien2kXSgroup(CalcJob):
    """AiiDA calculation plugin for WIEN2k calculation to execute: x sgroup [parameters]."""
    
    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(Wien2kXSgroup, cls).define(spec)

        # inputs/outputs
        spec.input('code', valid_type=Code, help='WIEN2k x sgroup')
        spec.input('parameters', valid_type=Dict, required=False, help='Dictionary of input arguments (if any)')
        spec.input('structfile_in', valid_type=SinglefileData, required=False, help='Structure file case.struct')
        spec.input('parent_folder', valid_type=RemoteData, required=False,\
                   help='parent_folder passed from a previous calulation')
        spec.inputs['metadata']['options']['resources'].default = {
                                            'num_machines': 1,
                                            'num_mpiprocs_per_machine': 1,
                                            }
        spec.inputs['metadata']['options']['parser_name'].default = 'wien2k-sgroup-parser'
        spec.output('structfile_out', valid_type=SinglefileData, help='Structure file after x sgroup')

        spec.exit_code(300, 'ERROR_MISSING_OUTPUT_FILES',
                message='Calculation did not produce all expected output files.')
        
    
    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        parameters = _cli_options(self.inputs.parameters.get_dict()) # command line args for init_lapw
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = ['sgroup'] + parameters # x exec [parameters]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = 'x.log'
        
        remote_copy_list = []
        if 'parent_folder' in self.inputs:
            path_from = os.path.join(self.inputs.parent_folder.get_remote_path(),'case')
            remote_copy_list = [(
                self.inputs.parent_folder.computer.uuid,
                path_from, './'
            )]
        else:
            folder.get_subfolder('case', create=True) # create case subfolder

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        if 'structfile_in' in self.inputs:
            calcinfo.local_copy_list = [
                (self.inputs.structfile_in.uuid, self.inputs.structfile_in.filename, 'case/case.struct')
            ] # copy case.struct to the local folder as new.struct
        else:
            calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = remote_copy_list
        calcinfo.retrieve_list = [('case/case.struct_sgroup'), ('case/*.error*')]

        return calcinfo