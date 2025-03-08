import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsItem, QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsItemGroup, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QBrush, QColor, QTransform
from PyQt5.QtCore import QRectF, QObject
from enum import Enum, Flag, auto, unique
from abc import ABC, abstractmethod, ABCMeta
from pathlib import Path
from typing import TypeVar, Generic, Optional, Callable, Any
from random import randint
import os
from PyQt5.QtCore import Qt
from directions import CardinalDirection, Turn


T = TypeVar("T")

# Temporary class
class ExternalArmData():
    def __init__(self, lane_count_in, dedicated_lanes):
        self.lane_count_in = lane_count_in
        
        self.dedicated_left = dedicated_lanes[0]
        self.dedicated_bus = dedicated_lanes[1]
        self.dedicated_right = dedicated_lanes[2]


# Temporary class
class JunctionData():
    def __init__(self, lane_counts, dedicated_lanes, has_crosswalk):
        self.arms = []
        for i in range(4):
            self.arms.append(ExternalArmData(lane_counts[i], dedicated_lanes[i]))
        
        self.has_crosswalk = has_crosswalk


class LaneType(Flag):
    """
    Enum used to specify the type of the lane

    Flag is used so that straight lanes at the edges are easier to change into
    STRAIGHT_LEFT, STRAIGHT_RIGHT, and STRAIGHT_LEFT_RIGHT variants.
    """

    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    BUS = auto()
    OUTBOUND = auto()
    STRAIGHT_LEFT = STRAIGHT | LEFT
    STRAIGHT_RIGHT = STRAIGHT | RIGHT
    STRAIGHT_LEFT_RIGHT = STRAIGHT | LEFT | RIGHT


class ResourceError(RuntimeError):
    # Custom error used for when a resource fails to load
    pass


class LazyPixmap():
    """
    Implements lazy loading for pixmaps

    i.e. a pixmap will not be created if it is never requested
    """

    _BASE_DIR = Path(__file__).parent

    def __init__(self, relativePath):
        self.relativePath = relativePath
        self.pixmap = None
    
    def __get__(self, obj, type=None):
        # Returns the pixmap if it has already been initalised
        # Otherwise it initialises and returns the pixmap

        if (self.pixmap != None):
            return self.pixmap
        self.pixmap = QPixmap((self._BASE_DIR / self.relativePath).resolve().__str__())
        if self.pixmap.isNull():
            raise ResourceError(f"Pixmap failed to load {self.relativePath}")
        return self.pixmap


class LazyDict(dict):
    """
    Allows the LazyPixmap to be stored in a dict and still work

    Otherwise the __get__ method would not be called when accessing the LazyPixmap from a dict
    """

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if hasattr(value, '__get__'):
            result = value.__get__(None, None)
            self[key] = result
            return result
        return value


