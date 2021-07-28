from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData
from aiida_wien2k.parsers.scf import check_error_files

DiffCalculation = CalculationFactory('wien2k-x-sgroup')

class Wien2kSgroupParser(Parser):
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: non-zero exit code, if parsing fails
        """

        # add output file
        self.logger.info(f"Parsing results of x sgroup")
        with self.retrieved.open('case.struct_sgroup', 'rb') as handle:
            structfile = SinglefileData(file=handle)
        self.out('structfile_out', structfile)

        # check error files and write to logger if any of them are not empty
        err_files_not_empty = check_error_files(files=self.retrieved, logger=self.logger)
        if( err_files_not_empty ):
            raise # non-empty error file(s) found

        return ExitCode(0)