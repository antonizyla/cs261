import pytest
from params import Parameters


class TestParameters:
    """Unit tests for the Parameters class."""

    def test_default_initialisation(self):
        """Ensure Parameters initializes with correct default values."""
        params = Parameters()
        assert params.get_no_lanes() == [2, 2, 2, 2]
        assert params.has_pedestrian_crossing() == [False, False, False, False]
        assert params.get_crossing_time() == [0, 0, 0, 0]
        assert params.get_crossing_rph() == [0, 0, 0, 0]
        assert params.get_sequencing_priority() == [1, 1, 1, 1]

    def test_custom_initialisation(self):
        """Ensure custom values are set correctly."""
        params = Parameters(
            no_lanes=[3, 2, 4, 1],
            pedestrian_crossing=[True, False, True, False],
            crossing_time=[10, 15, 20, 25],
            crossing_rph=[5, 10, 15, 20],
            sequencing_priority=[3, 1, 2, 4]
        )

        assert params.get_no_lanes() == [3, 2, 4, 1]
        assert params.has_pedestrian_crossing() == [True, False, True, False]
        assert params.get_crossing_time() == [10, 15, 20, 25]
        assert params.get_crossing_rph() == [5, 10, 15, 20]
        assert params.get_sequencing_priority() == [3, 1, 2, 4]

    def test_check_valid_parameters(self):
        """Ensure valid parameter sets pass the check function."""
        params = Parameters(
            no_lanes=[1, 2, 3, 4],
            pedestrian_crossing=[True, True, False, False],
            crossing_time=[5, 10, 15, 20],
            crossing_rph=[3, 6, 9, 12],
            sequencing_priority=[2, 3, 1, 4]
        )
        assert params.check() is True

    def test_invalid_no_lanes(self):
        """Ensure invalid lane values are caught."""
        invalid_values = [
            [-1, 2, 3, 4],  # Negative lane count
            [1, 2, 6, 4],  # Exceeding max lane limit (5)
            [1, 2, 3],  # Missing one value
            [1, 2, 3, 4.5]  # Float instead of int
        ]
        for no_lanes in invalid_values:
            assert Parameters(no_lanes=no_lanes).check() is False, f"Failed for no_lanes={no_lanes}"

    def test_invalid_pedestrian_crossing(self):
        """Ensure pedestrian crossing values are validated."""
        invalid_values = [
            [True, False, "yes", False],  # Non-boolean string
            [True, False, 1, 0],  # Integers instead of booleans
            [True, False, False],  # Missing one value
        ]
        for pedestrian_crossing in invalid_values:
            assert Parameters(pedestrian_crossing=pedestrian_crossing).check() is False, f"Failed for pedestrian_crossing={pedestrian_crossing}"

    def test_invalid_crossing_time(self):
        """Ensure crossing time is validated with realistic edge cases."""
        invalid_values = [
            [-5, 10, 15, 20],  # Negative values (invalid)
            [5, 10, 15],  # Missing one value (invalid)
        ]
        
        for crossing_time in invalid_values:
            try:
                params = Parameters(crossing_time=crossing_time)
                assert params.check() is False, f"Failed for crossing_time={crossing_time}"
            except TypeError:
                pytest.fail(f"TypeError raised unexpectedly for crossing_time={crossing_time}")



    def test_invalid_crossing_rph(self):
        """Ensure crossing requests per hour (RPH) is validated."""
        invalid_values = [
            [-1, 5, 10, 15],  # Negative values
            [5, 10, 15, 35],  # Exceeding max limit (30)
            [5, 10, 15],  # Missing one value
        ]
        for crossing_rph in invalid_values:
            assert Parameters(crossing_rph=crossing_rph).check() is False, f"Failed for crossing_rph={crossing_rph}"

    def test_invalid_sequencing_priority(self):
        """Ensure sequencing priority values are validated."""
        invalid_values = [
            [-1, 2, 3, 4],  # Negative priority value
            [1, 2, 3, 5],  # Exceeding max priority (4)
            [1, 2, 3],  # Missing one value
            [1, 2, 3, 4.5],  # Float instead of int
        ]
        for sequencing_priority in invalid_values:
            assert Parameters(sequencing_priority=sequencing_priority).check() is False, f"Failed for sequencing_priority={sequencing_priority}"

    def test_is_valid_param_set(self):
        """Ensure placeholder function for validation."""
        params = Parameters()
        assert params.is_valid_param_set() is None  # Should be implemented later
