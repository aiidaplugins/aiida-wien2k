from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import Dict, SinglefileData, StructureData, Code
import io
import numpy as np
from ase.units import Bohr

def cellconst(metT):
    """ metT=np.dot(cell,cell.T) """
    aa = np.sqrt(metT[0, 0])
    bb = np.sqrt(metT[1, 1])
    cc = np.sqrt(metT[2, 2])
    gamma = np.arccos(metT[0, 1] / (aa * bb)) / np.pi * 180.0
    beta = np.arccos(metT[0, 2] / (aa * cc)) / np.pi * 180.0
    alpha = np.arccos(metT[1, 2] / (bb * cc)) / np.pi * 180.0
    return np.array([aa, bb, cc, alpha, beta, gamma])

def write_struct(f, atoms2=None, rmt=None, lattice='P', zza=None):
    """ Adapted from ASE.
        It writes ASE structure into a WIEN2k struct file as a StringIO
        file-like object."""
    atoms = atoms2.copy()
    atoms.wrap()
    f.write('ASE generated\n')
    nat = len(atoms)
    if rmt is None:
        rmt = [2.0] * nat
        f.write(lattice +
                '   LATTICE,NONEQUIV.ATOMS:%3i\nMODE OF CALC=RELA\n' % nat)
    cell = atoms.get_cell()
    metT = np.dot(cell, np.transpose(cell))
    cell2 = cellconst(metT)
    cell2[0:3] = cell2[0:3] / Bohr
    f.write(('%10.6f' * 6) % tuple(cell2) + '\n')
    if zza is None:
        zza = atoms.get_atomic_numbers()
    for ii in range(nat):
        f.write('ATOM %3i: ' % (ii + 1))
        pos = atoms.get_scaled_positions()[ii]
        f.write('X=%10.8f Y=%10.8f Z=%10.8f\n' % tuple(pos))
        f.write('          MULT= 1          ISPLIT= 1\n')
        zz = zza[ii]
        if zz > 71:
            ro = 0.000005
        elif zz > 36:
            ro = 0.00001
        elif zz > 18:
            ro = 0.00005
        else:
            ro = 0.0001
        f.write('%-10s NPT=%5i  R0=%9.8f RMT=%10.4f   Z:%10.5f\n' %
                (atoms.get_chemical_symbols()[ii], 781, ro, rmt[ii], zz))
        f.write('LOCAL ROT MATRIX:    %9.7f %9.7f %9.7f\n' % (1.0, 0.0, 0.0))
        f.write('                     %9.7f %9.7f %9.7f\n' % (0.0, 1.0, 0.0))
        f.write('                     %9.7f %9.7f %9.7f\n' % (0.0, 0.0, 1.0))
    f.write('   0\n')
    return f # file-like object

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
    # create a file like object for the WIEN2k struct file to avoid writing it to disk
    wien2k_structfile_flo = io.StringIO() 
    # ASE -> WIEN2k, write WIEN2k struct
    wien2k_structfile_flo = write_struct(f=wien2k_structfile_flo, atoms2=ase_structure)
    # get proper AiiDA type for a single file (otherwise you cannot return)
    # Here we use bytes file-like object as an input to avoid creating an intermediate file
    # (It happened that the other process can overide such file)
    wien2k_structfile = SinglefileData(\
                file=io.BytesIO(bytes(wien2k_structfile_flo.getvalue(),'utf-8')),\
                filename='case.struct')

    return wien2k_structfile # orm.SinglefileData type

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
        calcinfo.retrieve_list = [('case/*.scf0'), ('case/*.scf1'), ('case/*.scf2'),\
                ('case/*.scfm'), ('case/*.scfc'), ('case/*.error*'), ('case/*.dayfile')]

        return calcinfo