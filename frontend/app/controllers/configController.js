angular.module('towerAdminApp')
.controller('ConfigController', function($scope) {

    $scope.config = {
        username: '',
        password: '',
        ldap_enabled: false
    };

    $scope.saveConfig = function() {
        // Here you can send $scope.config to your backend API
        alert('Configuration saved:\n' + JSON.stringify($scope.config, null, 2));
    };

});
