angular.module('towerAdminApp')
.factory('apiService', function($http, authUserService) {
    const BASE_URL = 'http://127.0.0.1:8000/api/';

    // Helper to add auth headers to requests
    function getConfig() {
        return { headers: authUserService.getAuthHeader() };
    }

    return {
        // Tower Instances
        getInstances: function() {
            return $http.get(BASE_URL + 'instances/', getConfig());
        },
        addInstance: function(instanceData) {
            return $http.post(BASE_URL + 'instances/', instanceData, getConfig());
        },
        updateInstance: function(id, instanceData) {
            return $http.put(BASE_URL + 'instances/' + id + '/', instanceData, getConfig());
        },
        deleteInstance: function(id) {
            return $http.delete(BASE_URL + 'instances/' + id + '/', getConfig());
        },

        // Credential Types
        getCredentialTypes: function() {
            return $http.get(BASE_URL + 'credential-type-status/', getConfig());
        },
        duplicateCredentialType: function(data) {
            return $http.post(BASE_URL + 'duplicate-credential-type/', data, getConfig());
        },
        verifyCredentialType: function(data) {
            return $http.post(BASE_URL + 'verify-credential-type/', data, getConfig());
        },

        // Environments
        getEnvironments: function() {
            return $http.get(BASE_URL + 'environments/', getConfig());
        },
        addEnvironment: function(envData) {
            return $http.post(BASE_URL + 'environments/', envData, getConfig());
        },
        deleteEnvironment: function(id) {
            return $http.delete(BASE_URL + 'environments/' + id + '/', getConfig());
        },

        // Statistics (assuming these are from the backend as well)
        getDashboardCounts: function() {
            return $http.get(BASE_URL + 'dashboard-counts/', getConfig()); // You might need to create this endpoint
        },
        getJobChartData: function() {
            return $http.get(BASE_URL + 'job-chart-data/', getConfig()); // You might need to create this endpoint
        },

        // Audit Logs
        getAuditLogs: function(limit) {
            const url = limit ? BASE_URL + 'audit-logs/?limit=' + limit : BASE_URL + 'audit-logs/';
            return $http.get(url, getConfig());
        },

        // User Management
        getUsers: function() {
            return $http.get(BASE_URL + 'users/', getConfig());
        },
        addUser: function(userData) {
            return $http.post(BASE_URL + 'users/', userData, getConfig());
        },
        updateUser: function(id, userData) {
            return $http.put(BASE_URL + 'users/' + id + '/', userData, getConfig());
        },
        deleteUser: function(id) {
            return $http.delete(BASE_URL + 'users/' + id + '/', getConfig());
        },

        // Config
        getConfig: function() {
            return $http.get(BASE_URL + 'config/', getConfig()); // You might need to create this endpoint
        },
        saveConfig: function(configData) {
            return $http.post(BASE_URL + 'config/', configData, getConfig()); // You might need to create this endpoint
        }
    };
});
