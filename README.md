# aiida-wien2k
WIEN2k plug-in for AiiDA workflow management

## Questions for AiiDA workshop
- [x] how to manipulate DB? one DB per project? there is no comments for "nodes" in DB; it is hard to keep track of what 726 was about? maybe use process label?
- [x] EOS +/- volumes (child calculations) based on the parent calculation VOL0: use copy
- [x] adding command line parameters to a code (e.g., x nn, x sgroup, run_lapw -ee 0.0001)
- [x] how to handle k-parallel calculations?: number of cores are passed to AiiDA
- [x] debuging AiiDA with VSCode https://marketplace.visualstudio.com/items?itemName=chrisjsewell.aiida-explore-vscode
- [x] submission of parallel calculations (EOS example; see eos_workchain.py)
```
(base) aiida@jupyter-rubel75:~$ verdi process list
  PK  Created    Process label    Process State    Process status
----  ---------  ---------------  ---------------  ---------------------------------------------------------
2574  30s ago    EquationOfState  ⏵ Waiting        Waiting for child processes: 2580, 2586, 2592, 2598, 2604
2580  28s ago    PwCalculation    ⏵ Waiting        Monitoring scheduler: job state RUNNING
2586  27s ago    PwCalculation    ⏵ Waiting        Monitoring scheduler: job state RUNNING
2592  25s ago    PwCalculation    ⏵ Waiting        Monitoring scheduler: job state RUNNING
2598  24s ago    PwCalculation    ⏵ Waiting        Monitoring scheduler: job state RUNNING
2604  22s ago    PwCalculation    ⏵ Waiting        Monitoring scheduler: job state RUNNING
Total results: 6
```

## Questions for Jul 13th meeting
* what to do with the APW specific parameters (RMT, r0 etc ) that are stored in the struct file?
* looping over volumes: Should we call something from AIIDA or just write our own loop and store the data?
* how input crystal structures will be supplied to us? (for the paper) (see https://arxiv.org/pdf/2105.05063.pdf)
* we should define `x` as a code and then `x sgroup` as a package (class)


- [x] what should we define as a "code" in code@host? (WIEN2k has many executables.): each executable is a code
- [x] how should we add the input crystal structure as a node to the providence graph? (as a file)
- [x] do we need AIIDA <-> ASE <-> WIEN2k structure converter? (ASE <-> WIEN2k works fine) ase_structure = structure.get_ase()
- [x] how results should be presented? table E vs V for each initial structure?
```
In [6]: result.get_dict()
Out[6]:
{'eos': [[137.84870014835, -1240.4759003187, 'eV'],
  [146.64498086438, -1241.4786547651, 'eV'],
  [155.807721341, -1242.0231198534, 'eV'],
  [165.34440034884, -1242.1847659475, 'eV'],
  [175.26249665852, -1242.0265883524, 'eV']]}
```

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

From a dicussion during tutorials: Could they create a plugin that subclasses StructureData? That way it could still be used by all calc plugins that use StructureData and they could add all functionalities from ASE that they want. maybe subclassing, maybe creating a separate object
