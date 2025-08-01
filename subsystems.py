from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
import re


class Subsystem:
    """Airplane subsystem object and its logs."""

    def __init__(self, subsystem_name):
        self.subsystem_name = subsystem_name
        self.action_log = []

        self.install_subsystem("tbd make", "tbd model", "tbd serial", (0, "years"))

        self.interval_date = "1903-01-01"
        self.interval_hobbs_hours = 0.0
        self.interval_flight_hours = 0.0
        # self.maintenance("1903-01-01", 0.0, 0.0, 0.0, "install: ","tbd make", "tbd model", "tbd serial",(0, "years"))

    def __str__(self):
        s = f"{self.subsystem_name} {self.make} {self.model} {self.serial} {self.maintenance_interval}\n"
        # s += f"Last:{self.maintenance_date} {self.maintenance_hobbs_hours} {self.maintenance_flight_hours} {self.maintenance_last_action}\n"
        # s += f"Install:{self.install_date} {self.install_hobbs_hours} {self.install_flight_hours} offset:{self.offset}\n"
        s += f"Interval:{self.interval_date} {self.interval_hobbs_hours} {self.interval_flight_hours} \n"
        # s += f"Log:{self.action_log}"
        # s += "*" * 30
        return s

    # Getter for interval date
    @property
    def interval_date(self) -> float:
        return self._interval_date

    # Setter for interval_date
    # make date is a reasonable ISO 8601 date
    @interval_date.setter
    def interval_date(self, interval_date):
        try:
            self._interval_date = isoparse(interval_date).strftime("%Y-%m-%d")
        except:
            raise ValueError(f'Invalid Interval Date "{interval_date}"')

    def install_subsystem(self, make, model, serial, interval):
        """Configure the subsystem.  Make, model, serial number and maintenance interval"""

        self.make = make
        self.model = model
        self.serial = serial
        valid_intervals = ("flight_hours", "calendar_months", "days", "years")
        quantity, units = interval
        try:
            float(quantity)
            if units in valid_intervals:
                self.maintenance_interval = interval
            else:
                raise ValueError(f"{units} not one of {valid_intervals}")
        except:
            raise ValueError(f"{quantity} not convertable to float")

    # maintenance Action
    # make, model and serial are required for install and replace actions

    def maintenance(
        self,
        maintenance_date: str,
        hobbs_hours: float,
        flight_hours: float,
        offset: float,
        action: str,  # action from ACTIONS list
        note: str,
        make: str,
        model: str,
        serial: str,
        maintenance_interval,
    ):
        """
        Log maintenance actions and update maintenance properties

        Parameters:
            maintenance_date (str): maintenance date in 8601 format
            hobbs_hours (float)   : hobbs hour meter reading when the maintenance was done
            flight_hours (float)  : flight hour meter reading when the maintenance was done
            offset (float)        : prior time in service of a subsystem a installation, defaults to 0.0
            action (str)          : install, replace, interval, repair, routine, troubleshoot
            note (str)            : optional note
            make: (str)           : make, only used with install or replace
            model (str)           : make, only used  with install or replace
            serial (str)          : make, only used  with install or replace
            maintenance_interval (tuple) : (quanity, units), only used  with install or replace
                                             quantity is an integer
                                             units are flight_hours, calendar_months or years

        Returns:
            None.  Updates the instance properties and logs.

        Raises:
            ValueError if the new interval time is before the current interval
        """

        # the last maintenance date will be forced to the most recent command
        # this forces commands to be chronological !!!  NOT GREAT
        self.maintenance_date = maintenance_date
        self.maintenance_hobbs_hours = hobbs_hours
        self.maintenance_flight_hours = flight_hours
        self.maintenance_last_action = action

        self.action_log.append(
            {
                "date": maintenance_date,
                "hobbs": hobbs_hours,
                "flight": flight_hours,
                "action": action,
                "note": note,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        if action in ("install", "replace"):
            self.install_subsystem(make, model, serial, maintenance_interval)
            self.install_date = maintenance_date
            self.install_hobbs_hours = hobbs_hours
            self.install_flight_hours = flight_hours
            self.offset = offset
            self.interval_date = maintenance_date
            self.interval_hobbs_hours = hobbs_hours
            self.interval_flight_hours = flight_hours

        # reset the interval start reference if appropriate
        if action in ("interval"):
            if (
                maintenance_date >= self.interval_date
                and hobbs_hours >= self.interval_hobbs_hours
                and flight_hours >= self.interval_flight_hours
            ):
                self.interval_date = maintenance_date
                self.interval_hobbs_hours = hobbs_hours
                self.interval_flight_hours = flight_hours
            else:
                raise ValueError("Maintenance Time is Before Current Interval Start")

    def maintenance_status(self, flight_hours):
        """Calculate the maintenace status from the susbsytem instance properties"""
        age_s = ""
        remaining_s = ""
        due_in_at_s = ""
        match self.maintenance_interval[1]:
            case "flight_hours":
                age = flight_hours - float(self.maintenance_flight_hours)
                due_in_at = float(self.interval_flight_hours) + float(
                    self.maintenance_interval[0]
                )
                remaining = due_in_at - flight_hours
                age_s = f"{age:.1f}"
                remaining_s = f"{remaining:.1f}"
                due_in_at_s = f"{due_in_at:.1f}"

            case "calendar_months":
                delta = int(self.maintenance_interval[0])
                # age = date.today() - datetime.strptime(self.maintenance_date, "%Y-%m-%d").date()
                age_s: str = self.years_days_age(self.interval_date, due_date=False)
                due_in_at_s = datetime.strptime(
                    self.interval_date, "%Y-%m-%d"
                ).date() + relativedelta(months=delta, day=31)
                remaining_s = self.years_days_age(
                    due_in_at_s.strftime("%Y-%m-%d"), due_date=True
                )

            case "years":
                delta = int(self.maintenance_interval[0])
                # age = date.today() - datetime.strptime(self.maintenance_date, "%Y-%m-%d").date()
                age_s: str = self.years_days_age(self.interval_date, due_date=False)
                due_in_at_s = datetime.strptime(
                    self.interval_date, "%Y-%m-%d"
                ).date() + relativedelta(years=delta)
                remaining_s = self.years_days_age(
                    due_in_at_s.strftime("%Y-%m-%d"), due_date=True
                )

        # force due and remaining strings to "" if no interval
        q, u = self.maintenance_interval
        if q == 0:
            q = ""
            u = ""
            due_in_at_s = ""
            remaining_s = ""
        interval_string_tuple = (str(q), u)

        return [
            self.subsystem_name,
            self.interval_date,
            self.interval_flight_hours,
            " ".join(interval_string_tuple),
            age_s,
            remaining_s,
            due_in_at_s,
        ]

    def years_days_age(self, relative_date, due_date=False) -> str:
        """
        Calculate a date difference  in days between today and a given date.
        If the relative date is not a due date, positive days are returned as such.  I.E. Age in years and days.
        If the relative date is a due date, negative days indicate overdue and will be returned as negative/red.

        Parameters:
            relative date (str ISO 8601 date)

        Returns:
            returns string in years and days based on 365 day year
            negative for future relative dates, positive for past relative dates (i.e.how old)
        """
        age = date.today() - datetime.strptime(relative_date, "%Y-%m-%d").date()
        q, r = divmod(abs(age.days), 365)
        if due_date:
            if age.days > 0:  # over due date, make negative
                q, r = -q, -r
        else:
            if age.days < 0:
                q, r = -q, -r

        if q == 0:
            return f"{r:3d} d"
        else:
            return f"{q:2d} y {r:3d} d"


def main(): ...


if __name__ == "__main__":
    main()
