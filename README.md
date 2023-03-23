# aiida-wien2k
It is a [WIEN2k](http://susi.theochem.tuwien.ac.at) plug-in for [AiiDA](https://www.aiida.net) workflow management developed in conjunction with the [Common workflow project](https://github.com/aiidateam/aiida-common-workflows). It is designed to calculate an equation of state (Etot vs volume) for any structure supplied in AiiDA format by running a very basic, yet extremely accurate, self-consistency field cycle. Limitations are a uniform scaling of all lattice parameters (applicable to cubic structures), no relaxation of atomic positions, no magnetism, no spin-orbit coupling. It is meant for DFT users who have no idea about WIEN2k, but still want to run EoS for benchmarking purposes using various DFT codes, including WIEN2k. WIEN2k version 22.2 (or higher) should be used (prior versions are incompatible).

The Materials Cloud “AiiDA common workflows verification” database (https://acwf-verification.materialscloud.org) contains WIEN2k results obtained using this workflow. The data are published and discussed in the article: E. Bosoni et al., Comprehensive verification of all-electron and pseudopotential density functional theory (DFT) codes via universal common workflows., in preparation (2023)

Developers: Oleg Rubel and Peter Blaha

Special thanks for the guidance through development: Emanuele Bosoni and Giovanni Pizzi
