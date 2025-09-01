angular.module('towerAdminApp').controller('LoginController', function ($scope, $http, $location, authUserService) {
    $scope.credentials = {
        username: '',
        password: ''
    };

    $scope.loginError = '';

    $scope.login = function () {
        authUserService.login($scope.credentials.username, $scope.credentials.password)
            .then(function (response) {
                // On successful login, redirect to dashboard or intended page
                $location.path('/dashboard'); 
            })
            .catch(function (error) {
                $scope.loginError = 'Invalid username or password.';
                console.error('Login failed:', error);
            });
    };
});
