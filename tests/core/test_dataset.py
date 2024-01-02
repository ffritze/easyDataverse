import json
import pytest

from easyDataverse.dataset import Dataset
from easyDataverse.file import File


class TestFileAddition:
    def test_add_file(self):
        """Tests whether the addition of a file works"""

        # Initialize dataset
        dataset = Dataset()

        # Add a random file
        dataset.add_file(dv_dir="mydir", local_path=".tests/fixture/toydataset.py")

        assert isinstance(
            dataset.files[0], File
        ), f"Expected File type, got {dataset.files[0].__class__.__name__}"

        assert dataset.files[0].filename == "toydataset.py", "Filename has changed"
        assert dataset.files[0].dv_dir == "mydir", "Dataverse directory has changed"
        assert (
            dataset.files[0].local_path == ".tests/fixture/toydataset.py"
        ), "Local path is incorrect"

        # Test adding the same file again -> Should result in an error
        with pytest.raises(FileExistsError):
            dataset.add_file(dv_dir="mydir", local_path=".tests/fixture/toydataset.py")

    def test_add_directory_fail(self):
        """Tests whether the addition of a directory that doesnt exist fails"""

        # initialize dataset
        dataset = Dataset()

        with pytest.raises(FileNotFoundError):
            # Should not work
            dataset.add_directory("./dir/does/not/exist")

    def test_add_directory_no_hidden(self):
        """Tests whether the addition of a directory works"""

        # initialize dataset
        dataset = Dataset()

        # Add directory from fixtures
        path = "./tests/fixture/upload_dir"
        dataset.add_directory("./tests/fixtures/upload_dir")

        # Set up cases to test for (without hidden)
        local_paths = [
            "./tests/fixtures/upload_dir/directory/another.file",
            "./tests/fixtures/upload_dir/some.file",
        ]

        assert list(
            filter(lambda file: file.local_path == local_paths[0], dataset.files)
        ), f"File '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[1]}' does not exist."

        dv_paths = [
            "directory/another.file",
            "some.file",
        ]

        assert list(
            filter(lambda file: file.filename == dv_paths[0], dataset.files)
        ), f"DV Path '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[1]}' does not exist."

        assert not list(
            filter(lambda file: ".hiddendir" in file.local_path, dataset.files)
        ), "Includes hidden dir, although not specified."

        assert not list(
            filter(lambda file: ".ishidden" in file.local_path, dataset.files)
        ), "Includes hidden dir, although not specified."

        assert not list(
            filter(lambda file: "shouldnot.include" in file.local_path, dataset.files)
        ), "Includes file from hidden dir, although not specified."

    def test_add_directory_with_hidden(self):
        """Tests whether the addition of a directory works with including hidden files"""

        # initialize dataset
        dataset = Dataset()

        # Add directory from fixtures
        dataset.add_directory("./tests/fixtures/upload_dir", include_hidden=True)

        # Set up cases to test for (without hidden)
        local_paths = [
            "./tests/fixtures/upload_dir/directory/another.file",
            "./tests/fixtures/upload_dir/.hiddendir/shouldnot.include",
            "./tests/fixtures/upload_dir/some.file",
            "./tests/fixtures/upload_dir/.ishidden",
        ]

        assert list(
            filter(lambda file: file.local_path == local_paths[0], dataset.files)
        ), f"File '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[1]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[2]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[3]}' does not exist."

        dv_paths = [
            "directory/another.file",
            ".hiddendir/shouldnot.include",
            "some.file",
            ".ishidden",
        ]

        assert list(
            filter(lambda file: file.filename == dv_paths[0], dataset.files)
        ), f"DV Path '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[1]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[2]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[3]}' does not exist."

    def test_add_directory_with_ignore(self):
        """Tests whether the addition of a directory works with ignores"""

        # initialize dataset
        dataset = Dataset()

        # Add directory from fixtures
        dataset.add_directory(
            "./tests/fixtures/upload_dir", include_hidden=True, ignores=[".hiddendir"]
        )

        # Set up cases to test for (without hidden)
        local_paths = [
            "./tests/fixtures/upload_dir/directory/another.file",
            "./tests/fixtures/upload_dir/some.file",
            "./tests/fixtures/upload_dir/.ishidden",
        ]

        assert list(
            filter(lambda file: file.local_path == local_paths[0], dataset.files)
        ), f"File '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[1]}' does not exist."

        assert list(
            filter(lambda file: file.local_path == local_paths[1], dataset.files)
        ), f"File '{local_paths[2]}' does not exist."

        dv_paths = [
            "directory/another.file",
            "some.file",
            ".ishidden",
        ]

        assert list(
            filter(lambda file: file.filename == dv_paths[0], dataset.files)
        ), f"DV Path '{local_paths[0]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[1]}' does not exist."

        assert list(
            filter(lambda file: file.filename == dv_paths[1], dataset.files)
        ), f"DV Path '{local_paths[2]}' does not exist."

    def test_has_hidden_dir(self):
        """Tests whether the function detects hidden directories"""

        path = "./.hiddendir"
        assert Dataset._has_hidden_dir(
            path, "some/dirpath"
        ), "Hidden dir is not ignored"

        assert not Dataset._has_hidden_dir(path, path), "Root dir is ignored"

    def test_has_ignore_dirs(self):
        """Tests whether the function detects ignore directories from an ignore list"""

        path = "some/ignored_dir"
        assert Dataset._has_ignore_dirs(
            path, ".", ["ignored_dir"]
        ), "Directory 'ignored_dir' is not ignored"


class TestDataverseExport:
    def test_dataverse_dict(self, metadatablock, dataverse_json):
        """Tests whether the output of the dataverse JSON export works"""

        # Build dataset
        dataset = Dataset()
        dataset.add_metadatablock(metadatablock)

        # Compare dictionary
        assert dataset.dataverse_dict() == json.loads(
            dataverse_json
        ), "Dataverse Dict output does not match expected output"

    def test_dataverse_json(self, metadatablock, dataverse_json):
        """Tests whether the output of the dataverse JSON export works"""

        # Build dataset
        dataset = Dataset()
        dataset.add_metadatablock(metadatablock)

        # Compare JSON output with expected output
        assert (
            dataset.dataverse_json() == dataverse_json
        ), "Dataverse JSON output does not match expected output"


class TestUtils:
    def test_snake_to_camel(self):
        """Tests snake to camel case conversion"""

        snake = "this_is_snake"

        assert (
            Dataset._snake_to_camel(snake) == "ThisIsSnake"
        ), "Snake to camel conversion failed"

    def test_keys_to_camel(self):
        """Tests whether the conversion of a snake keyed dict works"""

        # Set input
        snake_dict = {
            "this_is_snake": "ThisIsSnake",
            "this_is_sub": {"another_snake": "AnotherSnake"},
        }

        # Set expectation
        camel_dict = {
            "ThisIsSnake": "ThisIsSnake",
            "ThisIsSub": {"AnotherSnake": "AnotherSnake"},
        }

        # Initialize dataset to use instance method
        fun = Dataset()._keys_to_camel

        assert (
            fun(snake_dict) == camel_dict
        ), "Snake dict to camel dict conversion failed."
