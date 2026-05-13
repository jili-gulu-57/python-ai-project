from python_ai_project_manager import AIProjectLibrary


def test_list_projects_ignores_tooling_directories(tmp_path):
    (tmp_path / ".idea").mkdir()
    (tmp_path / "AIProject").mkdir()

    projects = AIProjectLibrary(tmp_path).list_projects()

    assert [project.name for project in projects] == ["AIProject"]


def test_list_python_files(tmp_path):
    project = tmp_path / "AIProject"
    project.mkdir()
    source = project / "app.py"
    source.write_text("print('ai')\n", encoding="utf-8")

    files = AIProjectLibrary(tmp_path).list_python_files()

    assert len(files) == 1
    assert files[0].path == source
    assert files[0].project == "AIProject"

