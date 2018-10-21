from .classes import InputLine, InputFile
from nose.tools import *


def test_input_pizzeria():
    """
    Testing input parsing in a valid scenario.
    :return:
    """
    input_line = InputLine('2 3 5\n')
    assert input_line.parse_pizzeria(30) == (2, 3, 5)


@raises(Exception)
def test_input_pizzeria_above_limits():
    """
    Test than an error is raised if pizzeria is outside of the city.
    :return:
    """
    input_line = InputLine('2 300 5\n')
    input_line.parse_pizzeria(30)


def test_input_header():
    """
    Testing input header in a valid scenario.
    :return:
    """
    input_line = InputLine('5 2\n')
    assert input_line.parse_playground() == (5, 2)


@raises(Exception)
def test_input_header_above_limits():
    """
    Test than an error is raised if headers values are above limits.
    :return:
    """
    input_line = InputLine('50000 2\n')
    input_line.parse_playground()


def end_2_end_test():
    """
    End-2-end test for the whole logic.
    :return:
    """
    input_file = InputFile('input/input.dat')
    pizzeria_map = input_file.parse_file()
    assert pizzeria_map.get_best_location_value() == 2