class Pixmap():
    """
    Used to store a single instance of each required pixmap (prevents duplicates for each lane)

    Lazy pixmaps are used for two reasons:
        1) Prevent creation of pixmaps which are not used
        2) pixmaps cannot be created before the QGuiApplication
    """

    STRAIGHT_LANE = LazyPixmap('tiles/s_in.png')
    LEFT_LANE = LazyPixmap('tiles/l_in.png')
    RIGHT_LANE = LazyPixmap('tiles/r_in.png')
    BUS_LANE = LazyPixmap('tiles/bus_in.png')
    OUTBOUND_LANE = LazyPixmap('tiles/out.png')
    STRAIGHT_LEFT_LANE = LazyPixmap('tiles/sl_in.png')
    STRAIGHT_RIGHT_LANE = LazyPixmap('tiles/sr_in.png')
    STRAIGHT_LEFT_RIGHT_LANE = LazyPixmap('tiles/slr_in.png')
    _LANES = LazyDict({
        LaneType.STRAIGHT: STRAIGHT_LANE,
        LaneType.LEFT: LEFT_LANE,
        LaneType.RIGHT: RIGHT_LANE,
        LaneType.BUS: BUS_LANE,
        LaneType.OUTBOUND: OUTBOUND_LANE,
        LaneType.STRAIGHT_LEFT: STRAIGHT_LEFT_LANE,
        LaneType.STRAIGHT_RIGHT: STRAIGHT_RIGHT_LANE,
        LaneType.STRAIGHT_LEFT_RIGHT: STRAIGHT_LEFT_RIGHT_LANE
    })
    
    INBOUND_DIVIDER = LazyPixmap('tiles/in_div.png')
    OUTBOUND_DIVIDER = LazyPixmap('tiles/out_div.png')
    
    CROSSWALK = LazyPixmap('tiles/cw')
    NO_CROSSWALK = LazyPixmap('tiles/no_cw')
    
    CROSSWALK_DIVIDER = LazyPixmap('tiles/cw_div.png')
    NO_CROSSWALK_DIVIDER = LazyPixmap('tiles/no_cw_div.png')
    
    ISLAND_EDGE_LEFT = LazyPixmap('tiles/island_edge.png')
    ISLAND_CENTER = LazyPixmap('tiles/island_center.png')
    _ISLAND_EDGE_RIGHT = None

    CORNER = LazyPixmap('tiles/corner.png')
    
    @classmethod
    @property
    def ISLAND_EDGE_RIGHT(cls):
        # This pixmaps initialisation must also be delayed to when it is first accessed
        if cls._ISLAND_EDGE_RIGHT == None:
            # If it has no been initalised yet then it created by flipping ISLAND_EDGE_LEFT
            cls._ISLAND_EDGE_RIGHT = cls.ISLAND_EDGE_LEFT.transformed(QTransform().scale(-1, 1))
        return cls._ISLAND_EDGE_RIGHT
    
    @classmethod
    def get_lane(cls, lane_type: LaneType) -> QPixmap:
        if lane_type not in cls._LANES:
            raise ValueError(f"Invalid lane type: {lane_type}")
        return cls._LANES[lane_type]

    @classmethod
    def get_lane_divider(cls, is_inbound: bool) -> QPixmap:
        if is_inbound:
            return cls.INBOUND_DIVIDER
        return cls.OUTBOUND_DIVIDER

    @classmethod
    def get_crosswalk(cls, has_crosswalk: bool) -> QPixmap:
        if has_crosswalk:
            return cls.CROSSWALK
        return cls.NO_CROSSWALK
    
    @classmethod
    def get_crosswalk_divider(cls, has_crosswalk: bool) -> QPixmap:
        if has_crosswalk:
            return cls.CROSSWALK_DIVIDER
        return cls.NO_CROSSWALK_DIVIDER


class QABCMeta(ABCMeta, type(QObject)):
    # Metaclass used to prevent metaclass conflicts between ABCs and PyQt classes
    pass


class Tile(QGraphicsItem):
    """
    Tiles are QGraphicsItems with a width and height, they also define
    an arrange_tiles which sets the positions of any subtiles.
    
    The subtiles of an object are the tiles which it contains
    """

    def width(self):
        return self.boundingRect().width()
    
    def height(self):
        return self.boundingRect().height()
    
    def arrange_tiles(self):
        # Contains no subtiles so does nothing
        pass


class PixmapTile(QGraphicsPixmapItem, Tile):
    # Tile implementation of a QGraphicsPixmapItem

    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)


class TileGroup(QGraphicsItemGroup, Tile, metaclass = QABCMeta):
    """
    A QGraphicsItemGroup which can contains subtiles
    """

    def __init__(self):
        super().__init__()
        self.subtiles = []
        self._boundingRect = None
    
    def add_to_group(self, tile):
        # adds a subtile
        super().addToGroup(tile)
        self.subtiles.append(tile)
    
    def arrange_tiles(self):
        # Arranges the subtiles and updates the bounding rect
        self._arrange()
        self._update_bounding_rect()
        
    @abstractmethod
    def _arrange(self):
        # Performs the actual moving of subtiles in arrange_tiles()
        pass

    def _update_bounding_rect(self):
        # Sets the bounding rect to be the union of the bounding rects of all subtiles
        boundingRect = QRectF()
        for tile in self.childItems():
            boundingRect |= self.mapFromScene(tile.sceneBoundingRect()).boundingRect()
        self._boundingRect = boundingRect
        
    def boundingRect(self):
        # Returns the bounding rect of the group
        if self._boundingRect == None:
            return super().boundingRect()
        return self._boundingRect


