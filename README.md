# aiida-wien2k
WIEN2k plug-in for AiiDA workflow management

## Questions for Jul 13th meeting
* AIIDA <-> ASE <-> WIEN2k structure converter.
* what to do with the APW specific parameters (RMT, r0 etc ) that are stored in the struct file?
* looping over volumes: Should we call something from AIIDA or just write our own loop and store the data?
* what should we define as a "code" in code@host? WIEN2k has many executables.
