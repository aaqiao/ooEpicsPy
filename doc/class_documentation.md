# Class Documentation for `ooepics`

This document provides detailed documentation for the classes and functions in the `ooepics` package.

## 1. LocalPV (`LocalPV.py`)
Implementation of a Local Process Variable (PV). It uses `RemotePV` internally to access the local PV but provides specific configurations for creating records.

### Class: `LocalPV`
#### Methods
- **`__init__(self, modStr, devStr, valStr, selItems, unitStr, pno, recTypeStr, descStr, enaSR=True, initVal=None, initProc=False)`**
  - Initializes a new LocalPV object and registers it in `LocalPV.LPVList`.
  - **Parameters:**
    - `modStr` (str): Module name.
    - `devStr` (str): Device name.
    - `valStr` (str): Value name.
    - `selItems` (list): Items for `mbbi` or `mbbo` records.
    - `unitStr` (str): Unit string.
    - `pno` (int): Number of points (elements).
    - `recTypeStr` (str): Record type (e.g., "ao", "ai", "bo", "waveform").
    - `descStr` (str): Description string.
    - `enaSR` (bool, optional): Enable Save/Restore. Defaults to `True`.
    - `initVal` (any, optional): Initial value.
    - `initProc` (bool, optional): Initial process. Defaults to `False`.

- **`read(self, return_str=False, use_monitor=False)`**
  - Reads the value of the local PV.
  - **Returns:** Result from `self.pv.read()`.

- **`write(self, value, wait=False, timeout=1.0)`**
  - Writes a value to the local PV.

- **`monitor(self, cbFun=None, cbArgList=None)`**
  - Sets up a monitor callback for the PV.

- **`get_pv_name(self)`**
  - Returns the full PV name.

#### Class Methods
- **`show(cls)`**: Displays all local PVs.
- **`init_wfs(cls)`**: Initializes waveform PVs with zeros.
- **`gen_db(cls, fileName)`**: Generates the EPICS database file (`.db` or `.template`).
- **`gen_srreq(cls, fileName)`**: Generates the Save/Restore request file.
- **`gen_arch(cls, fileName)`**: Generates the Archiver configuration file (placeholder).

---

## 2. RemotePV (`RemotePV.py`)
Python-based implementation of a Remote PV using PyEpics.

### Class: `RemotePV`
#### Methods
- **`__init__(self, pvName, local=False, auto_mon=None)`**
  - Initializes a RemotePV object.
  - **Parameters:**
    - `pvName` (str): Name of the PV.
    - `local` (bool): Flag to indicate if it is a local PV (used for filtering in `show`).
    - `auto_mon` (bool): Auto monitor setting.

- **`create(self)`**
  - Creates the underlying `epics.PV` object.

- **`is_connected(self)`**
  - Checks if the PV is connected.

- **`read(self, return_str=False, use_monitor=False, timeout=1.0)`**
  - Reads the PV value, timestamp, severity, and status.
  - **Returns:** `[value, timestamp, severity_ok, status_ok]`

- **`write(self, value, wait=False, timeout=1.0)`**
  - Writes a value to the PV.

- **`monitor(self, cbFun=None, cbArgList=None)`**
  - Sets up a callback for value changes.

#### Class Methods
- **`connect(cls)`**: Creates/Connects all registered RemotePVs.
- **`show(cls, local=False)`**: prints the status and value of all registered PVs.

---

## 3. Application (`Application.py`)
Manages the application thread, jobs, and communication structure.

### Class: `Application`
#### Methods
- **`__init__(self, appName, modName)`**
  - Initializes the application.

- **`registJob(self, job, cmdStr="EXE", mutex=None)`**
  - Registers a job and creates a command PV ("CMD-EXE" by default) to trigger it.

- **`registJobExtTrigPV(self, job, extPVList=[], mutex=None)`**
  - Registers a job triggered by external PVs.

- **`registJobPeriodic(self, job, period_s=1.0)`**
  - Registers a job to run periodically using a timer.

- **`letGoing(self)`**
  - Starts the application thread and timers.

- **`stop(self)`**
  - Stops the application.

#### Class Methods
- **`generateSoftIOC(cls, softIOCName, ...)`**: Generates the startup scripts and database files for a Soft IOC.

#### Functions
- **`AppThreadFunc(app)`**: Main loop for the application thread, processing the message queue.
- **`JobCmdCbFunc(cbArgs)`**: Callback for job command PVs.
- **`RunPeriodicJob(job)`**: Wrapper to execute periodic jobs.

---

## 4. FSMLite (`FSMLite.py`)
A lightweight Finite State Machine implementation.

### Class: `FSMLite`
#### Methods
- **`__init__(self, mod_name='', fsm_name='', timer_intv=1, max_try=3, states=[], state_tr={}, mon_func=None)`**
  - Initializes the FSM.
  - Creates control PVs: `START`, `STOP`, `RESET`, `MAX-TRY`, `CUR-STATE`, `FSM-MSG`, `STAY-TIME`, `ENTRY-OK`, `TRANS-OK`, `EXIT-OK`, `RUNNING`.

- **`letGoing(self)`**: Starts the FSM thread.
- **`start(self)`**: Starts the FSM (timer and logic).
- **`stop(self, reason='user command')`**: Stops the FSM.
- **`reset(self)`**: Resets the FSM to the initial state.
- **`after(self, dt)`**: Checks if the FSM has stayed in the current state for `dt` seconds.
- **`init_state(self, state_ini)`**: Forces the FSM to a specific state.

---

## 5. Job (`Job.py`)
Base class for jobs executed by the `Application`.

### Class: `Job`
#### Methods
- **`__init__(self, modName, jobName)`**
  - Initializes the Job.
- **`execute(self, cmdId=0, dataBus=None)`**
  - Abstract method to be implemented by subclasses. Executes the job logic.

---

## 6. RepeatedTimer (`RepeatedTimer.py`)
A timer that repeats its execution.

### Class: `RepeatedTimer`
#### Methods
- **`__init__(self, interval, user_cb, *args, **kwargs)`**
  - Initializes the timer.
- **`start(self, new_intv=None)`**: Starts or restarts the timer.
- **`stop(self)`**: Stops the timer.
- **`reset(self)`**: Resets the stop command flag.

---

## 7. RecordTemplate (`RecordTemplate.py`)
Helper to generate EPICS record definitions.

#### Functions
- **`generateRecord(pvName, selItems, unitStr, pointNum, recordType, descStr, initVal, initProc)`**
  - Generates a string containing the database record definition.

