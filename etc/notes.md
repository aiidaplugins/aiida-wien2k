## Intallation
### AiiDA installation steps
```
conda create -n aiida -c conda-forge aiida-core aiida-core.services ase fuzzywuzzy
conda activate aiida
pip install psycopg2-binary==2.8.6
pip install psycopg2==2.8.6
reentry scan
```
Here `pip` is used to downgread `psycopg2` otherwise AiiDA does not work (problems with `postgresql`)

Launch database
```
cd /eos/rubel
initdb -D mylocal_db
pg_ctl -D mylocal_db -l logfile start
cp /eos/rubel/aiida-wien2k/etc/rabbitmq.conf /eos/rubel/anaconda3/envs/aiida/etc/rabbitmq # path is system-specific
rabbitmq-server -detached
```
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
Launch AiiDA deamon
```
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
Test computer
```
verdi computer test localhost
```
Set up codes (do for all codes `aiida_wien2k/configs/codes/*.yml`)
```
cd aiida_wien2k/configs/codes/
verdi code setup --config run_lapw.yml # edit remote_abs_path, prepend_text!
```

### Install aiida-wien2k plugin package
```
git clone https://github.com/rubel75/aiida-wien2k
cd aiida-wien2k
pip install -e .
reentry scan
verdi daemon restart --reset
```
(in case of troubles try `pip install -e . -vvv` and also locate `/path/to/anaconda3/envs/aiida/lib/python3.8/site-packages/aiida-wien2k.egg-link` file)

## Run test case
```
cd aiida-wien2k/etc
verdi run launch_scf_workchain.py # SCF run Si (1 iteration only)
```

## In case of problems
```
verdi daemon stop
rabbitmqctl shutdown
pg_ctl -D mylocal_db -l logfile stop
pg_ctl -D mylocal_db -l logfile start
rabbitmq-server -detached
verdi daemon start 6
```
RubbitMQ (log files, configs, etc)
```
rabbitmq-diagnostics status
vim ~/anaconda3/envs/aiida/var/lib/rabbitmq/mnesia/rabbit@psi11/cluster_nodes.config
```

## Setting up another AiiDA profile
List all profiles (or projects)
```
verdi profile list
```
Show details of a profile `oleg`
```
verdi profile show oleg
```
New setup on `psi12`
```
initdb -D mylocal_db_psi12
pg_ctl -D mylocal_db_psi12 -l logfile start
rabbitmq-server -detached
verdi quicksetup
  Info: enter "?" for help
  Info: enter "!" to ignore the default and set no value
  Profile name [quicksetup]: psi12
  Email Address (for sharing data) [rubelo@mcmaster.ca]:
  First name [Oleg]:
  Last name [Rubel]:
  Institution [McMaster]:
  Success: created new profile `psi12`.
  Info: migrating the database.
  ...
  Success: database migration completed.
verdi -p psi12 daemon start 2
verdi profile list
  Info: configuration folder: /eos/rubel/.aiida
  * oleg
    psi12
verdi profile show psi12
  Info: Profile: psi12
  ----------------------  -----------------------------------------------
  aiidadb_backend         django
  aiidadb_engine          postgresql_psycopg2
  aiidadb_host
  aiidadb_name            psi12_rubel_2fa9a0278303c4aa880978e55540c74d
  aiidadb_pass            F37toZ9A4yGou5F2
  aiidadb_port            5432
  aiidadb_repository_uri  file:///eos/rubel/.aiida/repository/psi12
  aiidadb_user            aiida_qs_rubel_2fa9a0278303c4aa880978e55540c74d
  broker_host             127.0.0.1
  broker_password         guest
  broker_port             5672
  broker_protocol         amqp
  broker_username         guest
  broker_virtual_host
  default_user_email      rubelo@mcmaster.ca
  options                 {}
  profile_uuid            e23f410a63224206ad86388666b48caa
  ----------------------  -----------------------------------------------
verdi -p psi12 status
 ✔ config dir:  /eos/rubel/.aiida
 ✔ profile:     On profile psi12
 ✔ repository:  /eos/rubel/.aiida/repository/psi12
 ✔ postgres:    Connected as aiida_qs_rubel_2fa9a0278303c4aa880978e55540c74d@None:5432
 ✔ rabbitmq:    Connected as amqp://guest:guest@127.0.0.1:5672?heartbeat=600
 ✔ daemon:      Daemon is running as PID 8297 since 2021-09-22 01:09:37
verdi -p psi12 process list -a
```
Execute comand for a specific profile
```
verdi -p <profile> process list
```

Migrate database
```
verdi -p <profile_name> database migrate
```


## Other useful comands
CPU, memory, disk usage
```
vmstat -w 2
```
Verdi tab completion
```
eval "$(_VERDI_COMPLETE=source verdi)"
```
Verdi import structures
```
verdi archive import /eos/rubel/commonwf-oxides-scripts/1-preliminary/commonwf-oxides_set1_structures.aiida
```

## TU Wien
To connect via VNC
```
ssh -Y -L 5901:psi11:5901 uname@.....at
```
Launch VNC connection to `localhost:5901`

## Other
GET THE UNIQUE VALUES (DISTINCT ROWS) OF A DATAFRAME IN PYTHON PANDAS:
https://www.datasciencemadesimple.com/get-unique-values-rows-dataframe-python-pandas/

Launch AiiDA common workflow
```
from aiida_common_workflows.workflows.relax.wien2k import Wien2kCommonRelaxWorkChain
inputgen = Wien2kCommonRelaxWorkChain.get_input_generator()
from aiida.engine import submit
builder = inputgen.get_builder(structure=load_node(72328),engines= {
        'x-sgroup': {
            'code': 'wien2k-x-sgroup@localhost'
        },
        'init_lapw': {
            'code': 'wien2k-init_lapw@localhost'
        },
        'relax': {
            'code': 'wien2k-run_lapw@localhost'
        }
})
submit(builder)
```
