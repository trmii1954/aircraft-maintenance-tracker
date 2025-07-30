# Airplane Management

import sys
import re
import os
import pickle
import argparse
from argparse import ArgumentTypeError
from argparse import RawTextHelpFormatter
from airplane import Airplane
from dateutil import parser



def parse_command():
    """
    registration    N-number
    folder          folder to store plane objects
    """
    parser = argparse.ArgumentParser(
        description="CLI to Manage and Report Airplane Airworthiness", formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "registration", help="The FAA N-number of the Airplane", type=n_number
    )
    parser.add_argument(
        "folder", type=directory_path, help="The folder to store planes and reports"
    )
    parser.add_argument(
        "-k",
        "--make",
        help="make model serial option for initialization, config and maintenance",
        nargs=3,
        metavar=("make", "model", "serial"),
    )

    parser.add_argument(
        "-t",
        "--time",
        help="when did the action happen",
        nargs=3,
        metavar=("date", "hobbs", "flight"),
    )

    config_group = parser.add_argument_group(
        "Configuration Commands\n subsequent installations can be made with  --maintenance"
    )
    subsystem_config_group = parser.add_argument_group(
        "Subsystem Configuration Commands"
    )
    report_group = parser.add_argument_group("Report Options")
    maintenance_group = parser.add_argument_group("Maintenance Options")

    # initialization section
    config_group.add_argument(
        "-i",
        help="Plane and File initialization. Manufacture date.\nHobbs and Flight Hours default to 0.0 Use with --make.\nDELETES ALL PRIOR CONFIG.  Use -z to modify times.",
        nargs=1,
        metavar=("manufacture_date"),
    )
    # purchase date
    config_group.add_argument(
        "-z",
        "--day_zero",
        action="store_true",
        help="set Airplane day zero date, hobbs and flight hours (purchase). Use with --time",
    )

    config_group.add_argument(
        "-a",
        "--addsystem",
        help="add major system, e.g. engine_left. Use with --make",
        nargs=1,
        metavar=("system_name"),
        type=str,
    )

    # subsystem configuration commands, add subsystem to a major system
    config_group.add_argument(
        "-b",
        "--addsubsystem",
        help="add subsystem to a major system. Use with --make.",
        nargs=1,
        metavar=("system:subsystem"),
    )
    config_group.add_argument(
        "--offset",
        help="prior time-in-service when installed defaults to 0.0",
        type=float,
        default=0.0,
    )
    # inerval is an option when adding a subsystem
    config_group.add_argument(
        "-v",
        "--interval",
        help="set maintenance interval for system or subsystem\n  required for due report\n  units are calendar_months, years or flight_hours",
        nargs=2,
        metavar=("quantity", "units"),
        default=[0, "years"],
    )

    # report section
    report_group.add_argument(
        "-r",
        "--report",
        help="generate report(s)",
        type=str,
        choices=["all", "configuration", "maintenance", "log"],
    )
    report_group.add_argument(
        "-s", "--sheet", help="set google sheet-ID command", type=str
    )

    # fetch current flight hours command
    report_group.add_argument(
        "-u",
        "--update",
        help="update hobbs and flight hours from google sheet log",
        action="store_true",
    )

    # maintenance commands
    maintenance_group.add_argument(
        "-m",
        "--maintenance",
        help="action with note\n    must specify --time and --make\n    optional --offset and --interval\n    actions: install,replace,interval,repair,routine,troubleshoot",
        nargs=2,
        metavar=("system:subsystem", "action:note"),
    )

    return parser.parse_args()


def n_number(registration):
    """
    N-Numbers consist of a series of alphanumeric characters. U.S. registration numbers may not
    exceed five characters in addition to the standard U.S. registration prefix letter N.
      These characters may be:
        One to five numbers (N12345)
        One to four numbers followed by one letter (N1234Z)
        One to three numbers followed by two letters (N123AZ)
    To avoid confusion with the numbers one and zero, the letters I and O are not to be used.
    An N-Number may not begin with zero. You must precede the first zero in an N-Number with
    any number 1 through 9. For example, N01Z is not valid.
    """
    pattern = r"(^N[1-9][0-9]{0,3}[A-HJ-NP-Z]$)|(^N[1-9][0-9]{0,2}[A-HJ-NP-Z]{2}$)|(^N[1-9][0-9]{0,4}$)"
    match = re.match(pattern, registration)
    if match:
        return registration
    else:
        raise ArgumentTypeError(
            f"{registration} is invalid. Registration must be a valid FAA N-Number"
        )


def airplane_time(times):
    if times:
        try:
            # Split the input into three parts and apply different types
            # First value as string date, zero fill month and day if necessary
            zero_fill_date = "-".join(part.zfill(2) for part in times[0].split("-"))
            day = parser.isoparse(zero_fill_date).strftime("%Y-%m-%d")
            hobbs = float(times[1])  # Second value as float
            flight = float(times[2])  # Third value as float
            return (day, hobbs, flight)
        except (ValueError, IndexError, TypeError):
            raise argparse.ArgumentTypeError(
                "-t args must be of type ISO 8601 tbd date, float, float"
            )
    else:
        sys.exit("-t arguments are missing")

