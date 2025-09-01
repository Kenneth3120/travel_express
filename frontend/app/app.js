// app.js - Cleaned up version with external templates

angular.module('towerAdminApp', ['ngRoute', 'ngResource'])

.config(function($routeProvider) {
  $routeProvider
    .when('/dashboard', {
      templateUrl: './app/templates/dashboard.html',
      controller: 'DashboardController'
    })
    .when('/instances', {
      templateUrl: './app/templates/instances.html',
      controller: 'InstanceController'
    })
    .when('/credential-types', {
      templateUrl: './app/templates/credential-types.html',
      controller: 'CredentialController'
    })
    .when('/environments', {
      templateUrl: './app/templates/environments.html',
      controller: 'EnvironmentController'
    })
    .when('/statistics', {
      templateUrl: './app/templates/statistics.html',
      controller: 'StatisticsController'
    })
    .when('/audit-logs', {
      templateUrl: './app/templates/audit-logs.html',
      controller: 'AuditlogController'
    })
    .when('/users', {
      templateUrl: './app/templates/users.html',
      controller: 'UserMgmtController'
    })
    .when('/config', {
      templateUrl: './app/templates/config.html',
      controller: 'ConfigController'
    })
    .when('/login', {
      templateUrl: './app/partials/login.html',
      controller: 'LoginController'
    })
    .otherwise({
      redirectTo: '/dashboard'
    });
})

.run(function($rootScope, $location, authUserService) {
    // Route change authentication check
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
        if (!authUserService.isAuthenticated() && next.templateUrl !== './app/partials/login.html') {
            $location.path('/login');
        }
    });

    // Initialize authentication state
    $rootScope.isAuthenticated = authUserService.isAuthenticated();
    
    // Get user info if authenticated
    authUserService.getUserInfo().then(function(user) {
        $rootScope.currentUser = user;
    }).catch(function() {
        $rootScope.currentUser = null;
    });

    // Authentication event handlers
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

    // Global logout function
    $rootScope.logout = function() {
        authUserService.logout();
    };
});