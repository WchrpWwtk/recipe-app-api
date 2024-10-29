"""
Tests for the tags API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.models import Recipe
from tag.models import Tag

from ..serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """
    Create and return a tag detail url.
    :param tag_id:
    :return:
    """
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """
    Create and return a user.
    :param email:
    :param password:
    :return:
    """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test auth is required for retrieving tags.
        :return:
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving a list of tags.
        :param self:
        :return:
        """
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test list of tags is limited to authenticated user.
        :param self:
        :return:
        """
        user_2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user_2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """
        Test updating a tag.
        :return:
        """
        tag = Tag.objects.create(user=self.user, name="After Dinner")
        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """
        Test deleting a tag.
        :return:
        """
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """
        Test listing tags to those assigned to recipes.
        :return:
        """
        tag_1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag_2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Green Eggs on Toast",
            time_minutes=10,
            price=Decimal("2.5"),
            user=self.user,
        )
        recipe.tags.add(tag_1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s_1 = TagSerializer(tag_1)
        s_2 = TagSerializer(tag_2)

        self.assertIn(s_1.data, res.data)
        self.assertNotIn(s_2.data, res.data)

    def test_filtered_tags_unique(self):
        """
        Test filtered tags returns a unique list.
        :return:
        """
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Dinner")

        recipe_1 = Recipe.objects.create(
            title="Pancakes",
            time_minutes=5,
            price=Decimal("5"),
            user=self.user,
        )
        recipe_2 = Recipe.objects.create(
            title="Porridge",
            time_minutes=3,
            price=Decimal("2"),
            user=self.user,
        )

        recipe_1.tags.add(tag)
        recipe_2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
