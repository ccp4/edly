var app = angular.module('app', ['ngTouch','ngAria']);
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


app.directive('linePlot', function () {
  // Create a link function
  function linkFunc(scope, element, attrs) {
      scope.$watch('var_data', function (plots) {
          var layout = {
              'width': attrs.width,
              'height': attrs.height,
          };

          Plotly.newPlot(element[0], plots, layout);
      }, true);
  }

  // Return this function for linking ...
  return {
      link: linkFunc
  };
});

app.controller('viewer', ['$scope','$rootScope','$log','$http', '$interval', function ($scope,$rootScope,$log,$http,$interval) {

  var fig_path='/static/data/'
  $scope.inc_frame=function(){
    $scope.frame=Math.min($scope.max_frame,$scope.frame+1);
    $scope.update_frame();
  };
  $scope.dec_frame=function(){
    $scope.frame=Math.max(1,$scope.frame-1);
    $scope.update_frame();
  };
  $scope.update_frame=function(){
    var pad_frame = ('00000'+$scope.frame).slice(-5)+'.png';
    $scope.exp_frame=fig_path+$scope.structure+'/exp/'+pad_frame;
    // $log.log($scope.exp_frame);
    $http.post('/get_frame',JSON.stringify({'frame':$scope.frame}))
      .then(function(response){
        $scope.plot_data = response.data.im;
    });

    $http.post('/solve_bloch',JSON.stringify({'frame':$scope.frame}))
      .then(function(response){
        $scope.ly_data = response.data;
        $log.log(Object.values($scope.ly_data.I));
        $scope.var_data=[
          {
            x:Object.values($scope.ly_data.px),
            y:Object.values($scope.ly_data.py),
            mode: 'markers',
            marker:{
              // size:Object.values($scope.ly_data.I)*1,
              size:Object.values($scope.ly_data.I),
            }
          }
        ];
        // $scope.var_data=[
        //   {
        //     x:Object.values($scope.ly_data.px),
        //     y:Object.values($scope.ly_data.py),
        //     mode: 'markers',
        //     marker:{
        //       // size:Object.values($scope.ly_data.I)*1,
        //       size:Object.values($scope.ly_data.I),
        //     }
        //   }
        // ];
    });

    // $scope.var_data=[
    //   {
    //     z:$scope.plot_data,
    //     type: 'scatter',
    //     colorscale: 'Greys',
    //     zauto:false,
    //     zmin:0,
    //     zmax:100,
    //   }
    // ];
    // $scope.exp_frame=fig_path+$scope.structure+'/exp/'+pad_frame;
    // $scope.sim_frame=fig_path+$scope.structure+'/sim/'+pad_frame;
  };


  $http.get('/get_info')
    .then(function(response){
      $scope.max_frame = response.data.max_frame;
    });

  $scope.frame=1;
  $scope.structure='glycine';
  $scope.exp_frame='';

  // $scope.sim_frame=fig_path+'dummy.png';
  $scope.update_frame()
}]);
