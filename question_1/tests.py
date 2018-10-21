from .classes import InputLine, InputFile, Path
from nose.tools import *


def test_input_station():
    """
    Testing input parsing in a valid scenario.
    :return:
    """
    input_line = InputLine('2 3 5\n')
    assert input_line.parse_station() == ['2', '3', '5']


@raises(Exception)
def test_input_station_above_limits():
    """
    Test than an error is raised if coordinates are above limits.
    :return:
    """
    input_line = InputLine('10000 3 5\n')
    input_line.parse_station()


def test_input_header():
    """
    Testing input header in a valid scenario (number of stations).
    :return:
    """
    input_line = InputLine('5\n')
    assert input_line.parse_count() == 5


@raises(Exception)
def test_input_header_above_limits():
    """
    Testing than an error is raised if count is above limit.
    :return:
    """
    input_line = InputLine('15000\n')
    input_line.parse_count(maximum=10000)


def end_2_end_test():
    """
    End-2-end test for the whole logic.
    :return:
    """
    # Parsing the input file
    input_file = InputFile('input/input.dat')
    stations_map = input_file.parse_file()

    # Checking that the map is valid
    stations_map.is_valid()

    # Getting the safest longest teleportation trip within the map
    path = Path(stations_map)

    assert path.get_longest_teleportation() == '2.00'
