import io
from aiida.orm import StructureData, Code, Dict, ArrayData, utils
from aiida.engine import WorkChain, ToContext
from aiida.plugins.factories import CalculationFactory
from aiida.engine import calcfunction

@calcfunction
def _merge_dict(aiida_dict1, aiida_dict2):
    # merge dictionaries
    dmerged = aiida_dict1.get_dict()
    d = aiida_dict2.get_dict()
    for key in d.keys():
        if key in dmerged:
            if( not(type(dmerged[key])==list) ): # if element of dic is not a list, make it a list
                dmerged[key] = [dmerged[key]]
            # append to the list
            dmerged[key].append(d[key])
        else:
            dmerged[key] = d[key]

    return Dict(dict=dmerged)

Wien2kXSgroup = CalculationFactory("wien2k-x-sgroup") # plugin entry point
Wien2kInitLapw = CalculationFactory("wien2k-init_lapw")
Wien2kRunLapw = CalculationFactory("wien2k-run_lapw")
Wien2kXOptimize = CalculationFactory("wien2k-x-optimize")
Wien2kRunLapwClmextrapol = CalculationFactory("wien2k-run_lapw_clmextrapol")

class Wien2kEosWorkChain(WorkChain):
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
        spec.input("code4", valid_type=Code, required=True) # x optimize
        spec.input("code5", valid_type=Code, required=True) # run_lapw with clmextrapol
        spec.input("inpdict1", valid_type=Dict, required=True) # x sgroup [param]
        spec.input("inpdict2", valid_type=Dict, required=True) # init_lapw -b [param]
        spec.input("inpdict3", valid_type=Dict, required=True) # run_lapw [param]
        spec.input("inparr4", valid_type=ArrayData, required=True) # x optimize <<< [param]
        # calculation steps
        spec.outline(cls.x_sgroup,\
                cls.inspect_x_sgroup,\
                cls.init_lapw,\
                cls.inspect_init_lapw,\
                cls.run_lapw,\
                cls.inspect_run_lapw,\
                cls.x_optimize,\
                cls.run_lapw_clmextrapol,\
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
        """Run SCF calculation at V = V0."""

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
    
    def x_optimize(self):
        """Generate case_vol*.struct with different volumes."""

        if( not(self.ctx.node3.is_excepted) ): # make sure SCF at V0 is OK
            result = self.submit(
                Wien2kXOptimize,
                structfile_in = self.ctx.node2.outputs.structfile_out,
                parameters = self.inputs.inparr4,
                code = self.inputs.code4,
            )

        return ToContext(node4=result)

    def run_lapw_clmextrapol(self):
        """Run SCF calculations at different volumes V1, V2, ..."""

        # get all structure files created by x optimize and run scf for them
        structfile_uuid_list = self.ctx.node4.outputs.structfile_out_uuid_list.get_list()
        result = {}
        for structfile_uuid in structfile_uuid_list:
            structfile = utils.load_node(uuid=structfile_uuid)
            # here we use [structfile_uuid] as a label
            result = self.submit(
                Wien2kRunLapwClmextrapol,
                parent_folder = self.ctx.node3.outputs.remote_folder,
                wien2k_structure = structfile,
                parameters = self.inputs.inpdict3,
                code = self.inputs.code5,
            )
            self.to_context(**{structfile_uuid: result})

        return

    def result(self):
        """Parse the result."""

        # merge dict items from all results into one common dict
        dmerged = self.ctx.node3.outputs.scf_grep # result at V(0)
        structfile_uuid_list = self.ctx.node4.outputs.structfile_out_uuid_list.get_list()
        for structfile_uuid in structfile_uuid_list:
            result_aiida_dic = self.ctx[structfile_uuid].outputs.scf_grep # result at V(i)
            dmerged = _merge_dict(aiida_dict1=dmerged, aiida_dict2=result_aiida_dic)
        print(dmerged.get_dict())

        # Declaring the output
        self.out("workchain_result", dmerged)
    
        return

    def inspect_warn_all_steps(self):
        """Check warnings in all calculations and set the exit code accordingly"""

        # check all steps, including V(0) calculation
        for step in [self.ctx.node1, self.ctx.node2, self.ctx.node3, self.ctx.node4]:
            if( not step.is_finished_ok ):
                return self.exit_codes.WARNING # warnings during calc. steps
        # check steps V(i)
        structfile_uuid_list = self.ctx.node4.outputs.structfile_out_uuid_list.get_list()
        for structfile_uuid in structfile_uuid_list:
            step = self.ctx[structfile_uuid] # result at V(i)
            if( not step.is_finished_ok ):
                return self.exit_codes.WARNING # warnings during calc. steps
    
        return