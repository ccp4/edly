angular.module('app')
 .config(['$routeProvider', '$compileProvider', function ($routeProvider, $compileProvider) {
  $routeProvider
    .when('/felix', {
      controller: 'felix_ctrl',
      templateUrl: '/static/views/felix.html'
    })
    .when('/bloch', {
      controller: 'bloch_ctrl',
      templateUrl: '/static/views/felix.html'
    })
    .otherwise('/bloch');
    // $compileProvider.debugInfoEnabled(false);
}]);
