import click
from classes import InputFile


@click.command()
@click.option('--file', default='input/input.dat',
              help='The path of the input file')
def get_result_for_file(file):
    """
    Getting the result (best spot to maximize the number of accessible
    pizzerias delivery) given the input file provided.
    :param file: the path of the input file from the working directory.
    e.g: 'input.dat'
    :return integer best_delivery_value: The maximum of deliveries one can get
    within the map.
    """
    input_file = InputFile(file)
    pizzeria_map = input_file.parse_file()
    click.echo(pizzeria_map.get_best_location_value())


if __name__ == '__main__':
    get_result_for_file()
