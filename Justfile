@_default:
    just --list

# Initialize repository
@init:
    uv sync

run-pyside2:
	uv run python pyside2.py

run-pyside6:
	uv run python pyside6.py

run-pyqt5:
	uv run python pyqt5.py

run-pyqt6:
	uv run python pyqt6.py
