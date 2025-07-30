from project import n_number, airplane_time, directory_path
from pytest import raises
from argparse import ArgumentTypeError


def main():
    test_n_number()
    test_airplane_time()
    test_directory_path()


def test_n_number():
    assert n_number("N527W") == "N527W"
    with raises(ArgumentTypeError):
        n_number("N045")
    with raises(ArgumentTypeError):
        n_number("Y666890")


def test_airplane_time():
    assert airplane_time(["2025-04-13", 500.3, 400.2]) == ("2025-04-13", 500.3, 400.2)
    with raises(SystemExit):
        airplane_time([])
    with raises(ArgumentTypeError):
        airplane_time(["2024-01-32", 8, 7])
    with raises(ArgumentTypeError):
        airplane_time(["2024-01-30", "8afe", 7])


def test_directory_path():
    assert directory_path("planes/") == "planes/"
    with raises(ArgumentTypeError):
        directory_path("doesnotexist")


if __name__ == "__main__":
    main()
