from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import Dict
from fuzzywuzzy import fuzz

def _grep(key, pip):
    """"Serach patterns in lines `pip` that start with `key` only last iteration"""
    for line in pip.splitlines(): # search backward
        if(key==":ENE"): # total energy [Ry]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value = float(cut)
                return value
        elif(key==":VOL"): # cell folume [Borh3]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value = float(cut)
                return value
        elif(key==":FER"): # Fermi energy [Ry]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[1]
                value = float(cut)
                return value
        elif(key==":ITE"): # Iteration number
            if line[0:len(key)] == key:
                cut = line.rsplit(sep=':',maxsplit=-1)[-1]
                cut = cut.rsplit(sep='.',maxsplit=-1)[0]
                value = int(cut)
                return value
        elif(key==":GAP"): # Band gap [eV]
            if line[0:len(key)] == key:
                cut = line.rsplit(sep='=',maxsplit=-1)[-1]
                cut = cut.rsplit(sep=' eV ',maxsplit=-1)[0]
                value = float(cut)
                return value
        elif(key==":WAR"): # warnings
            if line[0:len(key)] == key:
                value = line
                return value
        elif(key==":WAR"): # warnings
            if line[0:len(key)] == key:
                value = [line]
                return value
        else: # generic grep option not implemented
            if line[0:len(key)] == key:
                value = line
                return value

    return None # return none if no match found

def _grep_all_instances(key, pip):
    """"Serach patterns in lines `pip` that start with `key` and return all instances as a list"""
    value = [] # set up as a list
    for line in pip.splitlines(): # search backward
        if(key==":CHA"): # search for Rmt's
            if line[0:len(key)] == key:
                # :CHA001: TOTAL VALENCE CHARGE INSIDE SPHERE   1 =   6.7577    (RMT=  1.5800 )
                cut = line.rsplit(sep='RMT=',maxsplit=-1)
                if( len(cut)>1 ): # line contains 'RMT='
                    cut = cut[1] # get '1.5800 )'
                    cut = cut.rsplit(sep=')',maxsplit=-1)[0] # get '1.5800'
                    value.append(float(cut))
        elif(key==":POS"): # serach for atom labels
            if line[0:len(key)] == key:
                # :POS001: ATOM    1 X,Y,Z = 0.00000 0.00000 0.00000  MULT= 1  ZZ= 14.000  Si1
                cut = line[73:75] # get exact positions (fixed format)
                value.append(cut.strip()) # remove trailing spaces before appending
        elif(key==":CINT"): # search for the number of core electrons
            if line[0:len(key)] == key:
                # :CINT001 Core Integral Atom   1    3.99550337
                cut = line.rsplit(sep='Core Integral Atom',maxsplit=-1)[1] # get '1    3.99550337'
                cut = cut.split()[1] # get '3.99550337'
                value.append(int(round(float(cut))))

    return value


    return None # return none if no match found

def check_error_files(files, logger):
    """
    Check for *.error files among 'files' retrieved.
    Return 'True' if any of then are not empty.
    Print errors into the error logger.

    Return:
    not_empty (bool)
    """
    not_empty = False
    errmsgs = ''
    for fname in files.list_object_names(): # loop through all files retrieved
        if( fname.endswith('error') ): # error file
            err_file_content = files.get_object_content(fname)
            if( err_file_content != '' ): # error file is empty
                not_empty = True
                errmsgs += f"File: {fname}\n" # assamble all error messages
                errmsgs += err_file_content + "\n"
    if( not_empty ): # non-empty error files found
        logger.error(errmsgs) # write all error messages to a logger

    return not_empty # False if all *.error files are empty
    

DiffCalculation = CalculationFactory('wien2k-run_lapw')

