from report import make_sort_key
from pytest import raises




def test_make_sort_key():
    assert make_sort_key("500.2") == 500.2
    assert make_sort_key("20240722") == 20240722





if __name__ == "__main__":
    main()
