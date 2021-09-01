import io
from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import SinglefileData, ArrayData, Code, List

def _cli_options(parameters):
    """Return command line options for parameters passed as
    AiiDA ArrayData
    """
    arrayname = parameters.get_arraynames()[0]
    dVarray = parameters.get_array(arrayname) # array of volume change in %: -6, -2, ...
    ndV = 0 # number of non-zero volume changes
    options = ''
    for dV in dVarray:
        if dV != 0: # exclude zero volume change
            options += '\n' + str(dV)
            ndV += 1
    if ndV == 0:
        raise # error 0 volume changes
    options = '1\n' + str(ndV) + options # 1 is the uniform (a, b, c) volume change option

    return options

class Wien2kXOptimize(CalcJob):
    """AiiDA calculation plugin for WIEN2k calculation to execute: x optimize <<< parameters"""
    
    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(Wien2kXOptimize, cls).define(spec)

        # inputs
        spec.input('code', valid_type=Code, help='WIEN2k x optimize')
        spec.input('parameters', valid_type=ArrayData, required=True, help='Array of volume changes in %')
        spec.input('structfile_in', valid_type=SinglefileData, required=True, help='Structure file case.struct')
        spec.inputs['metadata']['options']['resources'].default = {
                                            'num_machines': 1,
                                            'num_mpiprocs_per_machine': 1,
                                            }
        spec.inputs['metadata']['options']['parser_name'].default = 'wien2k-optimize-parser'
        # outputs
        spec.output('structfile_out_uuid_list', valid_type=List,\
                help='List of UUID for structure files of different volumes')
    
    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        paramstr = _cli_options(self.inputs.parameters) # convert input array of volume changes into command line args for optimize
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = ['optimize'] # x exec
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdin_name = 'paramstr.dat' # contains options for x optimize
        codeinfo.stdout_name = 'x.log'

        
        folder.get_subfolder('case', create=True) # create case subfolder

        # create file with options for x optimize
        folder.create_file_from_filelike(io.StringIO(paramstr),'case/paramstr.dat','w', encoding='utf8')


        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.local_copy_list = [
            (self.inputs.structfile_in.uuid, self.inputs.structfile_in.filename,
            'case/case.struct')
        ] # copy 'structfile_in' to the local folder as case.struct
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = [('case/case_vol*.struct')]

        return calcinfo