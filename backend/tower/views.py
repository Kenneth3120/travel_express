import requests
import urllib3
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model

from .models import TowerConfig, TowerInstance, Credential, ExecutionEnvironment, Auditlog
from .serializers import (
    TowerInstanceSerializer,
    CredentialSerializer,
    ExecutionEnvironmentSerializer,
    AuditlogSerializer,
    UserSerializer
)
from .utils import log_action, get_tower_credential_types, create_tower_credential_type, get_tower_credential_type_by_name
from .permissions import IsAdmin, ReadOnlyForViewer

User = get_user_model()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ========================
# Base ViewSet with Audit Logging
# ========================
class AuditedModelViewSet(viewsets.ModelViewSet):
    """Base ViewSet that automatically handles audit logging for CRUD operations."""
    
    def get_current_user(self):
        """Get current user or default to 'system' if not available."""
        return getattr(self.request.user, 'username', 'system')
    
    def track_changes(self, old_instance, new_instance, serializer):
        """Track changes between old and new instance."""
        changes = {}
        for field in serializer.fields:
            old_val = getattr(old_instance, field, None)
            new_val = getattr(new_instance, field, None)
            if old_val != new_val:
                changes[field] = {'from': old_val, 'to': new_val}
        return changes

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(user=self.get_current_user(), action='created', obj=instance)

    def perform_update(self, serializer):
        old_instance = serializer.instance.__class__.objects.get(pk=serializer.instance.pk)
        new_instance = serializer.save()
        changes = self.track_changes(old_instance, new_instance, serializer)
        log_action(user=self.get_current_user(), action='updated', obj=new_instance, changes=changes)

    def perform_destroy(self, instance):
        log_action(user=self.get_current_user(), action='deleted', obj=instance)
        instance.delete()


# ========================
# User Management
# ========================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """Returns current user info for Angular frontend."""
    if not request.user.is_authenticated:
        return Response({'detail': 'Not authenticated'}, status=401)

    return Response({
        'username': request.user.username,
        'role': request.user.role
    })


