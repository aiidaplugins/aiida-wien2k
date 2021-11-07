from aiida.orm import Int, StructureData, Code, Dict
from aiida.engine import WorkChain, ToContext
from aiida.plugins.factories import CalculationFactory

Wien2kRun123Lapw = CalculationFactory("wien2k-run123_lapw") # plugin entry point

class Wien2kScf123WorkChain(WorkChain):
    """WorkChain to add two integers."""

    @classmethod
    def define(cls, spec):
        """Specify inputs, outputs, and the workchain outline."""
        super().define(spec)
        # input parameters
        spec.input("aiida_structure", valid_type=StructureData, required=True)
        spec.input("code", valid_type=Code, required=True) # run123_lapw
        spec.input("inpdict", valid_type=Dict, required=True) # run123_lapw [param]
        # calculation steps
        spec.outline(cls.run123_lapw,\
                cls.inspect_run123_lapw,\
                cls.result,\
                cls.inspect_warn_all_steps)
        # output parameters
        spec.output("workchain_result", valid_type=Dict)
        # exit codes
        spec.exit_code(300, 'WARNING', 'There were warning messages during calculation steps')
        spec.exit_code(400, 'ERROR', 'There was a terminal error in one of calculation steps')
  
    def run123_lapw(self):
        """Run SCF calculation."""

        result = self.submit(
            Wien2kRun123Lapw,
            aiida_structure = self.inputs.aiida_structure,
            parameters = self.inputs.inpdict,
            code = self.inputs.code,
        )

        return ToContext(node=result)

    def inspect_run123_lapw(self):
        """Inspect results of run123_lapw"""

        if( self.ctx.node.is_excepted ):
            return self.exit_codes.ERROR # error during calc. steps
        
        return

    def result(self):
        """Parse the result."""

        # Declaring the output
        self.out("workchain_result", self.ctx.node.outputs.scf_grep)
    
        return

    def inspect_warn_all_steps(self):
        """Check warnings in all calculations and set the exit code accordingly"""

        for step in [self.ctx.node]:
            if( not step.is_finished_ok ):
                return self.exit_codes.WARNING # warnings during calc. steps
    
        return