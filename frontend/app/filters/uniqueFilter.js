angular.module('towerAdminApp')
.filter('unique', function() {
    return function(items, key) {
        if (!angular.isArray(items)) return items; // Guard for non-array input
        
        const seen = new Set();
        
        return items.filter(function(item) {
            const val = item[key];
            if (seen.has(val)) return false;
            seen.add(val);
            return true;
        });
    };
});
