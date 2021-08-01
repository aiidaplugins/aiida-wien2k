## Questions
- [ ] Giovanni: One comment is that many other plugins avoid the explicit call to a calcfunction to convert an AiiDA StructureData to the internal code format, but just perform the conversion inside the `prepare_for_submission` of the first step.
- [ ] Names convention check

## Issues
- [ ] In `run_lapw` stdout/stderr are mixed up. It is potentially a problem when parsing error or checking status of execution
  ```
  (aiida) [rubel@gra-login3 ~]$ verdi node show 393
  Property     Value
  -----------  ------------------------------------
  type         Wien2kRunLapw
  state        Finished [0]
  ...

  Outputs          PK  Type
  -------------  ----  ----------
  remote_folder   394  RemoteData
  ...
  
  (aiida) [rubel@gra-login3 ~]$ verdi data remote show 394
  - Remote computer name:
    localhost
  - Remote folder full path:
    /scratch/rubel/aiida/work/f3/c0/5838-3e64-459b-93ec-7b4463c7cd02
  
  (aiida) [rubel@gra-login3 ~]$ cd /scratch/rubel/aiida/work/f3/c0/5838-3e64-459b-93ec-7b4463c7cd02
  (aiida) [rubel@gra-login3 5838-3e64-459b-93ec-7b4463c7cd02]$ ll
  total 49
  -rw-r----- 1 rubel rubel   806 Jul 15 10:22 _aiidasubmit.sh
  drwxr-x--- 2 rubel rubel 41472 Jul 15 10:22 case
  -rw-r----- 1 rubel rubel    55 Jul 15 10:22 _scheduler-stderr.txt
  -rw-r----- 1 rubel rubel     0 Jul 15 10:22 _scheduler-stdout.txt
  (aiida) [rubel@gra-login3 5838-3e64-459b-93ec-7b4463c7cd02]$ cat _scheduler-stderr.txt
   LAPW0 END
   LAPW1 END
   LAPW2 END
   CORE  END
   MIXER END
  ```
- [ ] Another case with `init_lapw`
  ```
  (aiida) [rubel@gra-login3 d4e7-03d1-4e1f-9bc9-24ea4f4f9814]$ cat _scheduler-stderr.txt
  NN ENDS
  NN ENDS
  LSTART ENDS
  KGEN ENDS
  ```
  While `_scheduler-stdout.txt` is empty
  ```
  (aiida) [rubel@gra-login3 d4e7-03d1-4e1f-9bc9-24ea4f4f9814]$ cat _scheduler-stdout.txt
  (aiida) [rubel@gra-login3 d4e7-03d1-4e1f-9bc9-24ea4f4f9814]$
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
conda create -n aiida -c conda-forge aiida-core aiida-core.services ase fuzzywuzzy
conda activate aiida
pip install psycopg2-binary==2.8.6
pip install psycopg2==2.8.6
reentry scan
```
Here `pip` is used to downgread `psycopg2` otherwise AiiDA does not work (problems with `postgresql`)

Launch database
```
cd /home/rubel/scratch/aiida
initdb -D mylocal_db
pg_ctl -D mylocal_db -l logfile start
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
verdi daemon start 2

```

## TU Wien
To connect via VNC
```
ssh -Y -L 5901:psi11:5901 uname@.....at
```
Launch VNC connection to `localhost:5901`
