angular.module('towerAdminApp')
.controller('InstanceController', function($scope, $http) {

    // Data models
    $scope.instances = [];
    $scope.newInstance = {};
    $scope.filters = {
        region: '',
        environment: ''
    };
    $scope.uniqueRegions = [];
    $scope.uniqueEnvironments = [];
    $scope.showAddInstanceModal = false; // Controls modal visibility
    $scope.connectionTestStatus = '';
    $scope.connectionTestError = '';
    $scope.connectionSuccessful = false;

    // Load instances from API
    $scope.loadInstances = function() {
        $http.get('http://127.0.0.1:8000/api/instances/')
            .then(function(response) {
                $scope.instances = response.data;
                $scope.extractFilterValues();
            })
            .catch(function(error) {
                console.error('Failed to load instances:', error);
            });
    };

    // Extract unique values for dropdown filters
    $scope.extractFilterValues = function() {
        $scope.uniqueRegions = [...new Set($scope.instances.map(i => i.region))];
        $scope.uniqueEnvironments = [...new Set($scope.instances.map(i => i.environment))];
    };

    // Filter function for ng-repeat
    $scope.filterByRegionAndEnvironment = function(instance) {
        const matchRegion = !$scope.filters.region || instance.region === $scope.filters.region;
        const matchEnv = !$scope.filters.environment || instance.environment === $scope.filters.environment;
        return matchRegion && matchEnv;
    };

    // Add a new instance
    $scope.addInstance = function() {
        $http.post('http://127.0.0.1:8000/api/instances/', $scope.newInstance)
            .then(function(response) {
                $scope.instances.push(response.data);
                $scope.newInstance = {}; // reset form
                $scope.extractFilterValues();
            })
            .catch(function(error) {
                console.error('Failed to add instance:', error);
            });
    };

    // Delete an instance
    $scope.deleteInstance = function(id) {
        $http.delete(`http://127.0.0.1:8000/api/instances/${id}/`)
            .then(function() {
                $scope.instances = $scope.instances.filter(i => i.id !== id);
                $scope.extractFilterValues();
            })
            .catch(function(error) {
                console.error('Failed to delete instance:', error);
            });
    };

    // Initialize
    $scope.loadInstances();

});