class HorizontalTileGroup(TileGroup):
    # A tilegroup which aranges subtiles horizontally
    
    def _arrange(self):
        offset = 0
        for tile in self.subtiles:
            tile.setPos(offset, 0)
            tile.arrange_tiles()
            offset += tile.width()


class VerticalTileGroup(TileGroup):
    # A tilegroup which aranges subtiles vertically
    
    def _arrange(self):
        offset = 0
        for tile in self.subtiles:
            tile.setPos(0, offset)
            tile.arrange_tiles()
            offset += tile.height()


class LaneCrosswalkGroup(VerticalTileGroup, Generic[T], metaclass=QABCMeta):
    """
    A tile group which consists of two subtiles:
        1) A crosswalk tile
        2) A lane tile
    """

    def __init__(self, lane_type, has_crosswalk: bool):
        super().__init__()
        self.add_to_group(self._create_crosswalk_tile(has_crosswalk))
        self.add_to_group(self._create_lane_tile(lane_type))
            
    @abstractmethod
    def _create_crosswalk_tile(self, has_crosswalk: bool) -> PixmapTile:
        # Generates the crosswalk PixmapTile
        pass
    
    @abstractmethod
    def _create_lane_tile(self, lane_type: T) -> PixmapTile:
        # Generates the lane PixmapTile
        pass


class Lane(LaneCrosswalkGroup[LaneType]):
    # LaneCrosswalkGroup for a lane

    def __init__(self, lane_type: LaneType, has_crosswalk: bool):
        super().__init__(lane_type, has_crosswalk)
        
    def _create_crosswalk_tile(self, has_crosswalk: bool) -> PixmapTile:
        return PixmapTile(Pixmap.get_crosswalk(has_crosswalk))
        
    def _create_lane_tile(self, lane_type: LaneType) -> PixmapTile:
        return PixmapTile(Pixmap.get_lane(lane_type))


class LaneDivider(LaneCrosswalkGroup[bool]):
    # LaneCrosswalkGroup for a divider between lanes (Like the dashed white lines)

    def __init__(self, is_inbound: bool, has_crosswalk: bool):
        super().__init__(is_inbound, has_crosswalk)
        
    def _create_crosswalk_tile(self, has_crosswalk: bool) -> PixmapTile:
        return PixmapTile(Pixmap.get_crosswalk_divider(has_crosswalk))
        
    def _create_lane_tile(self, is_inbound: bool) -> PixmapTile:
        return PixmapTile(Pixmap.get_lane_divider(is_inbound))      


class CentralIsland(HorizontalTileGroup):
    # Tile group for the central island between the inbound and outbound lanes

    def __init__(self, tile_count):
        super().__init__()
        self.add_to_group(PixmapTile(Pixmap.ISLAND_EDGE_LEFT))
        for i in range(tile_count):
            self.add_to_group(PixmapTile(Pixmap.ISLAND_CENTER))
        self.add_to_group(PixmapTile(Pixmap.ISLAND_EDGE_RIGHT))


