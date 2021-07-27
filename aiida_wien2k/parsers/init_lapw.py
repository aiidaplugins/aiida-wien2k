from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import Dict
import sys
from fuzzywuzzy import fuzz
import os.path

DiffCalculation = CalculationFactory('wien2k-init_lapw')

class Wien2kInitLapwParser(Parser):
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: non-zero exit code, if parsing fails
        """

        output_filename = 'init_lapw.log'

        #Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename]
        # Note: set(A) <= set(B) checks whether A is a subset of B
        if( not set(files_expected) <= set(files_retrieved) ):
            self.logger.error(f"Found files '{files_retrieved}', expected to find '{files_expected}'")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES
        
        # check if the log file finishes with 'init_lapw finished ok'
        self.logger.info(f"Parsing '{output_filename}'")
        file_content = self.retrieved.get_object_content(output_filename)
        file_content_list = file_content.splitlines()
        last_line = file_content_list[-1]
        msgOK = 'init_lapw finished ok'
        if( fuzz.ratio(msgOK, last_line) < 50 ): # not OK
            self.logger.error(f"Found last line in init_lapw.log file '{last_line}',"+\
                    f" while expected to find '{msgOK}'\n" +\
                    "init_lapw failed")
            raise # init_lapw failed
        
        # check for core leakage
        corefile = 'case/.lcore'
        if os.path.isfile(corefile): # .lcore file found
            return self.exit_codes.WARNING_CORE_LEAKAGE

        return ExitCode(0)
