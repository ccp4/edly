// (function () {
//   'use strict';

app.factory('Refls', function(){
  return { e:'' ,s:''};
});

angular.module('app')
  .controller('FelixCtrl', ['$scope','$rootScope','$log','$http', '$interval','$timeout','Refls', function ($scope,$rootScope,$log,$http,$interval,$timeout,Refls) {
    var self=$scope;

    self.gen_felix = function () {
      $http.post('gen_felix',JSON.stringify(self.felix))
        .then(function(response){
          // self.fig2 = response.data;
          $log.log(self.structure)
      });
    }

    self.update_rock = function () {
      // self.update_refl('e');
      $http.post('show_felix_rock',JSON.stringify({'refl':$scope.refls['e']}))
        .then(function(response){
          self.fig1 = response.data;
          // $log.log()
      });
    }

    self.update_lacbed = function () {
      // self.update_refl('s');
      $http.post('show_lacbed',JSON.stringify({'refl':$scope.refls['s']}))
        .then(function(response){
          self.fig2 = JSON.parse(response.data.fig);
          // self.refls['s'] = response.data.refl
        })
    }

    ////////////////////////////////////////////////////////////////////////////////////////
    //// MISC
    ////////////////////////////////////////////////////////////////////////////////////////
    // self.update_refl = function(val){
    //   var a = $('#select_'+val+'refl')[0]
    //   self.refls[val]=a[a.selectedIndex].label
    //   // $log.log(self.refl)
    // }

    // self.set_graph = function (val) {
    //   self.fig1_graph=val;
    //   switch(self.fig1_graph){
    //     case 'rock'   : self.refls=self.exp_refls;break;
    //     case 'lacbed' : self.refls=self.sim_refls;break;
    //   }
    //   self.update_graph()
    // }

    // self.update_graph = function () {
    //   self.update_refl();
    //   switch(self.fig1_graph){
    //     case 'rock':self.update_felix_rock();break;
    //     case 'lacbed':self.show_lacbed();break;
    //   }
    // }

    self.fig1={};
    self.fig2={};
    self.single = true
    $scope.refls = Refls
    $scope.init_felix=function(){
      $http.post('init_felix')
        .then(function(response){
          self.felix    = response.data.felix;
          self.exp_refls = response.data.exp_refls;
          self.sim_refls = response.data.sim_refls;
          // $scope.refls = response.data.refls;
          Refls['e']=response.data.refls['e']
          Refls['s']=response.data.refls['s']
          // self.fig1 = JSON.parse(response.data.fig1);
          // self.fig2 = JSON.parse(response.data.fig2);
          // self.set_graph('lacbed');
          self.update_rock();
          self.update_lacbed();
        })
    }
    $scope.init_felix();

}]);


angular.module('app')
  .controller('FelixPanelCtrl', ['$scope','$rootScope','$log','$http', '$interval','$timeout','Refls', function ($scope,$rootScope,$log,$http,$interval,$timeout,Refls) {

    $scope.expand={};
    $scope.popup={};
    $scope.refls=Refls;
    $scope.init=function(){
      $http.post('init_felix_panel')
        .then(function(response){
          $scope.felix = response.data.felix;
        })
    }

    $scope.init();
}]);

// }());//function strict
