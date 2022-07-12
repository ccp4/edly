// (function () {
//   'use strict';

app.factory('felix_shared', function(){
  return { refls:{e:'',s:''},n_refls:{e:0,s:0},
    lock_refl:true, single:false};
});

angular.module('app')
  .controller('FelixCtrl', ['$scope','$rootScope','$log','$http', '$interval','$timeout','felix_shared', function ($scope,$rootScope,$log,$http,$interval,$timeout,felix_shared) {
    var self=$scope;

    self.gen_felix = function () {
      $http.post('gen_felix',JSON.stringify(self.felix))
        .then(function(response){
          // self.fig2 = response.data;
          $log.log(self.structure)
      });
    }

    self.update = function(val){
      if ($scope.info.lock_refl){
        if (val=='lacbed'){
          $scope.info.refls['e']=$scope.info.refls['s']
        }
        if (val=='rock'){
          $scope.info.refls['s']=$scope.info.refls['e']
        }
        $log.log($scope.info.refls)
        self.update_rock()
        self.update_lacbed()
      }
      else{
        if (val=='rock'){self.update_rock()}
        if (val=='lacbed'){self.update_lacbed()}
      }
    }

    self.update_rock = function () {
      // self.update_refl('e');
      $http.post('show_felix_rock',JSON.stringify({'refl':$scope.info.refls['e']}))
        .then(function(response){
          self.fig1 = response.data;
          // $log.log()
      });
    }

    self.update_lacbed = function () {
      $http.post('show_lacbed',JSON.stringify({'refl':$scope.info.refls['s']}))
        .then(function(response){
          self.fig2 = JSON.parse(response.data.fig);
        })
    }

    ////////////////////////////////////////////////////////////////////////////////////////
    //// INIT
    ////////////////////////////////////////////////////////////////////////////////////////
    self.fig1={};
    self.fig2={};
    $scope.info = felix_shared
    $scope.info.single = false
    $scope.init_felix=function(){
      $http.post('init_felix')
        .then(function(response){
          self.felix    = response.data.felix;
          self.exp_refls = response.data.exp_refls;
          self.sim_refls = response.data.sim_refls;
          // $scope.refls = response.data.refls;
          $scope.info.refls['e'] = response.data.refls['e']
          $scope.info.refls['s'] = response.data.refls['s']
          $scope.info.n_refls['e'] = self.exp_refls.length;
          $scope.info.n_refls['s'] = self.sim_refls.length;
          self.update('rock');
        })
    }
    $scope.init_felix();

}]);


angular.module('app')
  .controller('FelixPanelCtrl', ['$scope','$rootScope','$log','$http', '$interval','$timeout','felix_shared', function ($scope,$rootScope,$log,$http,$interval,$timeout,felix_shared) {

    $scope.expand={};
    $scope.popup={};
    $scope.info=felix_shared;
    $scope.init=function(){
      $http.post('init_felix_panel')
        .then(function(response){
          $scope.felix = response.data.felix;
        })
    }

    $scope.init();
}]);

// }());//function strict
