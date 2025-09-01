angular.module('towerAdminApp')
.controller('DashboardController', function($scope, $http, $timeout, $q) {

    // Loader Flags
    $scope.loadingCounts = true;
    $scope.loadingLogs = true;

    // Initial values
    $scope.instanceCount = 0;
    $scope.credentialCount = 0;
    $scope.environmentCount = 0;
    $scope.recentChanges = [];
    $scope.toasts = [];

    // Toast Notification
    $scope.showToast = function(type, message) {
        const id = Date.now();
        $scope.toasts.push({ id, type, message });
        $timeout(() => {
            $scope.toasts = $scope.toasts.filter(t => t.id !== id);
        }, 4000);
    };

    $scope.closeToast = function(id) {
        $scope.toasts = $scope.toasts.filter(t => t.id !== id);
    };

    // Previous counts to detect changes
    let previousInstanceCount = 0;
    let previousCredentialCount = 0;
    let previousEnvironmentCount = 0;

    // Fetch counts
    const fetchCounts = [
        $http.get('http://127.0.0.1:8000/api/tower/')
            .then(function(res) {
                $scope.instanceCount = res.data.length || 0;
                if ($scope.instanceCount > previousInstanceCount) {
                    $scope.showToast("info", "New instances added");
                }
                previousInstanceCount = $scope.instanceCount;
            }),

        $http.get('http://127.0.0.1:8000/api/credentials/')
            .then(function(res) {
                $scope.credentialCount = res.data.length || 0;
                if ($scope.credentialCount > previousCredentialCount) {
                    $scope.showToast("success", "New credential created");
                }
                previousCredentialCount = $scope.credentialCount;
            }),

        $http.get('http://127.0.0.1:8000/api/environments/')
            .then(function(res) {
                $scope.environmentCount = res.data.length || 0;
                if ($scope.environmentCount > previousEnvironmentCount) {
                    $scope.showToast("info", "Environment updated recently");
                }
                previousEnvironmentCount = $scope.environmentCount;
            })
    ];

    $q.all(fetchCounts).then(function() {
        $scope.loadingCounts = false;

        $timeout(function() {
            const instanceChartEl = document.getElementById('instanceChart');
            if (instanceChartEl) {
                new Chart(instanceChartEl, {
                    type: 'bar',
                    data: {
                        labels: ['Instances', 'Credentials', 'Environments'],
                        datasets: [{
                            label: 'Entity Count',
                            data: [$scope.instanceCount, $scope.credentialCount, $scope.environmentCount],
                            backgroundColor: ['#4e79a7', '#f28e2c', '#e15759']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }

            const jobChartEl = document.getElementById('jobChart');
            if (jobChartEl) {
                new Chart(jobChartEl, {
                    type: 'doughnut',
                    data: {
                        labels: ['Success', 'Failure'],
                        datasets: [{
                            label: 'Jobs',
                            data: [40, 60],
                            backgroundColor: ['#59a14f', '#e15759']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }

            // Toast for failed jobs
            const failedJobs = 20;
            if (failedJobs > 0) {
                $scope.showToast("error", `${failedJobs} jobs failed recently.`);
            }

        }, 300);
    });

    // Fetch recent audit logs
    $http.get('http://127.0.0.1:8000/api/audit-logs/?limit=5')
        .then(function(res) {
            $scope.recentChanges = res.data.results || res.data || [];
            $scope.loadingLogs = false;
            if ($scope.recentChanges.length > 0) {
                $scope.showToast("info", "New activity detected in audit logs");
            }
        })
        .catch(function(err) {
            console.error('Error fetching audit logs:', err);
            $scope.loadingLogs = false;
        });

});