# ========================
# Connection Testing
# ========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_connection(request):
    """Tests connection to an AAP instance with provided credentials."""
    url = request.data.get('url')
    username = request.data.get('username')
    password = request.data.get('password')

    if not all([url, username, password]):
        return Response(
            {'message': 'URL, username, and password are required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    test_url = url.rstrip('/') + '/api/v2/ping/'

    try:
        response = requests.get(test_url, auth=(username, password), timeout=5, verify=False)
        response.raise_for_status()
        return Response({'message': 'Connection successful!'}, status=status.HTTP_200_OK)
    
    except requests.exceptions.Timeout:
        return Response({'message': 'Connection timed out.'}, status=status.HTTP_408_REQUEST_TIMEOUT)
    
    except requests.exceptions.ConnectionError:
        return Response(
            {'message': 'Could not connect to the AAP instance. Check the URL.'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            return Response(
                {'message': 'Authentication failed: Invalid credentials.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {'message': f'HTTP Error: {e.response.status_code} - {e.response.reason}'}, 
            status=e.response.status_code
        )
    
    except Exception as e:
        return Response(
            {'message': f'An unexpected error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========================
# Tower Credential Proxy
# ========================
class TowerCredentialProxy(viewsets.ViewSet):
    """Proxies credential list calls to Ansible Tower using DB-stored credentials."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cfg = TowerConfig.objects.first()
        if not cfg:
            return Response(
                {"detail": "TowerConfig not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        tower_url = cfg.base_url.rstrip('/') + '/api/v2/credentials/'
        try:
            resp = requests.get(
                tower_url,
                auth=(cfg.username, cfg.password),
                timeout=10,
                verify=False
            )
            resp.raise_for_status()
            return Response(resp.json().get('results', []))
        
        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": f"Error contacting Tower: {e}"},
                status=status.HTTP_502_BAD_GATEWAY
            )


# ========================
# Main ViewSets (using base class)
# ========================
class TowerInstanceViewSet(AuditedModelViewSet):
    queryset = TowerInstance.objects.all()
    serializer_class = TowerInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]


class CredentialViewSet(AuditedModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExecutionEnvironmentViewSet(AuditedModelViewSet):
    queryset = ExecutionEnvironment.objects.all()
    serializer_class = ExecutionEnvironmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditlog.objects.all().order_by('-timestamp')
    serializer_class = AuditlogSerializer
    permission_classes = [permissions.IsAuthenticated]


# ========================
# Credential Type Management
# ========================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def credential_type_status(request):
    """Returns all unique CredentialTypes found across Tower instances with their presence status."""
    instances = TowerInstance.objects.all()
    all_tower_types = {}
    
    # Collect all credential types across instances
    for instance in instances:
        try:
            tower_credential_types = get_tower_credential_types(instance)
            for c_type in tower_credential_types:
                name = c_type.get('name')
                description = c_type.get('description', '')
                if name and name not in all_tower_types:
                    all_tower_types[name] = {'name': name, 'description': description}
        except Exception as e:
            print(f"Error fetching credential types from {instance.name}: {e}")

    # Calculate status for each credential type
    results = []
    for name, data in all_tower_types.items():
        type_status = {
            'name': data['name'],
            'description': data['description'],
            'present_in_instances': [],
            'missing_in_instances': [],
            'status': 'N/A'
        }
        
        present_count = 0
        total_instances = len(instances)
        
        for instance in instances:
            try:
                tower_credential_types = get_tower_credential_types(instance)
                if name in [t.get('name') for t in tower_credential_types]:
                    type_status['present_in_instances'].append(instance.name)
                    present_count += 1
                else:
                    type_status['missing_in_instances'].append(instance.name)
            except Exception as e:
                type_status['missing_in_instances'].append(f"{instance.name} (Error: {e})")
                
        # Calculate status based on presence percentage
        if total_instances > 0:
            percentage_present = (present_count / total_instances) * 100
            if percentage_present == 100:
                type_status['status'] = 'Green'
            elif percentage_present > 50:
                type_status['status'] = 'Orange'
            else:
                type_status['status'] = 'Red'
            
        results.append(type_status)

    return Response(results, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_missing_credential_type(request):
    """Duplicates a credential type to instances where it is missing."""
    credential_type_name = request.data.get('name')
    credential_type_description = request.data.get('description', '')
    missing_in_instances = request.data.get('missing_in_instances', [])

    if not credential_type_name or not missing_in_instances:
        return Response(
            {'message': 'Credential type name and missing instances are required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    results = []
    for instance_name in missing_in_instances:
        try:
            instance = TowerInstance.objects.get(name=instance_name)
            tower_credential_types = get_tower_credential_types(instance)
            
            if credential_type_name not in [t.get('name') for t in tower_credential_types]:
                credential_type_data = {
                    'name': credential_type_name,
                    'description': credential_type_description,
                }
                create_tower_credential_type(instance, credential_type_data)
                results.append({'instance': instance.name, 'status': 'duplicated'})
            else:
                results.append({'instance': instance.name, 'status': 'already_exists'})
                
        except TowerInstance.DoesNotExist:
            results.append({'instance': instance_name, 'status': 'instance_not_found'})
        except Exception as e:
            results.append({'instance': instance_name, 'status': 'error', 'message': str(e)})
            
    return Response(results, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_credential_type_by_name(request):
    """Verifies if a credential type exists under an alternative name in missing instances."""
    original_credential_type_name = request.data.get('original_name')
    alternative_name = request.data.get('alternative_name')
    missing_in_instances = request.data.get('missing_in_instances', [])

    if not all([original_credential_type_name, alternative_name, missing_in_instances]):
        return Response(
            {'message': 'Original credential type name, alternative name, and missing instances are required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    results = []
    for instance_name in missing_in_instances:
        try:
            instance = TowerInstance.objects.get(name=instance_name)
            found_type = get_tower_credential_type_by_name(instance, alternative_name)
            
            if found_type:
                results.append({
                    'instance': instance.name, 
                    'status': 'found', 
                    'found_name': found_type.get('name')
                })
            else:
                results.append({'instance': instance.name, 'status': 'not_found'})
                
        except TowerInstance.DoesNotExist:
            results.append({'instance': instance_name, 'status': 'instance_not_found'})
        except Exception as e:
            results.append({'instance': instance_name, 'status': 'error', 'message': str(e)})
            
    return Response(results, status=status.HTTP_200_OK)