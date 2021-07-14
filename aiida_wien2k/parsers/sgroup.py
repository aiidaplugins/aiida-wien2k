from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData, Dict
import os, sys

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

        return ExitCode(0)