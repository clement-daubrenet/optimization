import click
from classes import InputFile, Path


@click.command()
@click.option('--file', default='input/input.dat',
              help='The path of the input file')
def get_result_for_file(file):
    """
    Getting the result (longest safest path to Zearth) given the input file
    provided.
    :param file: the path of the input file from the working directory.
    e.g: 'input.dat'
    :return:
    """
    # Parsing the input file
    input_file = InputFile(file)
    stations_map = input_file.parse_file()

    # Checking that the map is valid
    stations_map.is_valid()

    # Getting the safest longest teleportation trip within the map
    path = Path(stations_map)
    click.echo(path.get_longest_teleportation())


if __name__ == '__main__':
    get_result_for_file()
