import numpy


class InputFile:
    """
    A class dealing with an input file. The input file looks like:
    [side length of the city] [number of pizzerias in the city]
    [pizzeria 1 line coefficient] [pizzeria 1 column coefficient]
    [pizzeria 2 line coefficient] [pizzeria 2 column coefficient]
    [pizzeria n line coefficient] [pizzeria n column coefficient]
    e.g: 5 2
    3 3 2
    1 1 2
    """
    def __init__(self, filename):
        """
        Setting the file name.
        :param str filename: The full file name in the working directory.
        e.g: 'input.dat'
        """
        self.filename = filename

    def parse_file(self):
        """
        Parsing the whole file to return the whole map of stations.
        :return obj map: the map instance of the city with pizzerias.
        """
        with open(self.filename, 'r') as pizzerias_file:
            cizy_size, pizzerias_count = self._parse_header(pizzerias_file)
            pizzerias_map = Map(cizy_size, pizzerias_count)
            self._parse_body(pizzerias_file, cizy_size, pizzerias_map)
        return pizzerias_map

    @staticmethod
    def _parse_header(pizerrias_file):
        """
        Parsing and validating the file header containing specific information.
        :param obj pizerrias_file: the file instance.
        :return obj map: the updated map with the header data.
        """
        perimeter_line = InputLine(pizerrias_file.readline())
        return perimeter_line.parse_playground()

    @staticmethod
    def _parse_body(pizzeria_file, city_size, pizzerias_map):
        """
        Parsing the body containing the list of pizzerias with the associated
        delivery perimeter.
        :return:
        """
        for line in pizzeria_file.readlines():
            input_line = InputLine(line)
            pizzeria_line, pizzeria_column, delivery_perimeter = \
                input_line.parse_pizzeria(city_size)
            pizzerias_map.pizzerias.append((pizzeria_line,
                                            pizzeria_column,
                                            delivery_perimeter))


class InputLine:
    """
    A class dealing with an input line. An input line can be 2 things:
    - The city dimensions with the number of pizzerias in the city.
    n.b:[side length of the city] [number of pizzerias in the city]
    e.g: 5 2
    - A pizzeria coordinates in the matrix
    n.b: [pizzeria 1 line coefficient] [pizzeria 1 column coefficient]
    e.g: 3 3 2
    We perform validations based on the constraints imposed by the size of
    the city and the delivery perimeters.
    """
    def __init__(self, line):
        """
        Declaring the line to parse.
        :param str line: The line to parse.
        e.g: 2.00 2.00 2.00
        """
        self.line = line

    def parse_playground(self, maximum_size=1000, maximum_count=10000):
        """
        Parsing the city size and the number of pizzerias in it.
        :param int maximum_size: A value specifying the maximum
        for the coordinates (for x, y) for the city matrix.
        :param int maximum_size: A value specifying the maximum
        for the coordinates (for x, y) for the city matrix.
        :return obj station: the station instance.
        """
        values = self.line.strip('\n').split(' ')

        try:
            city_length = int(values[0])
            pizzerias_count = int(values[1])

        except ValueError:
            raise Exception('The header line containing the size of the city'
                            'and the delivery perimeter is not integers only.')

        if city_length > 1000:
            raise Exception('The city dimension is too big (it should be '
                            'less than {})'.format(str(maximum_size)))

        if pizzerias_count > 1000:
            raise Exception('The pizzerias count is too big (it should be '
                            'less than {})'.format(str(maximum_count)))

        return city_length, pizzerias_count

    def parse_pizzeria(self, city_length, max_perimeter=100):
        """
        Parsing a pizzeria line.
        :return:
        """
        pizzeria = self.line.strip('\n').split(' ')

        try:
            pizzeria_line = int(pizzeria[0])
            pizzeria_column = int(pizzeria[1])
            delivery_perimeter = int(pizzeria[2])
        except ValueError:
            raise Exception('The pizzeria line {} containing the pizzeria'
                            ' localization is not integers only.'
                            .format(pizzeria))

        if pizzeria_line > city_length:
            raise Exception('The pizzeria with coordinate {} is outside of '
                            'the map (of dimension {}x{}'
                            .format(pizzeria_line, city_length, city_length))

        if pizzeria_column > city_length:
            raise Exception('The pizzeria with coordinate {} is outside of '
                            'the map (of dimension {}x{}'
                            .format(pizzeria_column, city_length, city_length))

        if delivery_perimeter > max_perimeter:
            raise Exception('The pizzeria delivery perimeter for the line {}'
                            'is above the maximum allowed {}'
                            .format(pizzeria, max_perimeter))

        return pizzeria_line, pizzeria_column, delivery_perimeter


