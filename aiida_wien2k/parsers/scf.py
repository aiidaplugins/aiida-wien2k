from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData, Dict
import os, sys

def _grep(key, pip):
    value = []
    for line in pip.splitlines():
        if(key==":ENE"): # total energy [Ry]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value.append( float(cut) )
        elif(key==":VOL"): # cell folume [Borh3]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value.append( float(cut) )
        elif(key==":FER"): # Fermi energy [Ry]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value.append( float(cut) )
        elif(key==":ITE"): # Iteration number
            if line[0:len(key)] == key:
                cut = line.rsplit(sep=':',maxsplit=-1)[-1]
                cut = cut.rsplit(sep='.',maxsplit=-1)[0]
                value.append( int(cut) )
        elif(key==":GAP"): # Band gap [eV]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[-1]
                cut = cut.rsplit(sep=' eV ',maxsplit=-1)[0]
                value.append( float(cut) )
        elif(key==":WAR"): # warnings
            if line[0:len(key)] == key:
                value.append( line )
        else:
            sys.exit(1) # error: grep option not implemented
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
        if enelist: # check if energy list is not empty
            res['EtotRyd'] = enelist[-1] # store last one
        vollist = _grep(key=":VOL", pip=file_content) # get all volumes in SCF run
        if vollist:
            res['VolBohr3'] = vollist[-1]
        eflist = _grep(key=":FER", pip=file_content) # get all Fermi ene in SCF run
        if eflist:
            res['EfermiRyd'] = eflist[-1]
        iterlist = _grep(key=":ITE", pip=file_content) # get all iteration in SCF run
        if iterlist:
            res['Iter'] = iterlist[-1]
        gaplist = _grep(key=":GAP", pip=file_content) # get all band gaps in SCF run
        if gaplist:
            res['GapEv'] = gaplist[-1]
        warngslist = _grep(key=":WAR", pip=file_content) # get all warnings
        if warngslist: # check if warnings list is not empty
            res['Warning_last'] = warngslist[-1]
        self.out('scf_grep', res)

        return ExitCode(0)