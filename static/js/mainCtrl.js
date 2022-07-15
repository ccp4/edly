angular.module('app').
  controller('mainCtrl',['$scope','$rootScope','$log','$http', '$interval','$timeout',function ($scope,$rootScope,$log,$http,$interval,$timeout) {


  var timer;
  var sel_style = {"border-style":'solid','background-color':'#18327c'};

  $scope.set_mode=function(val){
    $scope.mode_style[$scope.mode] = '';
    $scope.mode = val;
    $scope.mode_style[val]=sel_style;
    $http.post('set_mode',val) //JSON.stringify({'val':val}))
    .then(function(response){
        $scope.update()
        // $log.log($scope.mode,response.data)
      });
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
        if ($scope.init_done){
          $rootScope.$emit('update_bloch');
        }
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
    $scope.frames.active_frame+=1;//=Math.min($scope.max_frame,$scope.frame+1);
    $scope.update_frame();
  };
  $scope.dec_frame=function(){
    $scope.frames.active_frame-=1;//=Math.max(1,$scope.frame-1);
    $scope.update_frame();
  };
  $scope.update_frame=function(){
    // $log.log($scope.frames.active_frame)
    $scope.frame = $scope.frames.active_frame;
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
    $scope.frames.active_frame = $scope.frame;
    // $log.log('reloading frame',$scope.frames)
    $http.post('get_frame',JSON.stringify({'frame':$scope.frame,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.img = response.data;
    });
  }

  $scope.update_keyval=function(key,val){
    // $log.log('upadting offset to',$scope.frames.offset )
    $http.post('update_keyval',JSON.stringify({key:key,val:val}))
      .then(function(response){
        $scope.update_frame();
    });
  }

  $scope.update_offset = function(){
    $scope.update_keyval('offset',$scope.frames.offset);
  }

  $scope.toggle_reload=function(){
    $scope.frames.reload=!$scope.frames.reload
    $scope.update_keyval('reload',$scope.frames.reload)
    if ($scope.frames.reload){
      $scope.mode_style['reload']=sel_style
    }
    else{
      $scope.mode_style['reload']=''
    }
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // init stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.init_done=false
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
        $scope.frames.offset = response.data.offset;
        $scope.frames.active_frame = response.data.frame;
        $scope.frames.reload = response.data.reload;
        if ($scope.frames.reload){
          $scope.mode_style['reload']=sel_style;
        }
        $scope.mode         = response.data.mode;
        $scope.mode_style[$scope.mode]=sel_style;
        $scope.update();
        $scope.init_done=true
    });
  }

  $scope.frames = {offset:0,active_frame:0,reload:true}
  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.expand={};
  $scope.popup={};


  $scope.modes={'molecule':false};
  $scope.mode_style = {bloch:'',frames:'',felix:'',reload:''};
  $scope.titles={'frames':'Frames Viewer','bloch':'Bloch solver','ms':'Multislice solver','felix':'Felix Solver'}
  $scope.init();
}]);
