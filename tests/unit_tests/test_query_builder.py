from app.utils.query_builder import dict_to_sqlalchemy_filter_options
from app.models import Users


def test_filter_eq_int():
    filt = dict_to_sqlalchemy_filter_options(Users, {"id": 1})
    assert filt is not None


def test_filter_like_str():
    filt = dict_to_sqlalchemy_filter_options(Users, {"email": "test"})
    assert filt is not None


def test_filter_bool():
    filt = dict_to_sqlalchemy_filter_options(Users, {"is_active": True})
    assert filt is not None


def test_filter_operators():
    filt = dict_to_sqlalchemy_filter_options(Users, {"id__gte": 1, "id__lte": 10})
    assert filt is not None


def test_filter_isnull():
    filt = dict_to_sqlalchemy_filter_options(Users, {"photo__isnull": True})
    assert filt is not None
