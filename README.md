# aiida-wien2k
WIEN2k plug-in for AiiDA workflow management

## Questions
- [ ] Giovanni: One comment is that many other plugins avoid the explicit call to a calcfunction to convert an AiiDA StructureData to the internal code format, but just perform the conversion inside the `prepare_for_submission` of the first step.
- [ ] Names convention check

## Notes
* From a discussion during tutorials: Could they create a plugin that subclasses StructureData? That way it could still be used by all calc plugins that use StructureData and they could add all functionalities from ASE that they want. maybe subclassing, maybe creating a separate object


## TODOs:
- [ ] register `aiida-wien2k` in AiiDA repository 
- [ ] debugging AiiDA with VSCode https://marketplace.visualstudio.com/items?itemName=chrisjsewell.aiida-explore-vscode
- [ ] use `fuzzywuzzy` for error handeling (https://github.com/seatgeek/fuzzywuzzy)
- [ ] submission of parallel calculations (EOS example; see eos_workchain.py)

## Questions for Jul 13th meeting
* what to do with the APW specific parameters (RMT, r0 etc ) that are stored in the struct file?
