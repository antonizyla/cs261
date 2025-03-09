import pytest
from results import ResultSet  # Importing ResultSet from result.py


class TestResultSet:
    def setup_method(self):
        """Initialize ResultSet instance before each test."""
        self.result = ResultSet(northRoad=10, eastRoad=15, southRoad=20, westRoad=25, overallScore=70)

    def test_initialization(self):
        """Test that the ResultSet initializes correctly with given values."""
        assert self.result.northRoad == 10
        assert self.result.eastRoad == 15
        assert self.result.southRoad == 20
        assert self.result.westRoad == 25
        assert self.result.overallScore == 70

    def test_get_north_road(self):
        """Ensure getNorthRoad() returns the correct value."""
        assert self.result.getNorthRoad() == 10

    def test_get_east_road(self):
        """Ensure getEastRoad() returns the correct value."""
        assert self.result.getEastRoad() == 15

    def test_get_south_road(self):
        """Ensure getSouthRoad() returns the correct value."""
        assert self.result.getSouthRoad() == 20

    def test_get_west_road(self):
        """Ensure getWestRoad() returns the correct value."""
        assert self.result.getWestRoad() == 25

    def test_get_score(self):
        """Ensure getScore() returns the correct value."""
        assert self.result.getScore() == 70

    def test_zero_values(self):
        """Ensure that a ResultSet with zero values works correctly."""
        zero_result = ResultSet(northRoad=0, eastRoad=0, southRoad=0, westRoad=0, overallScore=0)
        assert zero_result.getNorthRoad() == 0
        assert zero_result.getEastRoad() == 0
        assert zero_result.getSouthRoad() == 0
        assert zero_result.getWestRoad() == 0
        assert zero_result.getScore() == 0

    def test_negative_values(self):
        """Ensure that ResultSet correctly handles negative values."""
        negative_result = ResultSet(northRoad=-5, eastRoad=-10, southRoad=-15, westRoad=-20, overallScore=-50)
        assert negative_result.getNorthRoad() == -5
        assert negative_result.getEastRoad() == -10
        assert negative_result.getSouthRoad() == -15
        assert negative_result.getWestRoad() == -20
        assert negative_result.getScore() == -50

    def test_large_values(self):
        """Ensure that ResultSet handles large values correctly."""
        large_result = ResultSet(northRoad=1000000, eastRoad=2000000, southRoad=3000000, westRoad=4000000, overallScore=10000000)
        assert large_result.getNorthRoad() == 1000000
        assert large_result.getEastRoad() == 2000000
        assert large_result.getSouthRoad() == 3000000
        assert large_result.getWestRoad() == 4000000
        assert large_result.getScore() == 10000000
