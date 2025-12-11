import app.utils.sort as sort_utils
from app import db
import app.tests.helpers as helpers
from app.models import Kelma


def test_sort_all_kelmas_with_no_preserve(app):
    size = 100
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(size)
        sort_utils.sort_all_kelmas()

        kelmas_sort = list(map(lambda kelma: kelma.sort, helpers.get_n_kelmas()))
        sort_set = set()
        # make sure every kelma has a unique sort
        for sort in kelmas_sort:
            assert sort not in sort_set
            sort_set.add(sort)

        assert min(kelmas_sort) == 1
        assert max(kelmas_sort) == len(kelmas_sort)


def test_sort_all_kelmas_return_different_result(app):
    size = 100
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(size)

        sort_utils.sort_all_kelmas()
        kelmas_sort_1 = list(map(lambda kelma: kelma.sort, helpers.get_n_kelmas()))
        sort_utils.sort_all_kelmas()
        kelmas_sort_2 = list(map(lambda kelma: kelma.sort, helpers.get_n_kelmas()))

        assert kelmas_sort_1 != kelmas_sort_2


def test_sort_all_kelmas_with_preserve(app):
    size = 100
    preserve = 5
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(size)

        preserved_kelmas_before = (
            db.session.execute(
                db.select(Kelma).where(Kelma.sort <= preserve).order_by(Kelma.id)
            )
            .scalars()
            .all()
        )
        id_list_before = list(map(lambda kelma: kelma.id, preserved_kelmas_before))

        sort_utils.sort_all_kelmas(preserve)

        preserved_kelmas_after = (
            db.session.execute(
                db.select(Kelma).where(Kelma.sort <= preserve).order_by(Kelma.id)
            )
            .scalars()
            .all()
        )
        id_list_after = list(map(lambda kelma: kelma.id, preserved_kelmas_after))

        assert id_list_before == id_list_after

        kelmas_sort = list(map(lambda kelma: kelma.sort, helpers.get_n_kelmas()))
        sort_set = set()
        # make sure every kelma has a unique sort
        for sort in kelmas_sort:
            assert sort not in sort_set
            sort_set.add(sort)

        assert min(kelmas_sort) == 1
        assert max(kelmas_sort) == len(kelmas_sort)