def action_split_verify(action):

    ACTIONS = (
        "install",
        "replace",
        "interval",
        "repair",
        "routine",
        "troubleshoot",
    )

    match = re.match("^(.*):(.*)", action)
    if match:
        a = match.group(1)
        note = match.group(2)
    else:
        a = action
        note = ""
    if a in ACTIONS:
        return a, note
    else:
        raise ValueError(f"Action {a} not in {ACTIONS}")



def directory_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory path.")
    if path[-1:] == "/":
        return path
    else:
        return path + "/"


def get_plane(registration, folder):

    try:
        with open(f"{folder}{registration}.pkl", "rb") as file:
            my_plane = pickle.load(file)
    except FileNotFoundError:
        sys.exit(f"No such file: {folder}{registration}.pkl")
    else:
        return my_plane


def main():

    try:
        args = parse_command()
    except SystemExit as e:
        if e.code == 2:
            print("\nMissing required arguments, invalid argument values, unrecognized arguments.")
            print(f"Command Argument Error: {" ".join(sys.argv)}")
        sys.exit(f"SystemExit with code: {e.code}")

    print("*"*30)
    print(f"\"{" ".join(sys.argv)}\" command successfully parsed")

    # initialize or retrieve plane
    if args.i:
        # --make option must be used with -i
        if args.make:
            #warn user about consequence of initialization
            go = input("Initialization will clear all prior actions.  To proceed enter \'Y\' : ")
            if go == "Y":
                try:
                    my_plane = Airplane(*args.make, *args.i, args.registration, args.folder)
                except ValueError as e:
                    sys.exit(f"Value Error {e}")
                print(
                    f"Initialization success.  {args.registration} has been FULLY initialized."
                )
            else:
                sys.exit(f"You entered {go}.  No action taken.")
        else:
            sys.exit("--make option must be used with -i")
    else:
        # get the object for the requested plane
        # will exit if no file
        my_plane = get_plane(args.registration, args.folder)

    if args.sheet:
        """set google sheet ID"""
        my_plane.set_sheet_id(args.sheet)
        my_plane.put_plane()

    if args.day_zero:
        """set day zero flight hours and hobbs hours using google sheet ID"""
        try:
            day, hobbs, flight = airplane_time(args.time)
            my_plane.set_day_zero(day, hobbs, flight)
        except ValueError as e:
            sys.exit(f"ValueError: {e}")
        my_plane.put_plane()

    if args.update:
        """update flight hours and hobbs hours using google sheet ID"""
        try:
            h, f, d = my_plane.get_current_hours()
        except:
            sys.exit("Could not get Hobbs and Flight Hours from Google Sheet")

        try:
            # setter for Airplane attribute screens hours
            my_plane.flight_hours = f
            my_plane.hobbs_hours = h
            my_plane.last_flight_date = d
        except:
            sys.exit(f"Cannot update Hobbs={h} or Flight={f}")

        print(f"Update success!  New Hobbs: {h}, New Flight: {f}, Last Flight on {d}")
        my_plane.put_plane()

    if args.addsystem:
        # system must be one of airframe, engine, propeller or avionics
        if args.make:
            # --make option must be used with --addsystem
            try:
                my_plane.configure_major_system(
                    *args.addsystem, *args.make, *args.interval
                )  # system, name, make, model, serial, plane
                my_plane.put_plane()
            except TypeError as e:
                sys.exit(f"Type Error: {e}")
            except ValueError as e:
                sys.exit(f"Value Error: {e}")
        else:
            sys.exit("No action:  --make option must be used with --addsystem")

    if args.addsubsystem:
        # subsystem must be added to a system
        if args.make:
            # --make option must be used with --addsystem
            try:
                my_plane.configure_subsystem(*args.addsubsystem, *args.make, *args.interval)
                my_plane.put_plane()
            except TypeError as e:
                sys.exit(f"Add Subsystem Type Error: {e}")
            except ValueError as e:
                sys.exit(f"Add Subsystem Value Error: {e}")
        else:
              sys.exit("No action:  --make option must be used with --addsubsystem")

    # System or Subsystem Name, Action:note, Date, Hobbs-Hours, Flight-Hours, Offset
    # --make is needed for installation or replacement
    if args.maintenance:
        try:
            day, hobbs, flight = airplane_time(args.time)
            action, note = action_split_verify(args.maintenance[1])
            system, subsystem = my_plane.system_split(args.maintenance[0])
            if not args.make:
                if action == "install" or action == "replace":
                    sys.exit(f"--make must be used with install and replace actions")
                else:
                    make = ""
                    model = ""
                    serial = ""
            else:
                make, model, serial = args.make
            my_plane.maintenance_action(
                system, subsystem, action, note, day, hobbs, flight, args.offset, make, model, serial
            )
            my_plane.put_plane()
        except ValueError as e:
            sys.exit(f"Maintenance Command Value Error: {e}")

    # Last Logic
    if args.report:
        my_plane.report(args.report)
    else:
        print(f"Success: {args.registration} attributes are stored in file {args.folder}{args.registration}.pkl")

if __name__ == "__main__":
    main()