class Arm(HorizontalTileGroup):
    """
    Generates a whole arm of the junction based on the data provided
    """

    def __init__(self, arm_data):
        super().__init__()

        # Generate inbound lanes
        incoming_lanes = self._calculate_incoming_lanes(arm_data)
        if len(incoming_lanes) >= 1:
            self.add_to_group(Lane(incoming_lanes[0], arm_data.has_crosswalk))
            for i in range(1, len(incoming_lanes)):
                self.add_to_group(LaneDivider(True, arm_data.has_crosswalk))
                self.add_to_group(Lane(incoming_lanes[i], arm_data.has_crosswalk))
        
        # Generate center island
        self.add_to_group(CentralIsland(arm_data.center_count))
        
        # Generate outbound lanes
        if arm_data.lane_count_out >= 1:
            self.add_to_group(Lane(LaneType.OUTBOUND, arm_data.has_crosswalk))
            for i in range(1, arm_data.lane_count_out):
                self.add_to_group(LaneDivider(False, arm_data.has_crosswalk))
                self.add_to_group(Lane(LaneType.OUTBOUND, arm_data.has_crosswalk))
        
        # Adds the corner to the group
        self.add_to_group(PixmapTile(Pixmap.CORNER))
             
    
    def _calculate_incoming_lanes(self, arm_data):
        # Outputs a list of incoming lane types in order from left to right
        lanes = []

        if arm_data.dedicated_bus:
            lanes.append(LaneType.BUS)
        
        if arm_data.dedicated_left:
            lanes.append(LaneType.LEFT)
        
        lanes += self._calculate_straight_lanes(arm_data)

        if arm_data.dedicated_right:
            lanes.append(LaneType.RIGHT)

        return lanes
    
    def _calculate_straight_lanes(self, arm_data):
        """
        Generates a list containing the correct number of lanes which can go straight
        Then lets the leftmost turn left, and the rightmost turn right
        """
        
        lanes = []
        lane_count = arm_data.lane_count_in
        if arm_data.dedicated_left:
            lane_count -= 1

        if arm_data.dedicated_right:
            lane_count -= 1

        if lane_count == 0:
            return []
        
        for i in range(lane_count):
            lanes.append(LaneType.STRAIGHT)
        
        if len(lanes) >= 1:
            lanes[0] |= LaneType.LEFT
            lanes[-1] |= LaneType.RIGHT
            
        return lanes


class ArmData():
    def __init__(self, lane_counts, dedicated_lanes, has_crosswalk):
        self.lane_count_in = lane_counts[0]
        self.center_count = lane_counts[1]
        self.lane_count_out = lane_counts[2]
        
        self.dedicated_left = dedicated_lanes[0]
        self.dedicated_bus = dedicated_lanes[1]
        self.dedicated_right = dedicated_lanes[2]
        
        self.has_crosswalk = has_crosswalk
    
    @staticmethod
    def generate_from_junction_data(junction_data):
        # Generates a list of 4 ArmData instances from a JunctionData object
        # TODO change JunctionData to the correct class

        arms = []
        
        # Calculates the number of lanes which exit at each arm
        lane_counts_out = []
        for direction in CardinalDirection:
            straight_data = junction_data.arms[(direction + Turn.BACK).index]
            # Number of lanes which can exit here by going straight (excluding bus lane)
            straight_undedicated_lanes = max(0, straight_data.lane_count_in - straight_data.dedicated_left - straight_data.dedicated_right)
            # Number of lanes which can exit here by going straight (including bus lane)
            straight_lanes = (
                straight_data.dedicated_bus
                + straight_undedicated_lanes
            )

            left_data = junction_data.arms[(direction + Turn.LEFT).index]
            left_undedicated_lanes = max(0, left_data.lane_count_in - left_data.dedicated_left - left_data.dedicated_right)
            # Number of lanes which can exit here by going left
            left_lanes = (
                left_data.dedicated_left
                + left_data.dedicated_bus
                + (left_undedicated_lanes >= 1)
            )
            
            # Number of lanes which can exit here by going right
            right_data = junction_data.arms[(direction + Turn.RIGHT).index]
            right_undedicated_lanes = max(0, right_data.lane_count_in - right_data.dedicated_left - right_data.dedicated_right)
            right_lanes = (
                right_data.dedicated_right
                + (right_undedicated_lanes >= 1)
            )
            # Only the max of these matters for the number of outgoing lanes
            lane_counts_out.append(max(1, left_lanes, straight_lanes, right_lanes))

        # Calculates the width of each island based on the difference 
        # between the width of each arm and its opposite arm
        island_widths = []
        for direction in CardinalDirection:
            i = direction.index
            this_arm = junction_data.arms[i]
            opposite_arm = junction_data.arms[(direction + Turn.BACK).index]
            
            this_arm_width = this_arm.dedicated_bus + this_arm.lane_count_in + lane_counts_out[i]
            opposite_arm_width = opposite_arm.dedicated_bus + opposite_arm.lane_count_in + lane_counts_out[(direction + Turn.BACK).index]
            
            island_widths.append(max(0, opposite_arm_width - this_arm_width))
            arms.append(
                ArmData(
                    [this_arm.lane_count_in, island_widths[i], lane_counts_out[i]], 
                    [this_arm.dedicated_left, this_arm.dedicated_bus, this_arm.dedicated_right], 
                    junction_data.has_crosswalk
                )
            )

        return arms


