# Pattern Analysis

This module identifies recurring SIF precursor patterns from safety reports.

The implementation uses Python and SQLite.

## Features

The analyser identifies:

- High-risk activities
- Locations
- Barrier failures
- SIF potential
- Confidence score
- Precursor patterns
- Missing/null values

## Files

### `__init__.py`

Initializes the Python package and exposes the main functions.

### `analyser.py`

Main pattern-analysis logic.

It also creates and manages the SQLite database.

### `api_handoff.py`

Provides Python functions that can be called by the Flask backend.

### `test_analyser.py`

Contains automated unit tests.

## SQLite Database

The database is automatically created at:

```text
data/sif_precursor.db