class Map:
    """
    A representation of the city with its pizzerias.
    It's a matrix initialized with 0. When a pizzeria covers a given
    area (coefficient), this coefficient goes +1.
    n.b: To calculate the best location, we first fill the delivery area of the
    first pizzeria with ones (it's a diamond shape). Same for the second,
    third,  etc, all being diamond shapes.
    Once all the diamond shapes are filled, it's done.
    The filling is about incrementing the coefficients of the shape with +1,
    and getting the best location is about keeping a track of the maximum
    coefficient.
    """
    def __init__(self, city_size, pizzerias_count):
        """
        Declaring the data attached to the city map with pizzerias.
        """
        self.pizzerias_count = pizzerias_count
        self.city_size = city_size
        self.city_matrix = numpy.zeros(shape=(city_size, city_size))
        self.best_location_value = 0
        self.pizzerias = []

    def get_best_location_value(self):
        """
        Getting the number of pizzerias accessible from the best location on
        the map.
        The delivery perimeter of each pizzeria is a diamond shape that
        we need to fill with an increase of +1. Then the best spot is the
        maximum on the matrix (we keep track of it).
        :param boolean revert_line: I rather consider the first line as the
        top of the matrix but based on the example of the task, the first line
        is apparently at the bottom. To keep the flexibility to change, I added
        this boolean.
        :return integer best_location_value:
        """
        for pizzeria in self.pizzerias:
            x_center, y_center, delivery = self._prepare_coordinates(pizzeria)
            self._fill_upper_diamond((x_center, y_center), delivery)
            self._fill_lower_diamond((x_center, y_center), delivery)
        return self.best_location_value

    def _fill_upper_diamond(self, pizzeria_position, delivery_width):
        """
        Starting to fill the upper part of the diamond (half of the pizzeria
        delivery perimeter) for a given pizzeria.
        e.g:
        0001000
        0011100
        0111110
        0000000
        0000000
        :param tuple pizzeria_position: line-column position of the pizzeria
        :param delivery_width: the delivery perimeter in blocks.
        :return:
        """
        top_corner = max(0, pizzeria_position[0] - delivery_width)
        for row_index in range(top_corner, pizzeria_position[0] + 1):
            left_side = max(0, pizzeria_position[1] - (
                    delivery_width - (pizzeria_position[0] - row_index)))
            right_side = min(self.city_size,
                             pizzeria_position[1] +
                             (delivery_width -
                              (pizzeria_position[0] - row_index)) + 1)
            for column_index in range(left_side, right_side):

                # Increase the coefficient with +1 to "fill" the square
                self.city_matrix[row_index][column_index] += 1

                if self.city_matrix[row_index][column_index] \
                        > self.best_location_value:
                    self.best_location_value \
                        = int(self.city_matrix[row_index][column_index])

    def _fill_lower_diamond(self, pizzeria_position, delivery_width):
        """
        Filling the lower part of the diamond (second half of the pizzeria
        delivery perimeter)
        e.g:
        0000000
        0000000
        0000000
        0011100
        0001000
        :param tuple pizzeria_position: line-column position of the pizzeria
        :param delivery_width: the delivery perimeter in blocks.
        :return:
        """
        bottom_corner = min(self.city_size,
                            pizzeria_position[0] + delivery_width + 1)

        for row_index in range(pizzeria_position[0] + 1, bottom_corner):
            left_side = max(0, pizzeria_position[1] -
                            (delivery_width - (row_index -
                                               pizzeria_position[0])))
            right_side = min(self.city_size, pizzeria_position[1] +
                             (delivery_width - (row_index -
                                                pizzeria_position[0])) + 1)
            for column_index in range(left_side, right_side):
                self.city_matrix[row_index][column_index] += 1
                if self.city_matrix[row_index][column_index] \
                        > self.best_location_value:
                    self.best_location_value \
                        = int(self.city_matrix[row_index][column_index])

    def _prepare_coordinates(self, pizzeria, revert_line=True):
        """
        I rather consider the first line as the top of the matrix but based on
        the example of the task, the first line is apparently at the bottom.
        To keep the flexibility to choose, I added a boolean to switch the
        logic. Another thing I adapt: for Python, rows/colums starts with a
        0 index, humans prefer 1.
        :param tuple pizzeria: pizzeria coordinates and delivery periveter
        e.g: (1,1,3)
        :param boolean revert_line: ff True, we start counting the lines
        from the bottom of the matrix. If False, from the top.
        :return:
        """
        x_center, y_center = pizzeria[0] - 1, pizzeria[1] - 1
        if revert_line:
            x_center = self.city_size - pizzeria[0]
        delivery_width = pizzeria[2]
        return x_center, y_center, delivery_width
