"""
Tests for app.models.project module.
"""

import os
import io
import json
import pytest
from unittest.mock import MagicMock

from app.models.project import Project, ProjectStatus, ProjectManager


class TestProjectStatus:
    """Tests for ProjectStatus enum."""

    def test_values(self):
        assert ProjectStatus.CREATED.value == "created"
        assert ProjectStatus.ONTOLOGY_GENERATED.value == "ontology_generated"
        assert ProjectStatus.GRAPH_BUILDING.value == "graph_building"
        assert ProjectStatus.GRAPH_COMPLETED.value == "graph_completed"
        assert ProjectStatus.FAILED.value == "failed"


class TestProject:
    """Tests for the Project dataclass."""

    def test_to_dict(self):
        p = Project(
            project_id="proj_abc123",
            name="Test Project",
            status=ProjectStatus.CREATED,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        d = p.to_dict()
        assert d["project_id"] == "proj_abc123"
        assert d["name"] == "Test Project"
        assert d["status"] == "created"
        assert d["ontology"] is None
        assert d["graph_id"] is None

    def test_from_dict(self):
        data = {
            "project_id": "proj_xyz",
            "name": "From Dict",
            "status": "ontology_generated",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "files": [{"filename": "test.txt"}],
            "total_text_length": 1000,
            "ontology": {"entity_types": []},
            "graph_id": "g123",
        }
        p = Project.from_dict(data)
        assert p.project_id == "proj_xyz"
        assert p.status == ProjectStatus.ONTOLOGY_GENERATED
        assert p.total_text_length == 1000
        assert p.ontology == {"entity_types": []}

    def test_roundtrip(self):
        p = Project(
            project_id="proj_rt",
            name="Roundtrip",
            status=ProjectStatus.GRAPH_COMPLETED,
            created_at="2026-03-01T00:00:00",
            updated_at="2026-03-01T00:00:00",
            graph_id="g456",
            simulation_requirement="Predict trends",
        )
        d = p.to_dict()
        p2 = Project.from_dict(d)
        assert p2.project_id == p.project_id
        assert p2.status == p.status
        assert p2.graph_id == p.graph_id
        assert p2.simulation_requirement == p.simulation_requirement

    def test_from_dict_defaults(self):
        data = {"project_id": "proj_min", "status": "created"}
        p = Project.from_dict(data)
        assert p.name == "Unnamed Project"
        assert p.chunk_size == 500
        assert p.chunk_overlap == 50


class TestProjectManager:
    """Tests for the ProjectManager class."""

    @pytest.fixture(autouse=True)
    def setup_projects_dir(self, tmp_dir):
        """Override PROJECTS_DIR for isolation."""
        self._original = ProjectManager.PROJECTS_DIR
        ProjectManager.PROJECTS_DIR = os.path.join(tmp_dir, "projects")
        os.makedirs(ProjectManager.PROJECTS_DIR, exist_ok=True)
        yield
        ProjectManager.PROJECTS_DIR = self._original

    def test_create_project(self):
        project = ProjectManager.create_project(name="Test")
        assert project.project_id.startswith("proj_")
        assert project.name == "Test"
        assert project.status == ProjectStatus.CREATED

        # Directory should exist
        project_dir = ProjectManager._get_project_dir(project.project_id)
        assert os.path.isdir(project_dir)

        # Meta file should exist
        meta_path = ProjectManager._get_project_meta_path(project.project_id)
        assert os.path.isfile(meta_path)

    def test_save_and_get_project(self):
        project = ProjectManager.create_project(name="Save Test")
        project.status = ProjectStatus.ONTOLOGY_GENERATED
        project.ontology = {"entity_types": [{"name": "Person"}]}
        ProjectManager.save_project(project)

        loaded = ProjectManager.get_project(project.project_id)
        assert loaded is not None
        assert loaded.status == ProjectStatus.ONTOLOGY_GENERATED
        assert loaded.ontology == {"entity_types": [{"name": "Person"}]}

    def test_get_project_nonexistent(self):
        assert ProjectManager.get_project("nonexistent_id") is None

    def test_list_projects(self):
        ProjectManager.create_project(name="Project A")
        ProjectManager.create_project(name="Project B")
        projects = ProjectManager.list_projects()
        assert len(projects) == 2
        # Should be sorted by created_at descending
        assert projects[0].created_at >= projects[1].created_at

    def test_list_projects_with_limit(self):
        for i in range(5):
            ProjectManager.create_project(name=f"Project {i}")
        projects = ProjectManager.list_projects(limit=3)
        assert len(projects) == 3

    def test_delete_project(self):
        project = ProjectManager.create_project(name="To Delete")
        pid = project.project_id
        assert ProjectManager.delete_project(pid) is True
        assert ProjectManager.get_project(pid) is None

    def test_delete_nonexistent(self):
        assert ProjectManager.delete_project("nonexistent") is False

    def test_save_and_get_extracted_text(self):
        project = ProjectManager.create_project(name="Text Test")
        text = "This is extracted text content."
        ProjectManager.save_extracted_text(project.project_id, text)
        loaded = ProjectManager.get_extracted_text(project.project_id)
        assert loaded == text

    def test_get_extracted_text_nonexistent(self):
        project = ProjectManager.create_project(name="No Text")
        assert ProjectManager.get_extracted_text(project.project_id) is None

    def test_save_file_to_project(self):
        project = ProjectManager.create_project(name="File Test")

        # Create a mock FileStorage
        mock_file = MagicMock()
        mock_file.save = lambda path: open(path, "w").write("file content")

        info = ProjectManager.save_file_to_project(
            project.project_id, mock_file, "original.txt"
        )
        assert info["original_filename"] == "original.txt"
        assert info["saved_filename"].endswith(".txt")
        assert os.path.exists(info["path"])

    def test_get_project_files(self):
        project = ProjectManager.create_project(name="Files Test")
        files_dir = ProjectManager._get_project_files_dir(project.project_id)
        os.makedirs(files_dir, exist_ok=True)

        # Create test files
        for name in ["a.txt", "b.txt"]:
            with open(os.path.join(files_dir, name), "w") as f:
                f.write("content")

        file_paths = ProjectManager.get_project_files(project.project_id)
        assert len(file_paths) == 2

    def test_get_project_files_empty(self):
        project = ProjectManager.create_project(name="Empty")
        files = ProjectManager.get_project_files(project.project_id)
        assert files == []
