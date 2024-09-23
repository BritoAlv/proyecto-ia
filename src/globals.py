class Colors:
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
    YELLOW = 'yellow'
    GREY = 'grey'
    BLACK = 'black'
    WHITE = 'white'
    ORANGE = 'orange'
    CYAN = 'cyan'
    VIOLET = 'violet'

class Directions:
    NORTH = 1
    SOUTH = 3
    EAST = 2
    WEST = 4
    INTERSECTION = -1
    EOR = -2
    EMPTY = 0

DIRECTION_COLOR = {
    Directions.NORTH: Colors.BLUE,
    Directions.SOUTH: Colors.RED,
    Directions.EAST: Colors.GREEN,
    Directions.WEST: Colors.ORANGE,
    Directions.EMPTY: Colors.GREY,
    Directions.INTERSECTION: Colors.VIOLET,
}

DIRECTION_OFFSETS = {
            Directions.NORTH: (-1, 0),
            Directions.SOUTH: (1, 0),
            Directions.EAST: (0, -1),
            Directions.WEST: (0, 1)
        }

def valid_coordinates(i, j, height, width):
    return 0 <= i < height and 0 <= j < width; 