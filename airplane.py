import sys
import pickle
import requests
import re
import csv
from validator_collection import checkers
from datetime import date
from io import StringIO
from dateutil.parser import isoparse

from report import pdf_report

# from major_systems import Airframe, Avionics, Engine, Propeller
from subsystems import Subsystem

MAJORS = ("airframe", "engine", "propeller", "avionics")


# this class holds subsystems - airframe, engines, propellers and avionics
# and it is a subsystem itself
class System(Subsystem):
    """Class for Systems that Hold Subsystems"""

    def __init__(self, system_name):
        super().__init__(system_name)
        self.subsystems = {}  # a dict to hold the subsystems

    def __str__(self):
        subsystem_str = super().__str__()
        return f"{self.subsystem_name} Subsystems: {self.subsystems}\n{subsystem_str}"

    # #add a subsystem to a system
    # def add_subsystem(self, subsystem_name):
    #     self.subsystems[subsystem_name] = Subsystem(subsystem_name)


class Airplane:

    def __init__(self, make, model, serial, manufacture_date, registration, folder):
        self.make = make
        self.model = model
        self.serial = serial
        self.manufacture_date = manufacture_date


        self.registration = registration
        self.folder: str = folder

        self.google_sheet_id: str = ""

        self.last_flight_date = manufacture_date
        self.flight_hours = 0.0
        self.hobbs_hours = 0.0

        self.day_zero_hobbs_hours: float = 0.0
        self.day_zero_flight_hours: float = 0.0

        # Airplane Major Systems a kept here, these systems contain subsystems
        self.major_systems: dict = {}

        self.put_plane()

    def __str__(self):
        return f"{self.make} {self.model} with serial {self.serial} and registration {self.registration}.\
            \nPlane stored in {self.folder}{self.registration}.\
            \nSystems: {", ".join(list(self.major_systems.keys()))}.\
            \nManufacture Date: {self.manufacture_date}\
            \nCurrent Hours from Google sheet, ID ending with {self.google_sheet_id[-6:]}.\
            \nDay Zero Hours: Hobbs {self.day_zero_hobbs_hours}, Flight {self.day_zero_flight_hours}.\
            \nCurrent  Hours: Hobbs {self.hobbs_hours}, Flight {self.flight_hours}."

    def put_plane(self):

        # Save plane to a file
        try:
            with open(f"{self.folder}{self.registration}.pkl", "wb") as file:
                pickle.dump(self, file)
        except (pickle.PicklingError, TypeError, IOError) as e:
            sys.exit(f"Error during pickling file write: {e}")

    # Getter for manufacture date
    @property
    def manufacture_date(self) -> float:
        return self._manufacture_date


    # Setter for manufacture_date
    # make date is an ISO 8601 date
    @manufacture_date.setter
    def manufacture_date(self, manufacture_date):
        try:
            self._manufacture_date = isoparse(manufacture_date).strftime("%Y-%m-%d")
        except:
            raise ValueError(f"Invalid Manufacture Date \'{manufacture_date}\'")



    # Getter for flight hours
    @property
    def flight_hours(self) -> float:
        return self._flight_hours

    # Setter for flight hours
    # make sure hours is a positive float rounded to tenths
    @flight_hours.setter
    def flight_hours(self, flight_hours):
        if checkers.is_float(
            flight_hours, minimum=0.0, maximum=20000.0
        ) and 10 * flight_hours == round(10 * flight_hours):
            self._flight_hours = flight_hours
        else:
            raise ValueError(f"Invalid Flight Hours {flight_hours}")

    # Getter for hobbs hours
    @property
    def hobbs_hours(self) -> float:
        return self._hobbs_hours

    # Setter for flight hours
    # make sure hours is a positive float rounded to tenths
    @hobbs_hours.setter
    def hobbs_hours(self, hobbs_hours):
        HOBBS_RATIO_MIN = 1.05
        HOBBS_RATIO_MAX = 1.30
        if (
            checkers.is_float(hobbs_hours, minimum=0.0, maximum=20000.0)
            and 10 * hobbs_hours == round(10 * hobbs_hours)
            and hobbs_hours >= self._flight_hours
            and self._flight_hours * HOBBS_RATIO_MIN <= hobbs_hours
            and self._flight_hours * HOBBS_RATIO_MAX + 100 > hobbs_hours
        ):
            self._hobbs_hours = hobbs_hours
        else:
            raise ValueError(f"Invalid Hobbs Hours {hobbs_hours}")

    def set_sheet_id(self, id):
        """Update the google sheet ID in the instance"""
        self.google_sheet_id = id

    def set_day_zero(self, purchase_date, hobbs, flight):
        """set the date and hours at purchase"""
        if checkers.is_date(purchase_date):
            self.purchase_date: date = purchase_date
        else:
            raise ValueError(f"Invalid date")
        if checkers.is_float(hobbs) and checkers.is_float(flight):
            self.day_zero_hobbs_hours: float = float(hobbs)
            self.day_zero_flight_hours: float = float(flight)
        else:
            raise ValueError(f"Invalid hobbs or flight hours")

    def get_current_hours(self):
        response = requests.get(
            f"https://docs.google.com/spreadsheets/d/{self.google_sheet_id}/export?format=csv"
        )

        # Convert the response content to a file-like object
        csv_data = StringIO(response.text)

        # Read the CSV
        reader = csv.reader(csv_data)

        #print(list(reader)[-1:][0][0])
        d,_,_,h, f = list(reader)[-1:][0][0:5]
        hobbs = float(h.replace(",", ""))
        flight = float(f.replace(",", ""))

        return hobbs, flight, d[0:11]

    def report(self, report_type):
        pdf_report(self, report_type)

    # add major system such as Engine left_engine ...
    # put in one of four Classes - Airframe, Engine, Avionics, Propeller
    # Class distinctions tbd -- such as software versions for avionics
    def configure_major_system(
        self, major_system_name, make, model, serial, interval_qty, interval_units
    ):
        if any(key in major_system_name for key in MAJORS):
            self.major_systems[major_system_name] = System(
                major_system_name
            )  # instantiation INITIALIZES the SYSTEM
            # install the major system using the inherited subsystem methods
            interval = (interval_qty, interval_units)
            self.major_systems[major_system_name].maintenance(
                self.manufacture_date,
                0.0,
                0.0,
                0.0,
                "install",
                "",
                make,
                model,
                serial,
                interval,
            )
        else:
            raise ValueError(
                f"System Name Must include airframe, engine, propeller, or avionics"
            )
        return

    def configure_subsystem(
        self, system_subsystem, make, model, serial, interval_qty, interval_units
    ):
        system, subsystem = self.system_split(system_subsystem)
        if any(key in system_subsystem for key in MAJORS):
            self.major_systems[system].subsystems[subsystem] = Subsystem(
                subsystem
            )  # instantiation INITIALIZES the SYSTEM
            # install the major system using the inherited subsystem methods
            interval = (interval_qty, interval_units)
            self.major_systems[system].subsystems[subsystem].maintenance(
                self.manufacture_date,
                0.0,
                0.0,
                0.0,
                "install",
                "",
                make,
                model,
                serial,
                interval,
            )
        else:
            raise ValueError(
                f"System Name Must include airframe, engine, propeller, or avionics"
            )
        return

    def maintenance_action(
        self,
        system,
        subsystem,
        action,
        note,
        maintenance_date,
        hobbs,
        flight,
        offset,
        make,
        model,
        serial,
    ):

        if system in self.major_systems.keys():
            if subsystem == "":  # action is on the major system
                interval = self.major_systems[system].maintenance_interval
                self.major_systems[system].maintenance(
                    maintenance_date,
                    hobbs,
                    flight,
                    offset,
                    action,
                    note,
                    make,
                    model,
                    serial,
                    interval,
                )
            elif subsystem in self.major_systems[system].subsystems.keys():
                interval = (
                    self.major_systems[system]
                    .subsystems[subsystem]
                    .maintenance_interval
                )
                self.major_systems[system].subsystems[subsystem].maintenance(
                    maintenance_date,
                    hobbs,
                    flight,
                    offset,
                    action,
                    note,
                    make,
                    model,
                    serial,
                    interval,
                )
            else:
                raise ValueError(f"Subystem named {subsystem} not found")
            return
        else:
            raise ValueError(f"Major System named {system} not found")

    def system_split(self, system_subsystem):
        # log
        match = re.match("^(.*):(.*)", system_subsystem)
        if match:
            system = match.group(1)
            subsystem = match.group(2)
        else:
            system = system_subsystem
            subsystem = ""
        return system, subsystem


def main(): ...


if __name__ == "__main__":
    main()
