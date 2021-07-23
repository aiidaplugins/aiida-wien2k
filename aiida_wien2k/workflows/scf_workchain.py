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
                cls.init_lapw,\
                cls.run_lapw,\
                cls.result)
        # output parameters
        spec.output("workchain_result", valid_type=Dict)

    def x_sgroup(self):
        """Generate case.struct with symmetry."""

        result = self.submit(
            Wien2kXSgroup,
            aiida_structure = self.inputs.aiida_structure,
            parameters = self.inputs.inpdict1,
            code = self.inputs.code1,
        )

        return ToContext(node1=result)
    
    def init_lapw(self):
        """Initialize calculation with init_lapw."""

        result = self.submit(
            Wien2kInitLapw,
            structfile = self.ctx.node1.outputs.structfile_out,
            parameters = self.inputs.inpdict2,
            code = self.inputs.code2,
        )

        return ToContext(node2=result)
    
    def run_lapw(self):
        """Run SCF calculation."""

        result = self.submit(
            Wien2kRunLapw,
            parent_folder = self.ctx.node2.outputs.remote_folder,
            parameters = self.inputs.inpdict3,
            code = self.inputs.code3,
        )

        # check if all error files are empty
        # node = result.get('retrieved')
        # node.list_object_names()
        # node.get_object_content('dstart.error')

        return ToContext(node3=result)

    def result(self):
        """Parse the result."""

        # Declaring the output
        print(self.ctx)
        self.out("workchain_result", self.ctx.node3.outputs.scf_grep)
