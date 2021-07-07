# aiida-wien2k
WIEN2k plug-in for AiiDA workflow management

## Questions for AiiDA workshop
* submission of parallel calculations
* errors and warnings (displaying warnings on the providence graph)
* EOS +/- volumes (child calculations) based on the parent calculation VOL0
* adding command line parameters to a code (e.g., x nn, x sgroup, run_lapw -ee 0.0001)
* how to manipulate DB? one DB per project? there is no comments for "nodes" in DB; it is hard to keep track of what 726 was about? maybe use process label?
* how to handle k-parallel calculations?

## Questions for Jul 13th meeting
* what to do with the APW specific parameters (RMT, r0 etc ) that are stored in the struct file?
* looping over volumes: Should we call something from AIIDA or just write our own loop and store the data?
* what should we define as a "code" in code@host? (WIEN2k has many executables.)
* how should we add the input crystal structure as a node to the providence graph?
* how input crystal structures will be supplied to us? (for the paper) (see https://arxiv.org/pdf/2105.05063.pdf)
* do we need AIIDA <-> ASE <-> WIEN2k structure converter? (ASE <-> WIEN2k works fine) ase_structure = structure.get_ase()
* how results should be tresented? table E vs V for each initial structure?
* probably we need somethin similar to `PwBandsWorkChain.get_builder_from_protocol(code=code, structure=structure)`

Si structure in AiiDA:
```
In [2]: struct.attributes
Out[2]: 
{'cell': [[3.86697465, 0.0, 0.0],
  [1.933487325, 3.3488982826904, 0.0],
  [1.933487325, 1.1162994275635, 3.1573715802592]],
 'pbc1': True,
 'pbc2': True,
 'pbc3': True,
 'kinds': [{'mass': 28.085,
   'name': 'Si',
   'symbols': ['Si'],
   'weights': [1.0]}],
 'sites': [{'position': [5.800461975, 3.3488982826904, 2.3680286851944],
   'kind_name': 'Si'},
  {'position': [3.86697465, 2.232598855127, 1.5786857901296],
   'kind_name': 'Si'}]}
```

"[...] all the crystal structures stored in the database are saved in nodes that are of the type StructureData."
