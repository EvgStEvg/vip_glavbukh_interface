## security.py

from cryptography.fernet import Fernet
from typing import Dict

class Security:
    """A class to handle encryption and decryption of user credentials."""

    def __init__(self, key: bytes = None):
        """Initializes the Security class with a given key or generates a new one."""
        self._key = key or Fernet.generate_key()
        self._cipher = Fernet(self._key)

    def encrypt_credentials(self, credentials: Dict[str, str]) -> str:
        """
        Encrypts user credentials.

        Args:
            credentials (Dict[str, str]): A dictionary containing user credentials.

        Returns:
            str: A string representing the encrypted credentials.
        """
        # Convert the credentials dictionary to a string
        credentials_str = str(credentials)
        # Encrypt the credentials string
        encrypted_data = self._cipher.encrypt(credentials_str.encode('utf-8'))
        return encrypted_data.decode('utf-8')

    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, str]:
        """
        Decrypts encrypted user credentials.

        Args:
            encrypted_data (str): A string representing the encrypted credentials.

        Returns:
            Dict[str, str]: A dictionary containing the decrypted user credentials.
        """
        # Decrypt the encrypted data
        decrypted_data = self._cipher.decrypt(encrypted_data.encode('utf-8'))
        # Convert the decrypted data back to a dictionary
        credentials = eval(decrypted_data.decode('utf-8'))
        return credentials
