angular.module('towerAdminApp')
.controller('EnvironmentController', function($scope, $http) {

    // Filter models
    $scope.filterName = '';
    $scope.filterInstance = '';

    // Data models
    $scope.environments = [];
    $scope.towerInstances = [];
    $scope.newEnv = {};

    // Filter function
    $scope.envFilter = function(env) {
        const nameMatch = !$scope.filterName || env.name.toLowerCase().includes($scope.filterName.toLowerCase());
        const instMatch = !$scope.filterInstance || env.tower_instance === $scope.filterInstance;
        return nameMatch && instMatch;
    };

    // Load tower instances
    $scope.loadInstances = function() {
        $http.get('http://127.0.0.1:8000/api/instances/')
        .then(function(res) {
            $scope.towerInstances = res.data.results || res.data;
        })
        .catch(function(err) {
            console.error('Error loading tower instances:', err);
        });
    };

    // Load environments
    $scope.loadEnvironments = function() {
        $http.get('http://127.0.0.1:8000/api/environments/')
        .then(function(res) {
            $scope.environments = res.data.results || res.data;
        })
        .catch(function(err) {
            console.error('Error loading environments:', err);
        });
    };

    // Add a new environment
    $scope.addEnv = function() {
        $http.post('http://127.0.0.1:8000/api/environments/', $scope.newEnv)
        .then(function(res) {
            $scope.environments.push(res.data);
            $scope.newEnv = {};
            $scope.envForm.$setPristine();
            $scope.envForm.$setUntouched();
        })
        .catch(function(err) {
            console.error('Error adding environment:', err);
        });
    };

    // Delete an environment
    $scope.deleteEnv = function(id) {
        $http.delete(`http://127.0.0.1:8000/api/environments/${id}/`)
        .then(function() {
            $scope.environments = $scope.environments.filter(e => e.id !== id);
        })
        .catch(function(err) {
            console.error('Error deleting environment:', err);
        });
    };

    // Map instance ID to instance name
    $scope.getInstanceName = function(id) {
        const inst = $scope.towerInstances.find(i => i.id === id);
        return inst ? inst.name : "Unknown";
    };

    // Initialize
    $scope.loadInstances();
    $scope.loadEnvironments();
});