class Wien2kScfParser(Parser):
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: non-zero exit code, if parsing fails
        """

        # check error files and write to logger if any of them are not empty
        err_files_not_empty = check_error_files(files=self.retrieved, logger=self.logger)
        if( err_files_not_empty ):
            raise # non-empty error file(s) found

        # all file to be processed
        output_fnames = ['case.scf0', 'case.scf1', 'case.scf2', \
                'case.scfm', 'case.scfc', 'run_lapw.log']

        #Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        # Note: set(A) <= set(B) checks whether A is a subset of B
        if not set(output_fnames) <= set(files_retrieved):
            self.logger.error(f"Found files '{files_retrieved}', expected to find '{output_fnames}'")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES
        
        # get output data
        res = Dict()

        # :ITE, :VOL
        output_fname = 'case.scf0'
        self.logger.info(f"Parsing '{output_fname}'")
        file_content = self.retrieved.get_object_content(output_fname)
        iterlist = _grep(key=":ITE", pip=file_content) # get all iteration in SCF run
        if iterlist:
            res['Iter'] = iterlist
        vollist = _grep(key=":VOL", pip=file_content) # get all volumes in SCF run
        if vollist:
            res['VolBohr3'] = vollist
        else:
            raise # Cell volume not found
        
        # :FER, :GAP, :CHA, :POS
        output_fname = 'case.scf2'
        self.logger.info(f"Parsing '{output_fname}'")
        file_content = self.retrieved.get_object_content(output_fname)
        eflist = _grep(key=":FER", pip=file_content) # get Fermi ene in SCF run
        if eflist:
            res['EfermiRyd'] = eflist
        else:
            raise # Efermi not found
        gaplist = _grep(key=":GAP", pip=file_content) # get band gap
        if gaplist:
            res['GapEv'] = gaplist
        rmtlist = _grep_all_instances(key=":CHA", pip=file_content) # get RMTs
        if rmtlist:
            res['Rmt'] = rmtlist
        else:
            raise # Rmt's not found
        atomlablelist = _grep_all_instances(key=":POS", pip=file_content) # get RMTs
        if atomlablelist:
            res['atom_labels'] = atomlablelist
        else:
            raise # atom labels not found
        

        # :ENE,:CINT
        output_fname = 'case.scfm'
        self.logger.info(f"Parsing '{output_fname}'")
        file_content = self.retrieved.get_object_content(output_fname)
        enelist = _grep(key=":ENE", pip=file_content) # get all energies in SCF run
        if enelist: # check if energy list is not empty
            res['EtotRyd'] = enelist
        else:
            raise # Etot not found
        # get number of core electrons
        numcoreellist = _grep_all_instances(key=":CINT", pip=file_content)
        if numcoreellist:
            res['num_core_el'] = numcoreellist
        else:
            raise # number of core electrons not found

        # :WAR
        res['Warning_last'] = [] # allocate list
        for output_fname in output_fnames:
            self.logger.info(f"Parsing '{output_fname}'")
            file_content = self.retrieved.get_object_content(output_fname)
            warngmsg = _grep(key=":WAR", pip=file_content) # get all warnings
            if warngmsg: # check if warnings list is not empty
                res['Warning_last'].append(warngmsg) # get last message if there are multiple lines

        # Assign results
        self.out('scf_grep', res)

        # Check warnings (if any) and assign the exit code accordingly
        if res['Warning_last']: # check if warnings list is not empty
            warn_qtlb = 'QTL-B value eq. in Band of energy ATOM= L='
            warn_vccoul = 'VK-COUL not well converged: Increase GMAX or decrease NCON'
            warn_int = 'RESULT OF INTEGRATION SHOULD BE'
            for msg in res['Warning_last']:
                # handle warnings using fuzzy matching
                if( fuzz.ratio(msg, warn_qtlb) > 50 ): # QRT-B warning
                    return self.exit_codes.WARNING_QTL_B
                elif( fuzz.ratio(msg, warn_vccoul) > 50 ): # VK-COUL warning
                    return self.exit_codes.WARNING_VK_COUL
                elif( fuzz.ratio(msg, warn_int) > 50 ): # RESULT OF INTEGRATION warning
                    return self.exit_codes.WARNING_INT
            # in case of no known warnings
            return self.exit_codes.WARNING_OTHER
        
        # Check if calculation is converged
        output_fname = 'run_lapw.log'
        self.logger.info(f"Parsing '{output_fname}'")
        file_content = self.retrieved.get_object_content(output_fname)
        converged = _grep(key="ec cc and fc_conv 1 1 1", pip=file_content) # check if the line present in log file
        if not converged: # if line not found
            res['Warning_last'].append('Warning: SCF not converged')
            return self.exit_codes.WARNING_CONVERG

        return ExitCode(0) # finished OK