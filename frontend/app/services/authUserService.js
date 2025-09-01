angular.module('towerAdminApp')

.factory('authUserService', function($http, $window, $rootScope) {
    const TOKEN_KEY = 'jwt_token';
    let isAuthenticatedFlag = false;

    function setToken(token) {
        if (token) {
            $window.localStorage.setItem(TOKEN_KEY, token);
            isAuthenticatedFlag = true;
        } else {
            $window.localStorage.removeItem(TOKEN_KEY);
            isAuthenticatedFlag = false;
        }
    }

    function getToken() {
        return $window.localStorage.getItem(TOKEN_KEY);
    }

    function getAuthHeader() {
        const token = getToken();
        return token ? { 'Authorization': 'Bearer ' + token } : {};
    }

    return {
        login: function(username, password) {
            return $http.post('http://127.0.0.1:8000/api/token/', { username: username, password: password })
                .then(function(response) {
                    setToken(response.data.access);
                    $rootScope.$broadcast('auth-login');
                    return response.data;
                });
        },

        logout: function() {
            setToken(null);
            $rootScope.$broadcast('auth-logout');
        },

        isAuthenticated: function() {
            return !!getToken();
        },

        getUserInfo: function() {
            if (!this.isAuthenticated()) {
                return Promise.reject('Not authenticated');
            }
            return $http.get('http://127.0.0.1:8000/api/user-info/', { headers: getAuthHeader() })
                .then(function(response) {
                    return response.data;
                });
        },

        getAuthHeader: getAuthHeader
    };
})

.factory('UserService', function($http) {
    const base = 'http://127.0.0.1:8000/api/users/';
    return {
        list: function() {
            return $http.get(base).then(function(r) { return r.data; });
        },
        create: function(user) {
            return $http.post(base, user).then(function(r) { return r.data; });
        },
        update: function(user) {
            return $http.put(base + user.id + '/', user).then(function(r) { return r.data; });
        },
        delete: function(userId) {
            return $http.delete(base + userId + '/').then(function(r) { return r.data; });
        }
    };
});
