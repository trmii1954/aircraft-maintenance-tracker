from airplane import Airplane
from pytest import raises
#from argparse import ArgumentTypeError




#"make, model, serial, manufacture_date, registration, folder"

def test_airplane_init():
    plane = Airplane("Mooney","M20R","227","2001-01-19","N527W","planes")
    assert plane.make == "Mooney"
    with raises(ValueError):
        plane = Airplane("Mooney","M20R","227","20tt01-01-19","N527W","planes")

#configure_major_system(self, major_system_name, make, model, serial, interval_qty, interval_units

def test_configure_major_system():
    plane = Airplane("Mooney","M20R","227","2001-01-19","N527W","planes")
    plane.configure_major_system("engine","TCM","IO-550","77896","2200","flight_hours")
    assert len(plane.major_systems) == 1
    with raises(ValueError):
        plane.configure_major_system("engine","TCM","IO-550","77896","2200","Fhours")


#configure_subsystem(self, system_subsystem, make, model, serial, interval_qty, interval_units
def test_configure_subsystem():
    plane = Airplane("Mooney","M20R","227","2001-01-19","N527W","planes")
    plane.configure_major_system("engine","TCM","IO-550","77896","2200","flight_hours")
    plane.configure_subsystem("engine:left_mag","Bendix","Slick Start","1234","500","flight_hours")
    assert len(plane.major_systems["engine"].subsystems) == 1
    with raises(ValueError):
        plane.configure_subsystem("tug:left_mag","Bendix","Slick Start","1234","500","flight_hours")
    with raises(ValueError):
        plane.configure_subsystem("engine:right_mag","Bendix","Slick Start","44336","500","f_hours")
    with raises(ValueError):
        plane.configure_subsystem("engine:fuel_pump","TCM","R83","123334","not a float","flight_hours")



if __name__ == "__main__":
    main()
