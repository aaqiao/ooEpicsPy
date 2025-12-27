# ooEpics Class Documentation

This document provides detailed documentation for the classes and modules within the `ooepics` package.

## List of Classes
- [Application](#class-application)
- [LocalPV](#class-localpv)
- [RemotePV](#class-remotepv)
- [FSMLite](#class-fsmlite)
- [Job](#class-job)
- [RepeatedTimer](#class-repeatedtimer)
- [RecordTemplate](#module-recordtemplate)

---

## Class `Application`
defined in `Application.py`

The main application class for creating Epics Soft IOCs. It manages tasks (Jobs), periodic executions, and necessary EPICS file generation.

### Constructor
`__init__(self, appName, modName)`
- **appName** (`str`): Name of the application.
- **modName** (`str`): Name of the module.

### Methods

#### `registJob(self, job, cmdStr="EXE", mutex=None)`
Registers a job to be executed upon a PV command.
- **job** (`Job`): The Job object to execute.
- **cmdStr** (`str` or `list`): Command string suffix(es) for the PV. E.g., if "EXE", creates `CMD-EXE`. Can be a list of strings for multiple commands.
- **mutex** (`threading.Lock`, optional): Mutex to protect job execution.

#### `registJobExtTrigPV(self, job, extPVList=[], mutex=None)`
Registers a job triggered by external PVs.
- **job** (`Job`): Job object.
- **extPVList** (`list` of `RemotePV`): List of external PVs that trigger this job.
- **mutex**: Mutex for thread safety.

#### `registJobPeriodic(self, job, period_s=1.0)`
Registers a job to run periodically.
- **job** (`Job`): Job object.
- **period_s** (`float`): Period in seconds (min 0.1s).

#### `letGoing(self)`
Starts the application thread and timer threads. Needs to be called after registration.

#### `generateSoftIOC(cls, softIOCName, py_cmd='python', only_db=False, version=None, release_time=None)`
**Class Method**. Generates the folder structure, startup scripts, and EPICS database (`.template`) files for the Soft IOC.
- **softIOCName** (`str`): Name of the IOC.
- **py_cmd** (`str`): Command to run python (default 'python').
- **only_db** (`bool`): If True, only generates DB files, no startup script logic.
- **version**: Optional version string for IOC PV.
- **release_time**: Optional release time string for IOC PV.

---

## Class `LocalPV`
defined in `LocalPV.py`

Represents a local Process Variable in the Soft IOC. It wraps a `RemotePV` connected to `localhost`.

### Constructor
`__init__(self, modStr, devStr, valStr, selItems, unitStr, pno, recTypeStr, descStr, enaSR=True, initVal=None, initProc=False)`
- **modStr**, **devStr**, **valStr**: Parts of the PV name (`Mod-Dev:Val` or `Mod:Val`).
- **selItems** (`list`): List of enum strings for `mbbi`/`mbbo` records.
- **unitStr** (`str`): EGU (Engineering Units).
- **pno** (`int`): Number of elements (for waveforms).
- **recTypeStr** (`str`): Record type (e.g., 'ao', 'bi', 'waveform').
- **descStr** (`str`): Description field.
- **enaSR** (`bool`): Enable Save/Restore.
- **initVal**: Initial value.
- **initProc** (`bool`): Process at initialization (`PINI`).

### Methods
- **`read(return_str=False, use_monitor=False)`**: Wrapper for `RemotePV.read()`.
- **`write(value, wait=False, timeout=1.0)`**: Wrapper for `RemotePV.write()`.
- **`monitor(cbFun=None, cbArgList=None)`**: Wrapper for `RemotePV.monitor()`.
- **`gen_db(fileName)`** (Class Method): Generates the EPICS DB file from all defined `LocalPV`s.
- **`gen_srreq(fileName)`** (Class Method): Generates Save/Restore request file.

---

## Class `RemotePV`
defined in `RemotePV.py`

Wrapper around `epics.PV` to handle channel access.

### Constructor
`__init__(self, pvName, local=False, auto_mon=None)`
- **pvName** (`str`): Full PV name.
- **local** (`bool`): Flag indicating if it is local.
- **auto_mon**: Auto monitor setting for pyepics.

### Methods
- **`create()`**: creates the underlying `epics.PV` object.
- **`read(return_str=False, use_monitor=False, timeout=1.0)`**: Returns `[value, timestamp, severity, status]`.
    - `severity`: True if severity == 0 (No Alarm), else False.
    - `status`: True if status is normal (not basic comm errors), else False.
- **`write(value, wait=False, timeout=1.0)`**: Writes value to PV. Returns `True` on success.
- **`monitor(cbFun=None, cbArgList=None)`**: Sets up a monitor callback.
- **`is_connected()`**: Checks connection status.
- **`connect()`** (Class Method): Batch creates all registered `RemotePV` objects.

---

## Class `FSMLite`
defined in `FSMLite.py`

Finite State Machine implementation with integrated PV interfaces.

### Constructor
`__init__(self, mod_name='', fsm_name='', timer_intv=1, max_try=3, states=[], state_tr={}, mon_func=None)`
- **mod_name**, **fsm_name**: Used for naming internal control PVs.
- **timer_intv** (`float`): Timer interval for the FSM thread.
- **max_try** (`int`): Max retries for transitions.
- **states** (`list`): List of state names (strings).
- **state_tr** (`dict`): Transition Dictionary. format: `{ 'StateName': {'entry': func, 'exit': func, 'transit': func} }`.
- **mon_func**: Function called when FSM is idle (not running).

### Methods
- **`start()`**: Starts the FSM (timer and logic).
- **`stop(reason)`**: Stops the FSM.
- **`reset()`**: Resets state to initial.
- **`letGoing()`**: Starts the background thread.
- **`postMsg(msg)`**: Logs message to stdout and to `FSM-MSG` PV.
- **`init_state(state_ini)`**: Force sets initial state.

---

## Class `Job`
defined in `Job.py`

Base class for execution units.

### Constructor
`__init__(self, modName, jobName)`

### Methods
#### `execute(self, cmdId=0, dataBus=None)`
**Overridable**. The main logic method.
- **cmdId**: ID of the command that triggered this execute (useful if multiple commands map to one job).
- **dataBus**: Context data (usually None in standard `Application` usage).
- **Returns**: `True` if success.

---

## Class `RepeatedTimer`
defined in `RepeatedTimer.py`

Thread-based timer that repeats itself.

### Constructor
`__init__(self, interval, user_cb, *args, **kwargs)`
- **interval**: Seconds.
- **user_cb**: Callback function to execute.

### Methods
- **`start(new_intv=None)`**: Starts (or restarts) the timer.
- **`stop()`**: Cancels the timer.
- **`reset()`**: Resets stop flags.

---

## Module `RecordTemplate`
defined in `RecordTemplate.py`

### Function `generateRecord`
`generateRecord(pvName, selItems, unitStr, pointNum, recordType, descStr, initVal, initProc)`
Generates the text body for an EPICS `.db` record entry.
- Returns: `str` containing the record definition.
- detailed handling for `ao`, `ai` (precision), `mbbo`/`mbbi` (state strings), `waveform` (NELM, FTVL), etc.
