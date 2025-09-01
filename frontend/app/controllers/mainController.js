angular.module('towerAdminApp')
.controller('MainController', function($scope, $http, $location, authUserService, $rootScope) {
    $scope.message = "Frontend is working";

    $scope.isActive = function(viewLocation){ 
        return viewLocation === $location.path();
    };

    // Initialize authentication status
    $rootScope.isAuthenticated = authUserService.isAuthenticated();
    authUserService.getUserInfo().then(function(user) {
        $rootScope.currentUser = user;
    }).catch(function() {
        $rootScope.currentUser = null; // No user logged in
    });

    // Listen for login/logout events from authUserService
    $rootScope.$on('auth-login', function() {
        $rootScope.isAuthenticated = true;
        authUserService.getUserInfo().then(function(user) {
            $rootScope.currentUser = user;
        });
    });

    $rootScope.$on('auth-logout', function() {
        $rootScope.isAuthenticated = false;
        $rootScope.currentUser = null;
        $location.path('/login');
    });

    $scope.logout = function() {
        authUserService.logout();
    };

});