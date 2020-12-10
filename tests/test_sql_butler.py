from sql_butler import SQLButler
import pytest


def test_set_up_sqlb():
    sqlb = SQLButler('unit_test_db')
    assert isinstance(sqlb.headers, dict)
    assert sqlb.database_name == 'unit_test_db.sql'


def test_negative_set_up_sql():
    # with pytest.raises(TypeError) as exp:
    #     SQLButler(123456)
    # assert str(exp.value) == 'The provided database name is not a string'
    pass
