angular.module('app').
  controller('mainCtrl',['$scope','$rootScope','$log','$http', '$interval','$timeout',function ($scope,$rootScope,$log,$http,$interval,$timeout) {

    var sel_style = {"border-style":'solid','background-color':'#18327c'};
    var timer;

  $scope.set_analysis_mode=function(val){
    $scope.mode = val;
    $scope.mode_style = {'bloch':'','frames':''};
    $scope.mode_style[val]=sel_style;
    $http.post('set_mode',JSON.stringify({'key':key,'val':val}))
    .then(function(response){
        $log.log(response.data);
      });

    // console.log($scope.mode)
  }


  // mouseenter event
  $scope.showIt = function (val) {
      timer = $timeout(function () {
          $scope.popup[val] = true;
      }, 500);
  };
  // mouseleave event
  $scope.hideIt = function (val) {
      $timeout.cancel(timer);
      $scope.popup[val]=false;
  };


  $scope.update = function(){
    // return new Promise(function(resolve, reject){
    switch ($scope.mode){
      case 'bloch':
        // if ( ! ($scope.modes['manual'] && $scope.modes['u']=='rock')){
        //   $scope.update_bloch();
        // }
        // else{
        //   $scope.get_rock_sim();
        // }
        break;
      case 'frames':
        $scope.update_img();break;
      case 'ms':
        $log.log('ms');break;
    }
    //   resolve($log.log($scope.rings));
    // });
  }


  ///////////////////////////////////////////////////////////////////
  // Frames
  ///////////////////////////////////////////////////////////////////
  $scope.inc_frame=function(){
    $scope.frame+=1;//=Math.min($scope.max_frame,$scope.frame+1);
    $scope.update_frame();
  };
  $scope.dec_frame=function(){
    $scope.frame-=1;//=Math.max(1,$scope.frame-1);
    $scope.update_frame();
  };
  $scope.update_frame=function(){
    $scope.frame=Math.max(1,Math.min($scope.frame,$scope.max_frame));
    // $log.log($scope.frame)
    changed=true;
    // $scope.bloch_solve_reset();
    $scope.update();
  }

  $scope.update_zmax=function(event,val){
    if (event.key=='Enter'){
      if ($scope.zmax[val]>0){
        $http.post('update_zmax',JSON.stringify({'zmax':$scope.zmax[val],'key':val}))
          .then(function(response){
            $scope.img[val] = response.data;
        });
      }
    }
  }

  $scope.update_img=function(){
    $http.post('get_frame',JSON.stringify({'frame':$scope.frame,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.img = response.data;
    });
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // init stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.init = function(){
    $http.get('init')
      .then(function(response){
        $scope.structure = response.data.mol;
        $scope.dat       = response.data.dat;
        $scope.frame     = response.data.frame;
        $scope.crys      = response.data.crys;
        $scope.cif_file  = response.data.cif_file;
        $scope.max_frame = response.data.max_frame;
        $scope.zmax      = response.data.zmax;
        $scope.mode      = response.data.mode;
        $scope.u_style[$scope.modes['u']]={"border-style":'solid'};
        $scope.mode_style[$scope.mode]=sel_style;
        $scope.update();
    });
  }


  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.expand={};
  $scope.popup={};


  $scope.modes={'molecule':false};
  $scope.u_style = {'edit':'','move':'','rock':''};
  $scope.mode_style = {'bloch':'','frames':''};
  $scope.titles={'frames':'Frames Viewer','bloch':'Bloch solver','ms':'Multislice solver','felix':'Felix Solver'}
  $scope.init();
}]);
