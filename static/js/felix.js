(function () {
  'use strict';

angular.module('app')
  .controller('felix_ctrl', ['$scope','$rootScope','$log','$http', '$interval','$timeout', function ($scope,$rootScope,$log,$http,$interval,$timeout) {

    //////////////////////////////////////////////////////////////////////////////
    //// felix Stuffs
    //////////////////////////////////////////////////////////////////////////////
    $scope.get_felix_rock = function () {
      $http.post('show_felix_rock',JSON.stringify({'refl':$scope.refl}))
        .then(function(response){
          $scope.fig2 = response.data;
          // $log.log()
      });
    }

}]);


}());
