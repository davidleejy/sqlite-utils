from sqlite_utils.db import NotFoundError
import pytest


def test_update_rowid_table(fresh_db):
    table = fresh_db["table"]
    rowid = table.insert({"foo": "bar"}).last_pk
    table.update(rowid, {"foo": "baz"})
    assert [{"foo": "baz"}] == list(table.rows)


def test_update_pk_table(fresh_db):
    table = fresh_db["table"]
    pk = table.insert({"foo": "bar", "id": 5}, pk="id").last_pk
    assert 5 == pk
    table.update(pk, {"foo": "baz"})
    assert [{"id": 5, "foo": "baz"}] == list(table.rows)


def test_update_compound_pk_table(fresh_db):
    table = fresh_db["table"]
    pk = table.insert({"id1": 5, "id2": 3, "v": 1}, pk=("id1", "id2")).last_pk
    assert (5, 3) == pk
    table.update(pk, {"v": 2})
    assert [{"id1": 5, "id2": 3, "v": 2}] == list(table.rows)


@pytest.mark.parametrize(
    "pk,update_pk",
    (
        (None, 2),
        (None, None),
        ("id1", None),
        ("id1", 4),
        (("id1", "id2"), None),
        (("id1", "id2"), 4),
        (("id1", "id2"), (4, 5)),
    ),
)
def test_update_invalid_pk(fresh_db, pk, update_pk):
    table = fresh_db["table"]
    table.insert({"id1": 5, "id2": 3, "v": 1}, pk=pk).last_pk
    with pytest.raises(NotFoundError):
        table.update(update_pk, {"v": 2})


def test_update_alter(fresh_db):
    table = fresh_db["table"]
    rowid = table.insert({"foo": "bar"}).last_pk
    table.update(rowid, {"new_col": 1.2}, alter=True)
    assert [{"foo": "bar", "new_col": 1.2}] == list(table.rows)
    # Let's try adding three cols at once
    table.update(
        rowid,
        {"str_col": "str", "bytes_col": b"\xa0 has bytes", "int_col": -10},
        alter=True,
    )
    assert [
        {
            "foo": "bar",
            "new_col": 1.2,
            "str_col": "str",
            "bytes_col": b"\xa0 has bytes",
            "int_col": -10,
        }
    ] == list(table.rows)
