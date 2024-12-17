import pytest
from dotenv import load_dotenv
import os
from counter.adapters.count_repo import CountSQLDBRepo
from counter.domain.models import ObjectCount

# Load environment variables from the .env file
load_dotenv()

@pytest.fixture
def repo():
    """
    Fixture to initialize the CountSQLDBRepo with the test database.
    Ensures cleanup before each test.
    """
    repo = CountSQLDBRepo(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
    )
    # Cleanup before each test
    with repo.conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE object_counts;")
    repo.conn.commit()
    yield repo
    # Optional: Additional cleanup after each test
    with repo.conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE object_counts;")
    repo.conn.commit()


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