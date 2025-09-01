angular.module('towerAdminApp')
.controller('UserMgmtController', function($scope, UserService, $rootScope) {

    // Current logged-in user
    $scope.currentUser = $rootScope.currentUser;

    // List of users
    $scope.users = [];

    // New user form model
    $scope.newUser = { username: "", email: "", role: "viewer" };

    // Show/hide add form
    $scope.showAddForm = false;

    // Load all users
    function load() {
        UserService.list().then(function(data) {
            $scope.users = data;
        });
    }

    // Initial load
    load();

    // Add a new user
    $scope.addUser = function() {
        UserService.create($scope.newUser).then(function() {
            load();
            $scope.showAddForm = false;
            $scope.newUser = { username: "", email: "", role: "viewer" }; // Reset form
        });
    };

    // Update an existing user
    $scope.updateUser = function(user) {
        UserService.update(user).then(function() {
            load();
        });
    };

    // Delete a user
    $scope.deleteUser = function(id) {
        if (confirm('Delete user?')) {
            UserService.delete(id).then(function() {
                load();
            });
        }
    };
});
