var app = angular.module('app', ['ngTouch','ngAria']);
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


// Plotly directive
app.directive('linePlot', function () {
  function linkFunc(scope, element, attrs) {
      scope.$watch('var_data', function (new_fig,fig) {
          // console.log(fig.layout);
          // console.log(new_fig.layout);
          new_fig.layout.width =attrs.width;
          new_fig.layout.height=attrs.height;
          Plotly.newPlot(element[0], new_fig.data, new_fig.layout);
      }, true);
  }
  return {
      link: linkFunc
  };
});


app.controller('viewer', ['$scope','$rootScope','$log','$http', '$interval', function ($scope,$rootScope,$log,$http,$interval) {

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
      if ($scope.frame<$scope.max_frame && $scope.frame>=0){
        $scope.update();
      }
    }
  }
  $scope.update_zmax=function(event){
    if (event.key=='Enter'){
      if ($scope.zmax>0){
        $scope.update_img();
        // $http.get($scope.exp_frame);
        $scope.exp_frame='';
        $scope.exp_frame=$scope.exp_frame;
      }
    }
  }

  $scope.update=function(){
    $scope.update_img();
    $scope.update_bloch();
  }

  $scope.update_img=function(){
    $http.post('/get_frame',JSON.stringify({'frame':$scope.frame,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.exp_frame = response.data.png_file;

    });
  };

  $scope.update_bloch=function(){
    $http.post('/solve_bloch',JSON.stringify({'frame':$scope.frame}))
      .then(function(response){
        $scope.var_data = response.data;
    });
  };


  $scope.var_data={'width':250,'height':800};
  $http.get('/init')
    .then(function(response){
      $scope.structure = response.data.mol;
      $scope.max_frame = response.data.max_frame;
      $scope.zmax      = response.data.zmax;
      $scope.frame     = response.data.frame;
      $log.log($scope.frame);
      $scope.update()
    });

}]);
