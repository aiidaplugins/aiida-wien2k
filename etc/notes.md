## Questions
- [ ] Giovanni: One comment is that many other plugins avoid the explicit call to a calcfunction to convert an AiiDA StructureData to the internal code format, but just perform the conversion inside the `prepare_for_submission` of the first step.
- [ ] Names convention check

## Issues
- [ ] stdout/stderr mixed up. It is potentially a problem when parsing error or checking status of execution
```
In [1]: fdata = load_node(395)
In [2]: fdata
Out[2]: <FolderData: uuid: dead272c-7735-4d25-9226-a8f4a5332765 (pk: 395)>
In [6]: fdata.list_object_names()
Out[6]:
['_scheduler-stderr.txt',
 '_scheduler-stdout.txt',
 'case.scf',
 'dstart.error',
 'lapw0.error',
 'lapw1.error',
 'lapw2.error',
 'lcore.error',
 'mixer.error']
In [11]: errfile = fdata.get_object_content('_scheduler-stderr.txt')
In [12]: errfile
Out[12]: ' LAPW0 END\n LAPW1 END\n LAPW2 END\n CORE  END\n MIXER END\n'
```

## Notes
* From a discussion during tutorials: Could they create a plugin that subclasses StructureData? That way it could still be used by all calc plugins that use StructureData and they could add all functionalities from ASE that they want. maybe subclassing, maybe creating a separate object
* what to do with the APW specific parameters (RMT, r0 etc ) that are stored in the struct file?


## TODOs:
- [ ] register `aiida-wien2k` in AiiDA repository 
- [ ] debugging AiiDA with VSCode https://marketplace.visualstudio.com/items?itemName=chrisjsewell.aiida-explore-vscode
- [ ] use `fuzzywuzzy` for error handeling (https://github.com/seatgeek/fuzzywuzzy)
- [ ] submission of parallel calculations (EOS example; see eos_workchain.py)

## Intallation
### AiiDA installation steps
```
conda create -n aiida -c conda-forge aiida-core aiida-core.services
conda activate aiida
pip install psycopg2-binary==2.8.6
pip install psycopg2==2.8.6
reentry scan
```
Here `pip` is used to downgread `psycopg2` otherwise AiiDA does not work (problems with `postgresql`)

Set up new profile
```
(aiida) [rubel@gra-login3 aiida]$ verdi quicksetup
Info: enter "?" for help
Info: enter "!" to ignore the default and set no value
Profile name [quicksetup]: oleg
Email Address (for sharing data): rubelo@....ca
First name: Oleg
Last name: Rubel
Institution: McMaster
...
```
Lunch database and AiiDA deamon
```
cd /home/rubel/scratch/aiida
initdb -D mylocal_db
pg_ctl -D mylocal_db -l logfile start
rabbitmq-server -detached
verdi daemon start 2
```
Check AiiDA status
```
(aiida) [rubel@gra-login3 aiida]$ verdi status
 ✔ config dir:  /home/rubel/.aiida
 ✔ profile:     On profile oleg
 ✔ repository:  /home/rubel/.aiida/repository/oleg
 ✔ postgres:    Connected as aiida_qs_rubel_460c5d44ef6f9a34ffc5c554d91656f8@None:5432
 ✔ rabbitmq:    Connected as amqp://guest:guest@127.0.0.1:5672?heartbeat=600
 ✔ daemon:      Daemon is running as PID 22409 since 2021-06-20 22:40:29
```
Set up computer `localhost`
```
cd aiida_wien2k/configs/computers/
verdi computer setup --config localhost.yml # edit work_dir!
```
Configure computer
```
verdi computer configure local localhost
Info: enter "?" for help
Info: enter "!" to ignore the default and set no value
Use login shell when executing command [True]:
Connection cooldown time (s) [0.0]:
Info: Configuring computer localhost for user rubelo@....ca.
Success: localhost successfully configured for rubelo@....ca
```
Set up codes (do for all codes `aiida_wien2k/configs/codes/*.yml`)
```
cd aiida_wien2k/configs/codes/
verdi code setup --config run_lapw.yml # edit remote_abs_path, prepend_text!
```

## Install aiida-wien2k plugin package
```
cd aiida-wien2k
pip install .
reentry scan
```

## Test case
```
cd aiida-wien2k/etc
verdi run launch_scf_workchain.py # SCF run Si (1 iteration only)
```
