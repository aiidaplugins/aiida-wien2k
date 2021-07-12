from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData, Dict
import os, sys

def _grep(key, pip):
    #Aaarrrggghhhh
    if(key==":ENE"): 
        col1=39;col2=61
    elif(key==":VOL"): 
        col1=26;col2=40
    else:
        sys.exit(1) # error: grep option not implementer
    value = []
    for line in pip.splitlines():
        if line[0:len(key)] == key:
            value.append(float(line[col1:col2]) )
    return value

DiffCalculation = CalculationFactory('wien2k-run_lapw')

class Wien2kScfParser(Parser):
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: non-zero exit code, if parsing fails
        """

        output_filename = 'case.scf'

        #Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename]
        # Note: set(A) <= set(B) checks whether A is a subset of B
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(f"Found files '{files_retrieved}', expected to find '{files_expected}'")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES
        
        # add output file
        self.logger.info(f"Parsing '{output_filename}'")
        file_content = self.retrieved.get_object_content(output_filename)
        res = Dict()
        enelist = _grep(key=":ENE", pip=file_content) # get all energies in SCF run
        res['EtotRyd'] = enelist[-1] # store last one
        vollist = _grep(key=":VOL", pip=file_content) # get all volumes in SCF run
        res['VolBohr3'] = vollist[-1] # store last one
        self.out('scf_grep', res)

        return ExitCode(0)