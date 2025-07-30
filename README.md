# AIRWORTHINESS TRACKING MADE EASY

#### Video Demo:  https://youtu.be/5_XgyKgEt8w

#### Description:

###### The Problem

To be *airworthy*, that is legal to fly, general aviation airplanes must be strictly maintained on a regular basis according to FAA regulations and manufacture's recommendations. Knowing when and if all of the required maintenance actions have been complied with creates a burden for the operator and pilot-in-command. This project creates a tool for dynamically configuring, tracking and logging the maintenance status of critical aircraft systems and subsystems.

An airplane can be modeled as a collection of systems. These systems can be grouped into major systems such as engines, propellers, avionics and airframe. Within each of the these major systems, several subsystems must be regularly maintained. Each maintenance action must be logged for every system or subsystem  with details about the action and any parts and materials used. Typically these logs are chronological, verbose and scattered across three or more active logbooks as well as inactive logbooks that have been filled and closed. Finding the airworthiness status of a particular subsystem can be frustrating, time-consuming and unproductive.

Before each and every flight, the pilot-in-command is required to insure that all required actions have been implemented, logged and properly signed-off.  This can be a cumbersome pre-flight action since it requires searching through multiple logbooks to find the most recent maintenance action for each subsystem and comparing the time, date or flight-hours, of that action to the current aircraft time and relevant maintenance interval.  Additionally, the number of days or flight hours until the next required action must be compared to the forthcoming missions to prevent grounding of the aircraft during the middle of a mission.

My project’s scripts make determination of airworthiness quick and easy by creating, configuring and updating an Airplane Object thereby enabling continuous tracking and logging of maintenance actions.  The scripts also generate PDF reports for configuration, maintenance status a summary log of each maintenance action.

##### The Approach

A command line interface (CLI) is provided to enter configuration, maintenance and reporting actions.  The CLI is also used to query a google sheet which contains the airplane’s last flight date and cumulative flight-hours.  At any time, the CLI can be used to request PDF reports of configuration, status and a summary log.  When a particular airplane is initialized, a file is created with a given path and N-number name.  One file for each airplane of interest.

The project folder contains multiple python scripts, a `README.md` file, a folder for airplanes and reports, and a list of pip installable libraries in `requirements.txt`.

##### Files

###### `project.py`

`project.py` is the primary script.  It contains the `main()` function.  The `argparse` library is used to define and parse the CLI commands.  Commands are entered from the terminal, parsed by this script and, if valid, executed.

###### `airplane.py`

The `airplane.py` script contains the System Class and Airplane Class and their methods.  The System class simply holds subsystem objects in a dictionary.  The Airplane Class holds all Major Systems in a dictionary with a limited set of keys.   It also holds airplane attributes such as N-number and cumulative flight hours.   This script has methods for saving an Airplane Objects as a pickle file, loading an Airplane Object from a file, getting current Airplane times from a Google Sheet, validating Airplane times, setting the Airplane’s purchase times, generating and saving reports, configuring systems, and subsystems,  logging and recording maintenance actions for systems and subsystems.

Maintenance intervals are a quantity of days, calendar months (FAA definition), years or flight hours.

ValueErrors are raised when detected.

###### `subsystems.py`

The `subsystem.py` script contains the Subsystem Class and methods for installing a subsystem, updating the time of a installation, validating and logging maintenance actions with optional brief notes, calculating maintenance status and the age of a Subsystem.

Major Systems, see `airplane.py` inherit all of the Subsystem Class methods.

ValueErrors are raised when detected.

###### `report.py`

The `report.py` script generates three type of reports -- configuration, maintenance status, maintenance log summary.  The `all` option will generate all three of the reports.

The Report Lab library is used to style the reports and handle multipage flow.

The maintenance table function constructs a table of *due dates* listing the subsystems in each major system.  This table used by the `report_maintenance` function for styling.  Similar table are created and formatted for configuration and logs.

Tables are sorted by due date or subsystem name.

A function is provided to generate custom  headers and footers for each page with page numbers and the date created.

###### `test_xxxx.py`

Test scripts for the project, airplane, subsystem and report scripts are included in the folder.  Run each of these with pytest.  They are not yet comprehansive.

###### `planes/` and `planes/reports/`

The `planes/` folder holds the pickle Airplane objects.  The registration number (N-number) is used with a `.pkl` extension.  Additionally, reports are placed in the `planes/reports` folder.

###### `xxxx commands.txt`

Files named `xxxx commands.txt` hold a series of commands that can be processed by `project.py`  using `source xxxx commands.txt` where xxxx is the registration.  Examples for N527W and N485DV are given.

###### `help.txt`

The `help.txt` file contains the output of `python project.py --help > help.txt`  positional arguments, options, configuration commands, maintenance commands and report commands are detailed.
#### Quick Start

The `N527W commands.txt` file can serve as a guide for a quick start


TODO
*  Graphical User Interface
* Deploy to a User Community
* Log Commands
* Adopt json instead of pickle
* BUG - when to use interval? maintenance action to set interval?
* BUG - time in service vs inspection interval, remove overlap



