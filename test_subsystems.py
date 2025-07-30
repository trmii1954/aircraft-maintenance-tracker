from subsystems import Subsystem
from airplane import System


def main():
     test_subsystem_init()
     test_system_init()




def test_subsystem_init():
    ss = Subsystem("left_mag")
    assert ss.subsystem_name == "left_mag"
    assert ss.make == "tbd make"
    assert ss.model == "tbd model"
    assert ss.serial == "tbd serial"
    assert ss.maintenance_interval == (0, "years")


def test_system_init():
    major = System("engine")
    assert major.subsystem_name == "engine"
    assert len(major.subsystems) == 0




if __name__ == "__main__":
    main()

