import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Changed from relative import to absolute import

# filepath: server/test_app.py
class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a test client using Flask's test client
        self.app = app.test_client()
        self.app.testing = True
        # Turn off database initialization for tests
        app.config['TESTING'] = True
        
    def _create_mock_dog(self, dog_id, name, breed):
        """Helper method to create a mock dog with standard attributes"""
        dog = MagicMock(spec=['to_dict', 'id', 'name', 'breed'])
        dog.id = dog_id
        dog.name = name
        dog.breed = breed
        dog.to_dict.return_value = {'id': dog_id, 'name': name, 'breed': breed}
        return dog
        
    def _setup_query_mock(self, mock_query, dogs):
        """Helper method to configure the query mock"""
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.all.return_value = dogs
        return mock_query_instance

    @patch('app.db.session.query')
    def test_get_dogs_success(self, mock_query):
        """Test successful retrieval of multiple dogs"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador")
        dog2 = self._create_mock_dog(2, "Max", "German Shepherd")
        mock_dogs = [dog1, dog2]
        
        self._setup_query_mock(mock_query, mock_dogs)
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        # Verify first dog
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Buddy")
        self.assertEqual(data[0]['breed'], "Labrador")
        
        # Verify second dog
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "Max")
        self.assertEqual(data[1]['breed'], "German Shepherd")
        
        # Verify query was called
        mock_query.assert_called_once()
        
    @patch('app.db.session.query')
    def test_get_dogs_empty(self, mock_query):
        """Test retrieval when no dogs are available"""
        # Arrange
        self._setup_query_mock(mock_query, [])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
        
    @patch('app.db.session.query')
    def test_get_dogs_structure(self, mock_query):
        """Test the response structure for a single dog"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0].keys()), {'id', 'name', 'breed'})
        @patch('app.db.session.query')
        def test_get_breeds_success(self, mock_query):
            """Test successful retrieval of all breeds"""
            # Arrange
            breed1 = MagicMock(id=1, name="Labrador")
            breed2 = MagicMock(id=2, name="German Shepherd")
            mock_breeds = [breed1, breed2]
            
            mock_query.return_value.all.return_value = mock_breeds
            
            # Act
            response = self.app.get('/api/breeds')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(len(data), 2)
            
            # Verify first breed
            self.assertEqual(data[0]['id'], 1)
            self.assertEqual(data[0]['name'], "Labrador")
            
            # Verify second breed
            self.assertEqual(data[1]['id'], 2)
            self.assertEqual(data[1]['name'], "German Shepherd")
            
            # Verify query was called
            mock_query.assert_called_once()

        @patch('app.db.session.query')
        def test_get_breeds_empty(self, mock_query):
            """Test retrieval when no breeds are available"""
            # Arrange
            mock_query.return_value.all.return_value = []
            
            # Act
            response = self.app.get('/api/breeds')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, [])

        @patch('app.db.session.query')
        def test_get_dog_success(self, mock_query):
            """Test successful retrieval of a single dog by ID"""
            # Arrange
            dog = MagicMock(
                id=1,
                name="Buddy",
                breed="Labrador",
                age=3,
                description="Friendly dog",
                gender="Male",
                status=MagicMock(name="Available")
            )
            mock_query.return_value.join.return_value.filter.return_value.first.return_value = dog
            
            # Act
            response = self.app.get('/api/dogs/1')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['id'], 1)
            self.assertEqual(data['name'], "Buddy")
            self.assertEqual(data['breed'], "Labrador")
            self.assertEqual(data['age'], 3)
            self.assertEqual(data['description'], "Friendly dog")
            self.assertEqual(data['gender'], "Male")
            self.assertEqual(data['status'], "Available")
            
            # Verify query was called
            mock_query.assert_called_once()

        @patch('app.db.session.query')
        def test_get_dog_not_found(self, mock_query):
            """Test retrieval of a dog by ID when the dog does not exist"""
            # Arrange
            mock_query.return_value.join.return_value.filter.return_value.first.return_value = None
            
            # Act
            response = self.app.get('/api/dogs/999')
            
            # Assert
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertEqual(data, {"error": "Dog not found"})
            
            # Verify query was called
            mock_query.assert_called_once()

if __name__ == '__main__':
    unittest.main()