class Junction(TileGroup):
    """
    Tile group which generates the whole junction from the junction_data passed to it 
    """

    def __init__(self, junction_data):
        super().__init__()

        arm_data = ArmData.generate_from_junction_data(junction_data)
        for data in arm_data:
            self.add_to_group(Arm(data))

        self.arrange_tiles()
    
    def _arrange(self):
        # Arranges subtiles of each arm, then positions each arm at the north/east/south/west of the junction
        for i in range(4):
            self.subtiles[i].arrange_tiles()

        # Entering north
        self.subtiles[0].setRotation(180)
        self.subtiles[0].setPos(self.subtiles[0].width(), self.subtiles[0].height())
        
        # Entering east
        self.subtiles[1].setRotation(270)
        self.subtiles[1].setPos(self.subtiles[0].width(), self.subtiles[1].width())
        
        # Entering south
        self.subtiles[2].setPos(self.subtiles[3].height(), self.subtiles[1].width())
        
        # Entering west
        self.subtiles[3].setRotation(90)
        self.subtiles[3].setPos(self.subtiles[3].height(), self.subtiles[0].height())


class JunctionView(QGraphicsView):
    """
    The object which will be used by the rest of the application to show the junction
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(0, 0, 100, 100)
        self.scene.setBackgroundBrush(QBrush(QColor(70, 70, 70)))  # Set background to grey
        self.setScene(self.scene)
        self.setStyleSheet("border: 2px solid black;")
        maxSize = (70*2) + (6*2) + (31*12) + (1*10) + 4
        self.setFixedSize(maxSize, maxSize)
    
    def set_junction(self, junction_data):
        # Updates the display to show the junction represented by junction_data
        self.scene.clear()

        junction = Junction(junction_data)
        junction.setPos(0,0)
        
        self.scene.addItem(junction)

        # Resize self
        width = int(junction.width())
        height = int(junction.height())
        self.scene.setSceneRect(QRectF(0, 0, width, height))


# The following code is temporary for testing
class ImageViewer(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.apply_stylesheet()

        # self.setWindowTitle("Visualisation")
        # self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout(self)

        self.junction_view = JunctionView(self)
        layout.addWidget(self.junction_view)

        button_layout = QHBoxLayout()
        self.button = QPushButton("Randomise", self)
        self.button.clicked.connect(self.randomise_junction)
        button_layout.addWidget(self.button)

        self.go_results_button = QPushButton("Go to Results", self)
        button_layout.addWidget(self.go_results_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.randomise_junction()
    
    def randomise_junction(self):
        data = [
            [],
            [],
            randint(0,1)
        ]

        for _ in range(4):
            data[1].append([])
            for _ in range(3):
                data[1][-1].append(randint(0,1))
            min_lanes = data[1][-1][0] + data[1][-1][2] + 1
            data[0].append(randint(min_lanes,5))
        
        self.junction_view.set_junction(JunctionData(data[0], data[1], data[2]))

        # junction_width = self.junction_view.width()
        # junction_height = self.junction_view.height()
        # button_height = self.button.height()

        # self.button.resize(junction_width, button_height)
        # self.resize(junction_width, junction_height + button_height)

        self.junction_view.updateGeometry()
        self.layout().update()


    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss'), 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     viewer = ImageViewer()
#     viewer.show()
#     sys.exit(app.exec_())
