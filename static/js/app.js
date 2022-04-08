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

  ///////////////////////////////////////////////////////////////////
  // uploads
  ///////////////////////////////////////////////////////////////////
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

  ///////////////////////////////////////////////////////////////////
  // Toggles
  ///////////////////////////////////////////////////////////////////
  $scope.toggle_mode=function(key){
    $scope.modes[key]=!$scope.modes[key]
    $http.post('/toggle_mode',JSON.stringify({'key':key,'val':$scope.modes[key]}))
    .then(function(response){
      $log.log(response.data);
    });
  }

  $scope.toggle_manual_mode=function(){
    $scope.toggle_mode('manual');
    if (!$scope.modes['manual']){
        $scope.update();
    }
  }

  $scope.toggle_analysis_mode=function(){
    $scope.toggle_mode('analysis');
    $scope.update()
  }

  $scope.toggle_popup=function(key){
    $scope.popup[key]=!$scope.popup[key];
  }

  ///////////////////////////////////////////////////////////////////
  // Frames
  ///////////////////////////////////////////////////////////////////
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

  $scope.update_img=function(){
    $http.post('/get_frame',JSON.stringify({'frame':$scope.frame,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.img = response.data;
    });
  }



  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Bloch
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.solve_bloch=function(event){
    if (event.key=='Enter'){
      $scope.update_bloch();
    }
  }
  $scope.update_bloch=function(){
    $http.post('/solve_bloch',JSON.stringify({'frame':$scope.frame,'bloch':$scope.bloch,'manual_mode':$scope.modes['manual']}))
      .then(function(response){
        $scope.load_bloch(response.data);
        if (!$scope.modes['single']){
          $scope.beam_vs_thickness()
        }
    });
  };

  $scope.load_bloch = function (data){
    $scope.fig       = JSON.parse(data.fig);
    $scope.bloch     = data.bloch;
    $scope.nbeams    = data.nbeams;
    $scope.theta_phi = data.theta_phi.split(',');
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Rotate mode
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update_theta_phi=function(e){
    // $log.log(e.keyCode);
    var updated = false;
    var theta_phi=[Number($scope.theta_phi[0]),Number($scope.theta_phi[1])];
    switch (e.keyCode) {
        case 37:
          theta_phi[1]-=$scope.dtheta_phi;
          updated=true;
          break;
        case 38:
          theta_phi[0]+=$scope.dtheta_phi;
          updated=true;
          break;
        case 39:
          theta_phi[1]+=$scope.dtheta_phi;
          updated=true;
          break;
        case 40:
          theta_phi[0]-=$scope.dtheta_phi;
          updated=true;
          break;
        case 34:
          $scope.dtheta_phi*=2;
          break;
        case 33:
          $scope.dtheta_phi/=2;
          break;
        case 8:
          $scope.dtheta_phi=0.1;
          break;
        case 13:
          $scope.update_bloch();
          break;
    }
    if (updated){
      theta_phi[0]%=180;
      theta_phi[1]%=360;
      $http.post('/bloch_rotation',JSON.stringify({'theta_phi':theta_phi}))
        .then(function(response){
          $scope.load_bloch(response.data);
        });
    }
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Thickness
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update_thickness = function (e) {
    var updated=false;
    switch (e.keyCode) {
        case 37:
          $scope.bloch['thick']-=$scope.dthick;
          updated=true;
          break;
        case 38:
          $scope.bloch['thick']+=$scope.dthick;
          updated=true;
          break;
        case 39:
          $scope.bloch['thick']+=$scope.dthick;
          updated=true;
          break;
        case 40:
          $scope.bloch['thick']-=$scope.dthick;
          updated=true;
          break;
        case 34:
          $scope.dthick+=5;
          break;
        case 33:
          $scope.dthick-=5;
          break;
        case 8:
          $scope.dthick=5;
          break;
        case 13:
          updated=true;
          break;
    }
    if (updated){
      $http.post('/update_thickness',JSON.stringify({'thick':$scope.bloch['thick']}))
      .then(function(response){
        $scope.fig = response.data;
      });
    }
  }

  $scope.update_beam_vs_thickness = function (event) {
    if (event.key=='Enter'){
      $scope.beam_vs_thickness()
    }
  }

  $scope.beam_vs_thickness = function () {
    $http.post('/beam_vs_thick',JSON.stringify({'thicks':$scope.bloch['thicks'],'refl':$scope.refl}))
      .then(function(response){
        $scope.modes['single']=false;
        $scope.fig2 = response.data;
    });
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // misc/init stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update=function(){
    if ($scope.modes['analysis']){
      $scope.update_bloch();
    }
    else{
      $scope.update_img();
    }
  }
  $scope.popup={'pets':false,'mol':false,'exp':false,'sim':false,'ana':false,
    'keV':false, 'u':false,'Smax':false, 'Nmax':false,'thicks':false,'thick':false,
    'nbms':false};

  $scope.analyis_mode=false;
  $scope.fig={};
  $scope.fig2={};
  // $scope.var_data={'width':250,'height':800};
  $http.get('/init')
    .then(function(response){
      $scope.structure = response.data.mol;
      $scope.frame     = response.data.frame;
      $scope.max_frame = response.data.max_frame;
      $scope.zmax      = response.data.zmax;
      $scope.bloch     = response.data.bloch;
      $scope.cif       = response.data.cif;
      $scope.cif_file  = response.data.cif_file;
      $scope.modes     = response.data.modes;
      $scope.theta_phi=response.data.theta_phi.split(',');

      $scope.update()
      if (!$scope.modes['single']){
        $scope.beam_vs_thickness();
      }
    });

    $scope.nbeams=0;
    $scope.show_buttons=false;
    // $scope.show={'molecule':false,'single':false}
    $scope.dtheta_phi=0.1;
    $scope.dthick=5;
    $scope.refl=[];
}]);
