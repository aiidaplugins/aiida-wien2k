from aiida.orm import Int, StructureData, Code, Dict
from aiida.engine import WorkChain, ToContext
from aiida.plugins.factories import CalculationFactory

Wien2kXSgroup = CalculationFactory("wien2k-x-sgroup") # plugin entry point
Wien2kInitLapw = CalculationFactory("wien2k-init_lapw")
Wien2kRunLapw = CalculationFactory("wien2k-run_lapw")

class Wien2kScfWorkChain(WorkChain):
    """WorkChain to add two integers."""

    @classmethod
    def define(cls, spec):
        """Specify inputs, outputs, and the workchain outline."""
        super().define(spec)
        # input parameters
        spec.input("aiida_structure", valid_type=StructureData, required=True)
        spec.input("code1", valid_type=Code, required=True) # x sgroup
        spec.input("code2", valid_type=Code, required=True) # init_lapw
        spec.input("code3", valid_type=Code, required=True) # run_lapw
        spec.input("inpdict1", valid_type=Dict, required=True) # x sgroup [param]
        spec.input("inpdict2", valid_type=Dict, required=True) # init_lapw -b [param]
        spec.input("inpdict3", valid_type=Dict, required=True) # run_lapw [param]
        # calculation steps
        spec.outline(cls.x_sgroup,\
                cls.inspect_x_sgroup,\
                cls.init_lapw,\
                cls.inspect_init_lapw,\
                cls.run_lapw,\
                cls.inspect_run_lapw,\
                cls.result,\
                cls.inspect_warn_all_steps)
        # output parameters
        spec.output("workchain_result", valid_type=Dict)
        # exit codes
        spec.exit_code(300, 'WARNING', 'There were warning messages during calculation steps')
        spec.exit_code(400, 'ERROR', 'There was a terminal error in one of calculation steps')

    def x_sgroup(self):
        """Generate case.struct with symmetry."""

        result = self.submit(
            Wien2kXSgroup,
            aiida_structure = self.inputs.aiida_structure,
            parameters = self.inputs.inpdict1,
            code = self.inputs.code1,
        )

        return ToContext(node1=result)

    def inspect_x_sgroup(self):
        """Inspect results of x sgroup"""

        if( self.ctx.node1.is_excepted ):
            return self.exit_codes.ERROR # error during calc. steps
        
        return
    
    def init_lapw(self):
        """Initialize calculation with init_lapw."""

        result = self.submit(
            Wien2kInitLapw,
            structfile = self.ctx.node1.outputs.structfile_out,
            parameters = self.inputs.inpdict2,
            code = self.inputs.code2,
        )

        return ToContext(node2=result)
    
    def inspect_init_lapw(self):
        """Inspect results of init_lapw"""

        if( self.ctx.node2.is_excepted ):
            return self.exit_codes.ERROR # error during calc. steps
        
        return
    
    def run_lapw(self):
        """Run SCF calculation."""

        result = self.submit(
            Wien2kRunLapw,
            parent_folder = self.ctx.node2.outputs.remote_folder,
            parameters = self.inputs.inpdict3,
            code = self.inputs.code3,
        )

        return ToContext(node3=result)

    def inspect_run_lapw(self):
        """Inspect results of run_lapw"""

        if( self.ctx.node3.is_excepted ):
            return self.exit_codes.ERROR # error during calc. steps
        
        return

    def result(self):
        """Parse the result."""

        # Declaring the output
        self.out("workchain_result", self.ctx.node3.outputs.scf_grep)
    
        return

    def inspect_warn_all_steps(self):
        """Check warnings in all calculations and set the exit code accordingly"""

        for step in [self.ctx.node1, self.ctx.node2, self.ctx.node3]:
            if( not step.is_finished_ok ):
                return self.exit_codes.WARNING # warnings during calc. steps
    
        return