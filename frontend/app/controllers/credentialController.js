angular.module('towerAdminApp')
.controller('CredentialController', function($scope, $http) {

    // Data models for Credential Types
    $scope.credentialTypes = [];
    $scope.showVerifyModal = false;
    $scope.selectedCredentialType = null; // Will store the full type object
    $scope.alternativeCredentialTypeName = '';
    $scope.verifyStatus = '';
    $scope.verifyError = '';

    // Load Credential Types and their status
    $scope.loadCredentialTypes = function() {
        $http.get('http://127.0.0.1:8000/api/credential-type-status/')
        .then(function(response) {
            $scope.credentialTypes = response.data;
        })
        .catch(function(err) {
            console.error('Error fetching credential types:', err);
            alert("Error fetching credential types.");
        });
    };

    // Modal functions for Verify Credential Type
    $scope.openVerifyModal = function(credentialType) {
        $scope.showVerifyModal = true;
        $scope.selectedCredentialType = credentialType; // Store the entire object
        $scope.alternativeCredentialTypeName = '';
        $scope.verifyStatus = '';
        $scope.verifyError = '';
    };

    $scope.closeVerifyModal = function() {
        $scope.showVerifyModal = false;
        $scope.selectedCredentialType = null;
        $scope.alternativeCredentialTypeName = '';
    };

    // Duplicate Missing Credential Type
    $scope.duplicateMissing = function(credentialType) {
        if (!confirm(`Are you sure you want to duplicate '${credentialType.name}' to missing instances?`)) {
            return;
        }

        $http.post('http://127.0.0.1:8000/api/duplicate-credential-type/', {
            name: credentialType.name,
            description: credentialType.description,
            missing_in_instances: credentialType.missing_in_instances
        })
        .then(function(response) {
            alert('Duplication process initiated. Check console for details.');
            console.log('Duplication results:', response.data);
            $scope.loadCredentialTypes(); // Refresh data after action
        })
        .catch(function(err) {
            console.error('Error duplicating credential type:', err);
            alert("Error duplicating credential type.");
        });
    };

    // Verify Credential Type
    $scope.verifyCredentialType = function() {
        if (!$scope.alternativeCredentialTypeName) {
            $scope.verifyError = 'Alternative name is required for verification.';
            return;
        }
        $scope.verifyStatus = 'Verifying...';
        $scope.verifyError = '';

        $http.post('http://127.0.0.1:8000/api/verify-credential-type/', {
            original_name: $scope.selectedCredentialType.name,
            alternative_name: $scope.alternativeCredentialTypeName,
            missing_in_instances: $scope.selectedCredentialType.missing_in_instances
        })
        .then(function(response) {
            console.log('Verification results:', response.data);
            let foundCount = response.data.filter(res => res.status === 'found').length;
            if (foundCount > 0) {
                $scope.verifyStatus = `Found in ${foundCount} instance(s).`;
                alert(`Verification successful! Found in ${foundCount} instance(s). Check console for details.`);
            } else {
                $scope.verifyStatus = 'Not found in any missing instances.';
                alert('Verification complete: Not found in any missing instances.');
            }
            $scope.closeVerifyModal();
            $scope.loadCredentialTypes(); // Refresh data after action
        })
        .catch(function(err) {
            console.error('Error verifying credential type:', err);
            $scope.verifyError = err.data?.message || 'An error occurred during verification.';
        });
    };

    // Initialize
    $scope.loadCredentialTypes();
});
