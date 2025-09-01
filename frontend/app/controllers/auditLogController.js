angular.module('toweradminApp').controller('AuditlogController', function($scope, $http) {

    $scope.auditlogs = [];

    // Fetch from backend API
    $http.get("http://127.0.0.1:8000/api/audit-logs/")
        .then(function(response) {
            $scope.auditlogs = response.data;
        })
        .catch(function(error) {
            console.error('Error fetching audit logs:', error);
        });

    // Search filters
    $scope.searchUser = "";
    $scope.searchType = "";

    $scope.auditFilter = function(log) {
        const userMatch = !$scope.searchUser || 
            log.user.toLowerCase().includes($scope.searchUser.toLowerCase());

        const typeMatch = !$scope.searchType || 
            log.object_type.toLowerCase().includes($scope.searchType.toLowerCase());

        return userMatch && typeMatch;
    };

});
