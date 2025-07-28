import pytest
from test_files.add import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-2, -3) == -5

def test_add_positive_and_negative_numbers():
    assert add(2, -3) == -1

def test_add_zero():
    assert add(5, 0) == 5

def test_add_large_numbers():
    assert add(1000000, 2000000) == 3000000