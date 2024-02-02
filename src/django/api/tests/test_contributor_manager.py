from api.models import Contributor, Source, User

from django.test import TestCase


class ContributorManagerTest(TestCase):
    fixtures = ["users", "contributors"]

    def test_filter_by_name(self):
        matches = Contributor.objects.filter_by_name("factory a")
        self.assertGreater(matches.count(), 0)

        # No result should be returned for exact match
        matches = Contributor.objects.filter_by_name("factory")
        self.assertEqual(matches.count(), 0)

    def test_filter_by_name_verified(self):
        user1 = User.objects.create(email="test1@test.com")
        user2 = User.objects.create(email="test2@test.com")
        c1 = Contributor.objects.create(
            admin=user1,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        c2 = Contributor.objects.create(
            admin=user2,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        matches = Contributor.objects.filter_by_name("TESTING")
        self.assertEqual(2, matches.count())
        # When the names are the same and neither is verified then the second
        # contributor happens to sort first
        self.assertEqual(c2, matches[0])

        c1.is_verified = True
        c1.save()
        matches = Contributor.objects.filter_by_name("TESTING")
        self.assertEqual(2, matches.count())
        # Marking c1 as verified forces it to sort first
        self.assertEqual(c1, matches[0])

    def test_filter_by_name_source(self):
        user1 = User.objects.create(email="test1@test.com")
        user2 = User.objects.create(email="test2@test.com")
        c1 = Contributor.objects.create(
            admin=user1,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        c2 = Contributor.objects.create(
            admin=user2,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        matches = Contributor.objects.filter_by_name("TESTING")
        self.assertEqual(2, matches.count())
        # When the names are the same and neither is verified than the second
        # contributor happens to sort first
        self.assertEqual(c2, matches[0])

        Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=c1,
        )

        matches = Contributor.objects.filter_by_name("TESTING")
        self.assertEqual(2, matches.count())
        # An active source forces it to sort first
        self.assertEqual(c1, matches[0])

    def test_filter_by_name_verified_and_source(self):
        user1 = User.objects.create(email="test1@test.com")
        user2 = User.objects.create(email="test2@test.com")
        c1 = Contributor.objects.create(
            admin=user1,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        c2 = Contributor.objects.create(
            admin=user2,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=c1,
        )

        c2.is_verified = True
        c2.save()

        matches = Contributor.objects.filter_by_name("TESTING")
        self.assertEqual(2, matches.count())
        # A verified contributor sorts before one with a source
        self.assertEqual(c2, matches[0])
