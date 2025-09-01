angular.module('towerAdminApp')
.controller('StatisticsController', function($scope, $timeout) {

    console.log("StatisticsController Loaded");

    // Statistics data
    $scope.stats = [
        { name: 'Job Templates', count: 42 },
        { name: 'Credentials', count: 23 },
        { name: 'Environments', count: 9 }
    ];

    // Delay to ensure the DOM element is rendered before Chart.js runs
    $timeout(function() {
        const ctx = document.getElementById('statsChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: $scope.stats.map(s => s.name),
                    datasets: [{
                        label: 'Item Counts',
                        data: $scope.stats.map(s => s.count),
                        backgroundColor: ['#4e79a7', '#f28e2c', '#e15759']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
    }, 100);

});
