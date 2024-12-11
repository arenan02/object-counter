import pytest
from counter.adapters.count_repo import CountSQLDBRepo
from counter.domain.models import ObjectCount

# Database configuration for tests
TEST_DB_CONFIG = {
    "host": "localhost",  # Replace with Docker host or localhost
    "port": 5400,  # Port where PostgreSQL is running
    "database": "test_object_db",
    "user": "postgres",
    "password": "postgres",
}


@pytest.fixture
def repo():
    """
    Fixture to initialize the CountSQLDBRepo with the test database.
    Ensures cleanup after each test.
    """
    repo = CountSQLDBRepo(
        host=TEST_DB_CONFIG["host"],
        port=TEST_DB_CONFIG["port"],
        database=TEST_DB_CONFIG["database"],
    )
    yield repo
    repo.close_connection()


def test_update_and_read_values(repo):
    """
    Test saving and retrieving object counts.
    """
    # Arrange
    object_counts = [
        ObjectCount(object_class="cat", count=2),
        ObjectCount(object_class="dog", count=1),
    ]

    # Act
    repo.update_values(object_counts)

    # Assert
    results = repo.read_values()
    assert len(results) == 2
    assert results[0].object_class == "cat"
    assert results[0].count == 2
    assert results[1].object_class == "dog"
    assert results[1].count == 1


def test_read_values_with_filter(repo):
    """
    Test filtering object counts by object classes.
    """
    # Arrange
    object_counts = [
        ObjectCount(object_class="cat", count=2),
        ObjectCount(object_class="dog", count=1),
        ObjectCount(object_class="car", count=3),
    ]
    repo.update_values(object_counts)

    # Act
    filtered_results = repo.read_values(object_classes=["cat", "car"])

    # Assert
    assert len(filtered_results) == 2
    assert filtered_results[0].object_class == "cat"
    assert filtered_results[0].count == 2
    assert filtered_results[1].object_class == "car"
    assert filtered_results[1].count == 3


def test_update_overwrites_existing_values(repo):
    """
    Test that updating values for the same object class overwrites previous data.
    """
    # Arrange
    initial_counts = [
        ObjectCount(object_class="cat", count=1),
        ObjectCount(object_class="dog", count=2),
    ]
    updated_counts = [
        ObjectCount(object_class="cat", count=3),
        ObjectCount(object_class="dog", count=4),
    ]
    repo.update_values(initial_counts)

    # Act
    repo.update_values(updated_counts)

    # Assert
    results = repo.read_values()
    assert len(results) == 2
    assert results[0].object_class == "cat"
    assert results[0].count == 3
    assert results[1].object_class == "dog"
    assert results[1].count == 4
