"""Test libutil."""
from pathlib import Path

import pytest

from haddock.libs.libutil import (
    convert_seconds_to_min_sec,
    extract_keys_recursive,
    file_exists,
    get_number_from_path_stem,
    non_negative_int,
    recursive_dict_update,
    sort_numbered_paths,
    transform_to_list,
    )


@pytest.mark.parametrize(
    'i,expected',
    [
        (1, 1),
        ('1', 1),
        (0, 0),
        ('0', 0),
        ],
    )
def test_non_negative_int(i, expected):
    """."""
    r = non_negative_int(i)
    assert r == expected


@pytest.mark.parametrize('i', [-1, -12, -14])
def test_non_negative_int_error(i):
    """."""
    with pytest.raises(ValueError):
        non_negative_int(i)


@pytest.mark.parametrize(
    'i,expected',
    [
        (Path(__file__), Path(__file__)),
        (str(Path(__file__)), Path(__file__)),
        ],
    )
def test_file_exists(i, expected):
    """."""
    r = file_exists(i)
    assert r == expected


@pytest.mark.parametrize(
    'i',
    [
        'some_bad.path',
        Path(__file__).parent,  # this is a folder
        ],
    )
def test_file_exists_wrong(i):
    """."""
    with pytest.raises(ValueError):
        file_exists(i)


@pytest.mark.parametrize(
    'in1,expected',
    [
        ('pdb_1.pdb', 1),
        ('pdb2.pdb', 2),
        ('pdb2.pdb', 2),
        ('pdb_3.pdb', 3),
        ('pdb_1231.pdb', 1231),
        ('pdb_0011.pdb', 11),
        ('pdb_1_.pdb', 1),
        ('pdb_1', 1),
        ('5', 5),
        ('pdb_20200101_1.pdb', 1),
        ],
    )
def test_get_number(in1, expected):
    """Test get number from path."""
    result = get_number_from_path_stem(in1)
    assert result == expected


@pytest.mark.parametrize(
    'in1,expected',
    [
        (
            ['f_1.pdb', 'f_11.pdb', 'f_2.pdb'],
            ['f_1.pdb', 'f_2.pdb', 'f_11.pdb'],
            ),
        (
            ['b.pdb', 'c.pdb', 'a.pdb'],
            ['a.pdb', 'b.pdb', 'c.pdb']),
        ],
    )
def test_sort_numbered_input_1(in1, expected):
    """Test sort numbered inputs."""
    result = sort_numbered_paths(*in1)
    assert result == expected


@pytest.mark.parametrize(
    'in1,error',
    [
        (['f_1.pdb', 'f_11.pdb', 'f_2.pdb'], TypeError),
        ]
    )
def test_sort_numbered_inputs_error(in1, error):
    """Test sort numbered inputs raised Errors."""
    with pytest.raises(error):
        sort_numbered_paths(in1)


def test_recursive_dict_update():
    """Test recursive dict update."""
    a = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    _list = list(range(10))
    b = {"a": 2, "b": {"d": {"e": 4}}, "z": {"z1": _list}}
    c = recursive_dict_update(a, b)
    assert a is not c
    assert a["b"] is not c["b"]
    assert a["b"]["d"] is not c["b"]["d"]
    assert b["z"]["z1"] is not c["z"]["z1"]
    assert c == {"a": 2, "b": {"c": 2, "d": {"e": 4}}, "z": {"z1": _list}}


def test_recursive_dict_update_empty():
    """Test recursive dict update."""
    a = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    c = recursive_dict_update(a, {})
    assert a is not c
    assert a == c


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (60, "1 minute and 0 seconds"),
        (120, "2 minutes and 0 seconds"),
        (40, "40 seconds"),
        (179, "2 minutes and 59 seconds"),
        (3600, "1h0m0s"),
        (3601, "1h0m1s"),
        (3600 + 120, "1h2m0s"),
        (3600 + 125, "1h2m5s"),
        (3600 * 2 + 125, "2h2m5s"),
        (3600 * 2 + 179, "2h2m59s"),
        (3600 * 2 + 180, "2h3m0s"),
        ]
    )
def test_convert_seconds(seconds, expected):
    """Convert seconds to min&sec."""
    result = convert_seconds_to_min_sec(seconds)
    assert result == expected


a = {
    "param1": 1,
    "param2": {"param3": 4, "param4": {"param5": {"param6": 7, "param7": 8}}},
    }
b = {"param1", "param3", "param6", "param7"}


@pytest.mark.parametrize(
    "inp,expected",
    [
        (a, b),
        ]
    )
def test_extract_keys_recursive(inp, expected):
    """Test extract keys recursive."""
    result = set(extract_keys_recursive(inp))
    assert result == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        [1, [1]],
        [Path("a"), [Path("a")]],
        [list(range(10)), list(range(10))],
        [tuple(range(10)), tuple(range(10))],
        [1.1, [1.1]],
        ["a", ["a"]],
        [set([1, 2, 3]), [1, 2, 3]],
        [{"a": 1}, ["a"]],
        [None, [None]],
        ]
    )
def test_transform_to_list(value, expected):
    result = transform_to_list(value)
    assert result == expected
