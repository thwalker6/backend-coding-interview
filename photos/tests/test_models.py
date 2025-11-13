from django.test import TestCase
from django.db import IntegrityError

from ..models import Photographer, Photo


class PhotographerModelTest(TestCase):
    def setUp(self):
        # Define test data as class or instance attributes
        self.photographer_data = {
            "photographer_id": 57767809,
            "name": "Felix",
            "url": "https://www.pexels.com/@felix-57767809",
        }
        self.photographer = Photographer.objects.create(**self.photographer_data)

    def test_photographer_creation(self):
        self.assertEqual(
            self.photographer.photographer_id, self.photographer_data["photographer_id"]
        )
        self.assertEqual(self.photographer.name, self.photographer_data["name"])
        self.assertEqual(self.photographer.url, self.photographer_data["url"])

    def test_photographer_string_representation(self):
        expected = f"Felix (ID: 57767809)"
        self.assertEqual(str(self.photographer), expected)

    def test_photo_count_property_with_photos(self):
        Photo.objects.create(
            photo_id=1,
            width=1920,
            height=1080,
            url="https://example.com/photo1",
            src_url="https://example.com/photo1.jpg",
            photographer=self.photographer,
            avg_color="#FF5733",
            alt="Test photo 1",
        )
        Photo.objects.create(
            photo_id=2,
            width=1920,
            height=1080,
            url="https://example.com/photo2",
            src_url="https://example.com/photo2.jpg",
            photographer=self.photographer,
            avg_color="#33FF57",
            alt="Test photo 2",
        )

        self.assertEqual(self.photographer.photo_count, 2)


class PhotoModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.photographer = Photographer.objects.create(
            photographer_id=12345,
            name="Jane Photographer",
            url="https://example.com/photographer/jane",
        )

        self.photo_data = {
            "photo_id": 99999,
            "width": 1920,
            "height": 1080,
            "url": "https://example.com/photos/99999",
            "src_url": "https://example.com/photos/99999.jpg",
            "photographer": self.photographer,
            "avg_color": "#123456",
            "alt": "Beautiful landscape",
        }
        self.photo = Photo.objects.create(**self.photo_data)

    def test_photo_creation(self):
        self.assertEqual(self.photo.photo_id, 99999)
        self.assertEqual(self.photo.width, 1920)
        self.assertEqual(self.photo.height, 1080)
        self.assertEqual(self.photo.url, "https://example.com/photos/99999")
        self.assertEqual(self.photo.src_url, "https://example.com/photos/99999.jpg")
        self.assertEqual(self.photo.photographer, self.photographer)
        self.assertEqual(self.photo.avg_color, "#123456")
        self.assertEqual(self.photo.alt, "Beautiful landscape")

    def test_photo_str_representation(self):
        expected_str = "Photo Beautiful landscape by Jane Photographer"
        self.assertEqual(str(self.photo), expected_str)

    def test_photo_id_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Photo.objects.create(
                photo_id=99999,  # Same photo_id
                width=800,
                height=600,
                url="https://example.com/photos/different",
                src_url="https://example.com/photos/different.jpg",
                photographer=self.photographer,
                avg_color="#ABCDEF",
                alt="Different photo",
            )

    def test_photo_delete(self):
        photo_count_before = Photo.objects.count()
        self.assertEqual(photo_count_before, 1)

        self.photographer.delete()

        photo_count_after = Photo.objects.count()
        self.assertEqual(photo_count_after, 0)

    def test_photo_url_properties(self):
        """Test all photo URL properties generate correct URLs"""
        url_tests = {
            "portrait_url": "?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=800",
            "landscape_url": "?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
            "tiny_pic_url": "?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=200&w=280",
            "extra_large_pic_url": "?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "large_pic_url": "?auto=compress&cs=tinysrgb&h=650&w=940",
            "small_pic_url": "?auto=compress&cs=tinysrgb&h=130",
            "medium_pic_url": "?auto=compress&cs=tinysrgb&h=350",
        }

        for property_name, query_params in url_tests.items():
            with self.subTest(property=property_name):
                expected = f"{self.photo.src_url}{query_params}"
                actual = getattr(self.photo, property_name)
                self.assertEqual(actual, expected)

    def test_photographer_relationship(self):
        photo2 = Photo.objects.create(
            photo_id=88888,
            width=1920,
            height=1080,
            url="https://example.com/photos/88888",
            src_url="https://example.com/photos/88888.jpg",
            photographer=self.photographer,
            avg_color="#654321",
            alt="Second photo",
        )

        photographer_photos = self.photographer.photos.all()
        self.assertEqual(photographer_photos.count(), 2)
        self.assertIn(self.photo, photographer_photos)
        self.assertIn(photo2, photographer_photos)
