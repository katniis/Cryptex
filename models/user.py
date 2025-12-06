"""
User Model
Handles user registration, authentication, and user data management
"""

import bcrypt
from datetime import datetime
from database.connection import execute_query, Database
import logging

logger = logging.getLogger(__name__)


class User:
    """
    User model for authentication and user management
    """
    
    def __init__(self, user_id=None, username=None, email_address=None, 
                 password_hash=None, created_at=None):
        self.user_id = user_id
        self.username = username
        self.email_address = email_address
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def hash_password(password):
        """
        Hash a password using bcrypt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify a password against its hash
        
        Args:
            password (str): Plain text password
            password_hash (str): Hashed password from database
            
        Returns:
            bool: True if password matches
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @classmethod
    def create(cls, username, password, email_address):
        """
        Create a new user
        
        Args:
            username (str): Username
            password (str): Plain text password
            email_address (str): Email address
            
        Returns:
            User: Newly created user object or None if failed
        """
        try:
            # Check if username already exists
            if cls.get_by_username(username):
                logger.error(f"Username '{username}' already exists")
                return None
            
            # Hash password
            password_hash = cls.hash_password(password)
            
            # Insert into database
            query = """
                INSERT INTO User (username, password_hash, email_address)
                VALUES (%s, %s, %s)
            """
            user_id = execute_query(query, (username, password_hash, email_address))
            
            logger.info(f"✅ User '{username}' created successfully with ID: {user_id}")
            
            # Return new user object
            return cls.get_by_id(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            return None

    @classmethod
    def get_by_id(cls, user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            User: User object or None if not found
        """
        query = "SELECT * FROM User WHERE user_id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_username(cls, username):
        """
        Get user by username
        
        Args:
            username (str): Username
            
        Returns:
            User: User object or None if not found
        """
        query = "SELECT * FROM User WHERE username = %s"
        result = execute_query(query, (username,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_email(cls, email_address):
        """
        Get user by email
        
        Args:
            email_address (str): Email address
            
        Returns:
            User: User object or None if not found
        """
        query = "SELECT * FROM User WHERE email_address = %s"
        result = execute_query(query, (email_address,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate a user
        
        Args:
            username (str): Username
            password (str): Plain text password
            
        Returns:
            User: User object if authentication successful, None otherwise
        """
        user = cls.get_by_username(username)
        
        if user and cls.verify_password(password, user.password_hash):
            logger.info(f"✅ User '{username}' authenticated successfully")
            return user
        
        logger.warning(f"⚠️ Authentication failed for username: '{username}'")
        return None

    def update(self, **kwargs):
        """
        Update user information
        
        Args:
            **kwargs: Fields to update (username, email_address, password)
            
        Returns:
            bool: True if update successful
        """
        try:
            # Build dynamic update query
            fields = []
            values = []
            
            if 'username' in kwargs:
                fields.append("username = %s")
                values.append(kwargs['username'])
                
            if 'email_address' in kwargs:
                fields.append("email_address = %s")
                values.append(kwargs['email_address'])
                
            if 'password' in kwargs:
                fields.append("password_hash = %s")
                values.append(self.hash_password(kwargs['password']))
            
            if not fields:
                return False
            
            values.append(self.user_id)
            query = f"UPDATE User SET {', '.join(fields)} WHERE user_id = %s"
            
            execute_query(query, tuple(values))
            
            # Update object attributes
            for key, value in kwargs.items():
                if key == 'password':
                    self.password_hash = self.hash_password(value)
                else:
                    setattr(self, key, value)
            
            logger.info(f"✅ User {self.user_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False

    def delete(self):
        """
        Delete user (cascade will delete all related data)
        
        Returns:
            bool: True if deletion successful
        """
        try:
            query = "DELETE FROM User WHERE user_id = %s"
            execute_query(query, (self.user_id,))
            
            logger.info(f"✅ User {self.user_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting user: {e}")
            return False

    @classmethod
    def get_all(cls):
        """
        Get all users
        
        Returns:
            list: List of User objects
        """
        query = "SELECT * FROM User ORDER BY created_at DESC"
        results = execute_query(query, fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    def to_dict(self):
        """
        Convert user object to dictionary
        
        Returns:
            dict: User data (excluding password_hash)
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email_address': self.email_address,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"


# Test functions
def test_user_model():
    """
    Test the User model
    """
    print("\n" + "="*50)
    print("Testing User Model")
    print("="*50)
    
    # Test 1: Create user
    print("\n1. Creating new user...")
    user = User.create(
        username="testuser",
        password="SecurePass123!",
        email_address="test@example.com"
    )
    
    if user:
        print(f"✅ User created: {user}")
        print(f"   - ID: {user.user_id}")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email_address}")
    else:
        print("❌ User creation failed")
        return
    
    # Test 2: Get by username
    print("\n2. Getting user by username...")
    found_user = User.get_by_username("testuser")
    print(f"✅ Found user: {found_user}")
    
    # Test 3: Authenticate
    print("\n3. Testing authentication...")
    auth_user = User.authenticate("testuser", "SecurePass123!")
    if auth_user:
        print(f"✅ Authentication successful: {auth_user}")
    else:
        print("❌ Authentication failed")
    
    # Test 4: Failed authentication
    print("\n4. Testing wrong password...")
    auth_fail = User.authenticate("testuser", "WrongPassword")
    if not auth_fail:
        print("✅ Correctly rejected wrong password")
    
    # Test 5: Update user
    print("\n5. Updating user email...")
    if user.update(email_address="newemail@example.com"):
        print(f"✅ Email updated to: {user.email_address}")
    
    # Test 6: Get all users
    print("\n6. Getting all users...")
    all_users = User.get_all()
    print(f"✅ Total users in database: {len(all_users)}")
    for u in all_users:
        print(f"   - {u}")
    
    # Test 7: Delete user
    print("\n7. Deleting test user...")
    if user.delete():
        print("✅ User deleted successfully")
    
    print("\n" + "="*50)
    print("User Model Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_user_model()