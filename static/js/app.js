var app = angular.module('app', ['ngTouch','ngAria']);
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


// Plotly directive
app.directive('linePlot', function () {
  function linkFunc(scope, element, attrs) {
      scope.$watch(attrs.fig, function (new_fig,fig) {
      // scope.$watch('var_data', function (new_fig,fig) {
          // console.log(fig.layout);
          // console.log(new_fig.layout);
          // new_fig.layout.width =attrs.width;
          // new_fig.layout.height=attrs.height;
          Plotly.newPlot(element[0], new_fig.data, new_fig.layout);
      }, true);
  }
  return {
      link: linkFunc
  };
});



app.controller('viewer', ['$scope','$rootScope','$log','$http', '$interval', function ($scope,$rootScope,$log,$http,$interval) {

  // uploads
  $scope.set_structure=function(){
    $http.post('/set_structure',JSON.stringify({'cif':$scope.cif}))
    .then(function(response){
      $scope.cif_file=response.data;
      // $log.log(response.data);
    });
  }

  $scope.upload=function(val){
    $log.log(val);
  }
  $scope.toggle_molecule=function(){
    $scope.show_molecule=!$scope.show_molecule
    $http.get('/toggle_molecule')
    .then(function(response){
      // $log.log(response.data);
    });
  }


  //mode selection
  $scope.toggle_analysis_mode=function(){
    $scope.analysis_mode=!$scope.analysis_mode
    $scope.update()
  }

  $scope.inc_frame=function(){
    $scope.frame=Math.min($scope.max_frame,$scope.frame+1);
    $scope.update();
  };
  $scope.dec_frame=function(){
    $scope.frame=Math.max(1,$scope.frame-1);
    $scope.update();
  };
  $scope.update_frame=function(event){
    if (event.key=='Enter'){
      if ($scope.frame>$scope.max_frame){
        $scope.frame=$scope.max_frame;
      }
      if($scope.frame<1){
        $scope.frame=1;
      }
      $scope.update();
    }
  }
  $scope.update_zmax=function(event,val){
    if (event.key=='Enter'){
      if ($scope.zmax[val]>0){
        $http.post('/update_zmax',JSON.stringify({'zmax':$scope.zmax[val],'key':val}))
          .then(function(response){
            $scope.img[val] = response.data;
        });
      }
    }
  }

  $scope.update=function(){
    if ($scope.analysis_mode){
      $scope.update_bloch();
    }
    else{
      $scope.update_img();
    }
  }

  $scope.update_img=function(){
    $http.post('/get_frame',JSON.stringify({'frame':$scope.frame,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.img = response.data;
    });
  };

  $scope.update_bloch=function(){
    $http.post('/solve_bloch',JSON.stringify({'frame':$scope.frame}))
      .then(function(response){
        $scope.fig = response.data;
    });
  };

  $scope.toggle_popup=function(key){
    $scope.popup[key]=!$scope.popup[key];
  }

  $scope.analyis_mode=false;
  $scope.fig={};

  // $scope.var_data={'width':250,'height':800};
  $http.get('/init')
    .then(function(response){
      $scope.structure = response.data.mol;
      $scope.frame     = response.data.frame;
      $scope.analysis_mode = response.data.analysis_mode;
      $scope.show_molecule = response.data.show_molecule;
      $scope.max_frame = response.data.max_frame;
      $scope.zmax      = response.data.zmax;
      $scope.bloch     = response.data.bloch;
      $scope.cif       = response.data.cif;
      $scope.cif_file  = response.data.cif_file;
      $scope.update()
    });
    // $log.log($scope.structure);

    $scope.popup={'pets':false,'mol':false,'exp':false,'sim':false,'ana':false};
    $scope.show_buttons=false;
}]);
