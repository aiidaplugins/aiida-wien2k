from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import Dict
import sys
from fuzzywuzzy import fuzz

def _grep_all_iter(key, pip):
    """"Serach patterns in lines `pip` that start with `key`"""
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

def _grep_last_iter(key, pip):
    """"Serach patterns in lines `pip` that start with `key` only last iteration"""
    value = []
    for line in reversed(pip.splitlines()): # search backward
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
        if(line[0:len(key)] == ":ITE"): # return the result as soon as :ITE found (last iteration because of backward serach)
            print('key=', key, 'value=', value)
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
        enelist = _grep_last_iter(key=":ENE", pip=file_content) # get all energies in SCF run
        if enelist: # check if energy list is not empty
            res['EtotRyd'] = enelist
        vollist = _grep_last_iter(key=":VOL", pip=file_content) # get all volumes in SCF run
        if vollist:
            res['VolBohr3'] = vollist
        eflist = _grep_last_iter(key=":FER", pip=file_content) # get all Fermi ene in SCF run
        if eflist:
            res['EfermiRyd'] = eflist
        iterlist = _grep_last_iter(key=":ITE", pip=file_content) # get all iteration in SCF run
        if iterlist:
            res['Iter'] = iterlist
        else:
            self.logger.error('Unable to perform even 1 SCF iteration.\n'+\
                    'Please check *.error files')
            raise # Exception: unable to perform even 1 iteration
        gaplist = _grep_last_iter(key=":GAP", pip=file_content) # get all band gaps in SCF run
        if gaplist:
            res['GapEv'] = gaplist
        warngslist = _grep_last_iter(key=":WAR", pip=file_content) # get all warnings
        if warngslist: # check if warnings list is not empty
            res['Warning_last'] = warngslist[-1] # get last message if there are multiple lines

        # Assign results
        self.out('scf_grep', res)

        # check error files

        # Return exit code
        if warngslist: # check if warnings list is not empty
            warn_qtlb = 'QTL-B value eq. in Band of energy ATOM= L='
            warn_vccoul = 'VK-COUL not well converged: Increase GMAX or decrease NCON'
            warn_int = 'RESULT OF INTEGRATION SHOULD BE'
            msg = res['Warning_last']
            print(msg)
            # handle errors using fuzzy matching
            if( fuzz.ratio(msg, warn_qtlb) > 50 ): # QRT-B warning
                return self.exit_codes.WARNING_QTL_B
            elif( fuzz.ratio(msg, warn_vccoul) > 50 ): # VK-COUL warning
                return self.exit_codes.WARNING_VK_COUL
            elif( fuzz.ratio(msg, warn_int) > 50 ): # RESULT OF INTEGRATION warning
                return self.exit_codes.WARNING_INT
            else: # unknown warning
                return self.exit_codes.WARNING_OTHER
        else:
            return ExitCode(0)