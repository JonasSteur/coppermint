from pytest import fixture

from django.core.cache import cache


@fixture(autouse=True)
def enable_db_access_for_all_tests(db) -> None:
    """
    This enables database access for all unit tests. The alternative is to mark those that need it with @mark.django_db,
    but at this point, most tests need it, so we enable it globally.
    """


@fixture(autouse=True)
def clear_cache_after_test_run():
    yield cache.clear()
