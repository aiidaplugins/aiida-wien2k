from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData, List
from aiida_wien2k.parsers.scf import check_error_files

def _check_struct_files(files, logger):
    """
    Check for *.struct files among 'files' retrieved.
    Print errors into the error logger.

    Return:
    not_empty (bool)
    """
    struct_files_present = False
    for fname in files.list_object_names(): # loop through all files retrieved
        if( fname.endswith('struct') ): # struct file
            struct_files_present = True
    if( not(struct_files_present) ): # non-empty error files found
        errmsgs = 'no case_vol_*.struct file(s) generated'
        logger.error(errmsgs) # write all error messages to a logger

    return struct_files_present # True is there is at least 1 *.struct file

DiffCalculation = CalculationFactory('wien2k-x-optimize')

class Wien2kOptimizeParser(Parser):
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: non-zero exit code, if parsing fails
        """

        # check error files and write to logger if any of them are not empty
        struct_files_present = _check_struct_files(files=self.retrieved, logger=self.logger)
        if( not(struct_files_present) ):
            raise # no case_vol_*.struct file(s) generated

        # create a list of SinglefileData objects that contain WIEN2k struct files 
        # at different volumes [vol1, vol2, ...]
        structfile_uuid_list = []
        for fname in self.retrieved.list_object_names(): # loop through all files retrieved
            if( fname.endswith('struct') ): # select only struct files
                with self.retrieved.open(fname, 'rb') as handle:
                    structfile = SinglefileData(file=handle)
                    structfile.store()
                structfile_uuid_list.append(structfile.uuid)
        
        # Convert to AiiDA list and return all structure files [vol1, vol2, ...]
        self.out('structfile_out_uuid_list', List(list=structfile_uuid_list) )

        return ExitCode(0)