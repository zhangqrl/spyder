# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License

"""
Tests for collectionseditor.py
"""

# Standard library imports
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock # Python 2

# Third party imports
import pandas
import pytest

# Local imports
from spyder.widgets.variableexplorer.collectionseditor import (
    CollectionsEditorTableView, CollectionsModel)
from spyder.widgets.variableexplorer.tests.test_dataframeeditor import \
    generate_pandas_indexes

# Helper functions
def data(cm, i, j):
    return cm.data(cm.createIndex(i, j))

# --- Tests
# -----------------------------------------------------------------------------

def test_create_dataframeeditor_with_correct_format(qtbot, monkeypatch):
    MockDataFrameEditor = Mock()
    mockDataFrameEditor_instance = MockDataFrameEditor()
    monkeypatch.setattr('spyder.widgets.variableexplorer.collectionseditor.DataFrameEditor',
                        MockDataFrameEditor)
    df = pandas.DataFrame(['foo', 'bar'])
    editor = CollectionsEditorTableView(None, {'df': df})
    qtbot.addWidget(editor)
    editor.set_dataframe_format('%10d')
    editor.delegate.createEditor(None, None, editor.model.createIndex(0, 3))
    mockDataFrameEditor_instance.dataModel.set_format.assert_called_once_with('%10d')

def test_accept_sig_option_changed_from_dataframeeditor(qtbot, monkeypatch):
    df = pandas.DataFrame(['foo', 'bar'])
    editor = CollectionsEditorTableView(None, {'df': df})
    qtbot.addWidget(editor)
    editor.set_dataframe_format('%10d')
    assert editor.model.dataframe_format == '%10d'
    editor.delegate.createEditor(None, None, editor.model.createIndex(0, 3))
    dataframe_editor = next(iter(editor.delegate._editors.values()))['editor']
    qtbot.addWidget(dataframe_editor)
    dataframe_editor.sig_option_changed.emit('dataframe_format', '%5f')
    assert editor.model.dataframe_format == '%5f'

def test_collectionsmodel_with_two_ints():
    coll = {'x': 1, 'y': 2}
    cm = CollectionsModel(None, coll)
    assert cm.rowCount() == 2
    assert cm.columnCount() == 4
    # dict is unordered, so first row might be x or y
    assert data(cm, 0, 0) in {'x', 'y'}
    if data(cm, 0, 0) == 'x':
        row_with_x = 0
        row_with_y = 1
    else:
        row_with_x = 1
        row_with_y = 0
    assert data(cm, row_with_x, 1) == 'int'
    assert data(cm, row_with_x, 2) == '1'
    assert data(cm, row_with_x, 3) == '1'
    assert data(cm, row_with_y, 0) == 'y'
    assert data(cm, row_with_y, 1) == 'int'
    assert data(cm, row_with_y, 2) == '1'
    assert data(cm, row_with_y, 3) == '2'

def test_collectionsmodel_with_index():
    # Regression test for issue #3380, modified for #3758
    for rng_name, rng in generate_pandas_indexes().items():
        coll = {'rng': rng}
        cm = CollectionsModel(None, coll)
        assert data(cm, 0, 0) == 'rng'
        assert data(cm, 0, 1) == rng_name
        assert data(cm, 0, 2) == '(20,)' or data(cm, 0, 2) == '(20L,)'
        assert data(cm, 0, 3) == rng.summary()

def test_shows_dataframeeditor_when_editing_index(qtbot, monkeypatch):
    for rng_name, rng in generate_pandas_indexes().items():
        MockDataFrameEditor = Mock()
        mockDataFrameEditor_instance = MockDataFrameEditor()
        monkeypatch.setattr('spyder.widgets.variableexplorer.collectionseditor.DataFrameEditor',
                            MockDataFrameEditor)
        coll = {'rng': rng}
        editor = CollectionsEditorTableView(None, coll)
        editor.delegate.createEditor(None, None,
                                     editor.model.createIndex(0, 3))
        mockDataFrameEditor_instance.show.assert_called_once_with()

if __name__ == "__main__":
    pytest.main()