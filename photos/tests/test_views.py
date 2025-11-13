from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Photo, Photographer


class PhotographerViewSetTest(APITestCase):
    def setUp(self):
        """Set up test data and authentication"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Create test photographers
        self.photographer1 = Photographer.objects.create(
            photographer_id=57767809,
            name='Felix',
            url='https://www.pexels.com/@felix-57767809'
        )
        self.photographer2 = Photographer.objects.create(
            photographer_id=55954677,
            name='Centre for Ageing Better',
            url='https://www.pexels.com/@centre-for-ageing-better-55954677'
        )
        
        # Create test photos
        self.photo1 = Photo.objects.create(
            photo_id=111,
            width=1920,
            height=1080,
            url='https://www.pexels.com/photo/a-small-island-surrounded-by-trees-in-the-middle-of-a-lake-21751820/',
            src_url='https://images.pexels.com/photos/21751820/pexels-photo-21751820.jpeg',
            photographer=self.photographer1,
            avg_color='#FF5733',
            alt='Photo by Alice'
        )
        self.photo2 = Photo.objects.create(
            photo_id=222,
            width=1920,
            height=1080,
            url='https://www.pexels.com/photo/elderly-man-and-woman-with-bikes-at-park-21405575/',
            src_url='https://images.pexels.com/photos/21405575/pexels-photo-21405575.jpeg',
            photographer=self.photographer1,
            avg_color='#33FF57',
            alt='Another photo by Alice'
        )
        
        # URLs
        self.list_url = reverse('photos:photographers-list')
        self.detail_url = reverse('photos:photographers-detail', kwargs={'pk': self.photographer1.pk})

    def test_list_photographers_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_photographers_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_photographer_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Felix')
        self.assertEqual(response.data['photographer_id'], 57767809)

    def test_retrieve_photographer_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Felix')

    def test_create_photographer_unauthenticated(self):
        data = {
            'photographer_id': 99999,
            'name': 'Charlie Brown',
            'url': 'https://example.com/charlie'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_photographer_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photographer_id': 99999,
            'name': 'Charlie Brown',
            'url': 'https://example.com/charlie'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Charlie Brown')
        self.assertEqual(response.data['photographer_id'], 99999)
        self.assertEqual(Photographer.objects.count(), 3)

    def test_update_photographer_unauthenticated(self):
        """Test that unauthenticated users cannot update photographers"""
        data = {
            'photographer_id': 12345,
            'name': 'Alice Updated',
            'url': 'https://example.com/alice-updated'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_photographer_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photographer_id': 12345,
            'name': 'Alice Updated',
            'url': 'https://example.com/alice-updated'
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Alice Updated')
        
        # Verify in database
        self.photographer1.refresh_from_db()
        self.assertEqual(self.photographer1.name, 'Alice Updated')

    def test_partial_update_photographer_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'name': 'Alice Partially Updated'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Alice Partially Updated')
        self.assertEqual(response.data['photographer_id'], 57767809)

    def test_delete_photographer_unauthenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_photographer_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Photographer.objects.count(), 1)

    def test_filter_photographer_by_id(self):
        url = f"{self.list_url}?photographer_id=57767809"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['photographer_id'], 57767809)

    def test_photographer_ordering(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(results[0]['name'], 'Centre for Ageing Better')
        self.assertEqual(results[1]['name'], 'Felix')

    def test_photographer_photos_action_unauthenticated(self):
        url = reverse('photos:photographers-photos', kwargs={'pk': self.photographer1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_photographer_photos_action_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        url = reverse('photos:photographers-photos', kwargs={'pk': self.photographer1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['photo_id'], 222)
        self.assertEqual(response.data[1]['photo_id'], 111)

    def test_photographer_photos_action_no_photos(self):
        url = reverse('photos:photographers-photos', kwargs={'pk': self.photographer2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_uses_list_serializer(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_count', response.data[0])

    def test_retrieve_uses_detail_serializer(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertIn('url', response.data)


class PhotoViewSetTest(APITestCase):

    def setUp(self):
        """Set up test data and authentication"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Create test photographer
        self.photographer = Photographer.objects.create(
            photographer_id=12345,
            name='Test Photographer',
            url='https://example.com/photographer'
        )
        
        # Create test photos
        self.photo1 = Photo.objects.create(
            photo_id=111,
            width=1920,
            height=1080,
            url='https://example.com/photo1',
            src_url='https://example.com/photo1.jpg',
            photographer=self.photographer,
            avg_color='#FF5733',
            alt='Beautiful landscape'
        )
        self.photo2 = Photo.objects.create(
            photo_id=222,
            width=800,
            height=600,
            url='https://example.com/photo2',
            src_url='https://example.com/photo2.jpg',
            photographer=self.photographer,
            avg_color='#33FF57',
            alt='Portrait photo'
        )
        
        # URLs
        self.list_url = reverse('photos:photos-list')
        self.detail_url = reverse('photos:photos-detail', kwargs={'pk': self.photo1.pk})

    def test_list_photos(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_photo(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['photo_id'], 111)

    def test_create_photo_unauthenticated(self):
        data = {
            'photo_id': 999,
            'width': 1024,
            'height': 768,
            'url': 'https://example.com/photo999',
            'src_url': 'https://example.com/photo999.jpg',
            'photographer': self.photographer.pk,
            'avg_color': '#ABCDEF',
            'alt': 'New photo'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_photo_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photo_id': 999,
            'width': 1024,
            'height': 768,
            'url': 'https://example.com/photo999',
            'src_url': 'https://example.com/photo999.jpg',
            'photographer': {
                'photographer_id':57767809,
                'name':'Felix',
                'url':'https://www.pexels.com/@felix-57767809'
            },
            'avg_color': '#ABCDEF',
            'alt': 'New photo'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['photo_id'], 999)
        self.assertEqual(response.data['alt'], 'New photo')
        self.assertEqual(Photo.objects.count(), 3)

    def test_update_photo_unauthenticated(self):
        data = {
            'photo_id': 999,
            'width': 1024,
            'height': 768,
            'url': 'https://example.com/photo999',
            'src_url': 'https://example.com/photo999.jpg',
            'photographer': {
                'photographer_id':57767809,
                'name':'Felix',
                'url':'https://www.pexels.com/@felix-57767809'
            },
            'avg_color': '#ABCDEF',
            'alt': 'New photo'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_photo_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photo_id': 111,
            'width': 1920,
            'height': 1080,
            'url': 'https://example.com/photo1',
            'src_url': 'https://example.com/photo1.jpg',
            'photographer': self.photographer.pk,
            'avg_color': '#FF5733',
            'alt': 'Updated landscape'
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['alt'], 'Updated landscape')

    def test_partial_update_photo_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'alt': 'Partially updated alt text'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['alt'], 'Partially updated alt text')
        self.assertEqual(response.data['photo_id'], 111)

    def test_delete_photo_unauthenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_photo_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Photo.objects.count(), 1)

    def test_filter_photo_by_photographer(self):
        url = f"{self.list_url}?photographer={self.photographer.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_photo_by_photo_id(self):
        url = f"{self.list_url}?photo_id=111"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['photo_id'], 111)

    def test_photo_ordering_default(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertTrue(results[0]['id'] > results[1]['id'])

    def test_list_uses_list_serializer(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_id', response.data[0])

    def test_retrieve_uses_detail_serializer(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photographer', response.data)
        self.assertIn('alt', response.data)

    def test_photo_validation_invalid_photo_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photo_id': 111,  # Duplicate
            'width': 1024,
            'height': 768,
            'url': 'https://example.com/photo-dup',
            'src_url': 'https://example.com/photo-dup.jpg',
            'photographer': self.photographer.pk,
            'avg_color': '#ABCDEF',
            'alt': 'Duplicate photo'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_photo_with_nonexistent_photographer(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'photo_id': 999,
            'width': 1024,
            'height': 768,
            'url': 'https://example.com/photo999',
            'src_url': 'https://example.com/photo999.jpg',
            'photographer': 99999,  # Non-existent
            'avg_color': '#ABCDEF',
            'alt': 'New photo'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)