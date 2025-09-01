angular.module('towerAdminApp')
.run(function($rootScope) {

    // Load dark mode setting from localStorage
    $rootScope.isDarkMode = localStorage.getItem('darkMode') === 'true';

    // Apply theme on initial load
    if ($rootScope.isDarkMode) {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.remove("dark-mode");
    }

    // Toggle theme function
    $rootScope.toggleTheme = function() {
        $rootScope.isDarkMode = !$rootScope.isDarkMode;

        if ($rootScope.isDarkMode) {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }

        // Save preference
        localStorage.setItem('darkMode', $rootScope.isDarkMode);
    };
});
