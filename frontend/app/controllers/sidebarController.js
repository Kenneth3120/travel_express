angular.module('towerAdminApp')
.controller('MainController', function($scope, $http) {
    $scope.isActive = function(viewPath){
        return $location.path() === viewPath;
    };
});