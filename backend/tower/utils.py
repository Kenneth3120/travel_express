"""
Utility functions for the Tower app.
Provides audit logging and Tower API interaction helpers.
"""
import requests
from django.utils.timezone import now
from .models import Auditlog


def log_action(user, action, obj, changes=None):
    """
    Create an audit log entry for model changes.
    
    Args:
        user (str): Username who performed the action
        action (str): Action performed ('created', 'updated', 'deleted')
        obj: Model instance that was changed
        changes (dict): Dictionary of field changes (optional)
    """
    try:
        Auditlog.objects.create(
            user=user,
            action=action,
            object_type=obj.__class__.__name__,
            object_repr=str(obj),
            object_id=obj.pk,
            timestamp=now(),
            changes=changes or {}
        )
    except Exception as e:
        # Log the error but don't break the main operation
        print(f"Error creating audit log: {e}")


def get_tower_credential_types(tower_instance):
    """
    Fetch credential types from a Tower instance.
    
    Args:
        tower_instance: TowerInstance model object
        
    Returns:
        list: List of credential type dictionaries
        
    Raises:
        requests.RequestException: If API call fails
    """
    if not tower_instance.url or not tower_instance.username:
        raise ValueError("Tower instance missing required connection details")
    
    url = tower_instance.url.rstrip('/') + '/api/v2/credential_types/'
    
    try:
        response = requests.get(
            url,
            auth=(tower_instance.username, tower_instance.password),
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        return response.json().get('results', [])
    
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to fetch credential types from {tower_instance.name}: {e}")


def create_tower_credential_type(tower_instance, credential_type_data):
    """
    Create a credential type in a Tower instance.
    
    Args:
        tower_instance: TowerInstance model object
        credential_type_data (dict): Credential type data to create
        
    Returns:
        dict: Created credential type data
        
    Raises:
        requests.RequestException: If API call fails
    """
    if not tower_instance.url or not tower_instance.username:
        raise ValueError("Tower instance missing required connection details")
    
    url = tower_instance.url.rstrip('/') + '/api/v2/credential_types/'
    
    try:
        response = requests.post(
            url,
            auth=(tower_instance.username, tower_instance.password),
            json=credential_type_data,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to create credential type in {tower_instance.name}: {e}")


def get_tower_credential_type_by_name(tower_instance, name):
    """
    Find a credential type by name in a Tower instance.
    
    Args:
        tower_instance: TowerInstance model object
        name (str): Name of the credential type to find
        
    Returns:
        dict or None: Credential type data if found, None otherwise
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        credential_types = get_tower_credential_types(tower_instance)
        
        for cred_type in credential_types:
            if cred_type.get('name', '').lower() == name.lower():
                return cred_type
                
        return None
    
    except requests.RequestException:
        # Re-raise the exception from get_tower_credential_types
        raise


def test_tower_connection(url, username, password):
    """
    Test connection to a Tower instance.
    
    Args:
        url (str): Tower instance URL
        username (str): Username for authentication
        password (str): Password for authentication
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    test_url = url.rstrip('/') + '/api/v2/ping/'
    
    try:
        response = requests.get(
            test_url,
            auth=(username, password),
            timeout=5,
            verify=False
        )
        response.raise_for_status()
        return True
    
    except requests.exceptions.RequestException:
        return False
