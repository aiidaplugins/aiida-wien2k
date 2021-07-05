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
* how input crystal structures will be supplied to us? (for the paper)
* do we need AIIDA <-> ASE <-> WIEN2k structure converter? (ASE <-> WIEN2k works fine)
* how results should be tresented? table E vs V for each initial structure?
