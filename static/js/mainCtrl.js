angular.module('app').
  controller('mainCtrl',['$scope','$rootScope','$log','$http', '$interval','$timeout',function ($scope,$rootScope,$log,$http,$interval,$timeout) {


  var timer;
  var sel_style = {"border-style":'solid','background-color':'#18327c'};

  $scope.set_mode=function(val){
    $scope.mode_style[$scope.mode] = '';
    $scope.mode = val;
    $scope.mode_style[val]=sel_style;
    // $log.log($scope.mode)
    $http.post('set_mode',val) //JSON.stringify({'val':val}))
    .then(function(response){
      if ($scope.changed==true){
        // $log.log($scope.mode,response.data)
        $scope.update();
        // if ($scope.mode=='frames'){
        //   $scope.update_img();
        // }
        $scope.changed=false;
        }
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
    switch ($scope.mode){
      case 'bloch':
          $rootScope.$emit('update_bloch',$scope.frame);
        break;
      case 'frames':
        if ($scope.max_frame>0){
          $scope.update_img();break;
        }
      case 'ms':
        $log.log('ms');break;
    }
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

  $scope.update_frame_event=function(e){
    switch (e.keyCode){
      case 37: $scope.dec_frame();break;
      case 39: $scope.inc_frame();break;
      case 13:
        $scope.toggle_reload();
        // $scope.toggle_reload();
        // $scope.update_frame();
        break;
    }
  }


  $scope.update_frame=function(){
    $scope.frame=Math.max(1,Math.min($scope.frames.active_frame,$scope.max_frame));
    // $log.log($scope.frame,$scope.frames.active_frame)
    if ($scope.frame == $scope.frames.active_frame){
      $scope.changed=true;
      $scope.update();
    }
    $scope.frames.active_frame=$scope.frame;

    // $scope.frame = $scope.frames.active_frame;
    // $scope.frame=Math.max(1,Math.min($scope.frame,$scope.max_frame));
    // $scope.bloch_solve_reset();
  }

  $scope.update_zmax=function(event,frame_type){
    if (event.key=='Enter'){
      $scope.update_keyval('zmax',$scope.zmax,0);
      $scope.draw_frame(frame_type);
      // $http.post('update_zmax',JSON.stringify({'frame_type':frame_type,'zmax':$scope.zmax[frame_type]}))
      // .then(function(response){
      //   // $log.log(response.data);
      // });
    }
  }

  $scope.draw_frame=function(frame_type){
    dats = $scope.data[frame_type];
    const npts = dats.length;
    const wh   = Math.sqrt(npts)
    // $log.log(wh);

    const vals = new Uint8ClampedArray(npts);
    for (let i = 0; i < vals.length; i += 1) {
      vals[i] = Math.floor((Math.min(dats[i],$scope.zmax[frame_type]-1)/$scope.zmax[frame_type])*$scope.nb_colors);
    }

    var cs   = $scope.heatmaps[$scope.caxis.cmap];//$scope.caxis.cmap;//.vals;
    const arr = new Uint8ClampedArray(4*dats.length);
    // Fill the array with the RGBA values of the colormap
    for (let i = 0; i < dats.length; i += 1) {
      // var idx=3*dats[Math.floor(i/4)]
      arr[4*i + 0] = cs[3*vals[i]+0]; // R value
      arr[4*i + 1] = cs[3*vals[i]+1]; // G value
      arr[4*i + 2] = cs[3*vals[i]+2]; // B value
      arr[4*i + 3] = 255;
      // console.log(dats[i]);
    }
    draw_frame(frame_type,arr,wh);//,$scope.cmap);
  }

  $scope.change_heatmap=function(){
    // $log.log($scope.caxis.cmap);
    $scope.draw_frame("exp");
    if ($scope.dat['sim']==true){
      $scope.draw_frame("sim");
    }
    $scope.update_keyval('cmap',$scope.caxis.cmap,0);
  }

  $scope.update_img=function(){
    $scope.frames.active_frame = $scope.frame;
    // $log.log('reloading frame',$scope.frames)
    $http.post('get_frame',JSON.stringify({'frame':$scope.frame-1}))//,'zmax':$scope.zmax}))
      .then(function(response){
        $scope.data['exp'] = response.data.exp;
        $scope.draw_frame("exp");

        if ($scope.dat['sim']==true){
          $scope.data['sim'] = response.data.sim;
          $scope.draw_frame("sim");

        }
    });
  }

  $scope.update_keyval=function(key,val,refresh){
    // $log.log('upadting offset to',$scope.frames.offset )
    $http.post('update_keyval',JSON.stringify({key:key,val:val}))
      .then(function(response){
        if (refresh){
          $scope.update_frame();
        }
        // $log.log(response.data.val);
    });
  }

  $scope.update_offset = function(){
    $scope.update_keyval('offset',$scope.frames.offset,1);
  }

  // $scope.toggle_reload=function(){
  //   $scope.frames.reload=!$scope.frames.reload
  //   $scope.update_keyval('reload',$scope.frames.reload)
  //   if ($scope.frames.reload){
  //     $scope.mode_style['reload']=sel_style
  //   }
  //   else{
  //     $scope.mode_style['reload']=''
  //   }
  // }

  $scope.show_structure = function(){
    $scope.expand['struct']=!$scope.expand['struct']
    // $log.log($scope.crys.chemical_formula)
    update_formula($scope.crys.chemical_formula);
  }

  // $scope.init_panels=function(){
  //   if ($scope.mode in {'felix':'',bloch:''}){
  //     // $rootScope.$emit('init_'+$scope.mode)
  //     switch($scope.mode){
  //       case 'felix':
  //         $rootScope.$emit('init_felix');break
  //       case 'bloch':
  //         $rootScope.$emit('init_bloch');break
  //       }
  //   }
  // }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // init stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.init = function(){
    $http.get('init')
      .then(function(response){
        $scope.structure = response.data.mol;
        $scope.crys      = response.data.crys;
        $scope.cif_file  = $scope.crys.file!='?';
        // $log.log($scope.crys.file,$scope.cif_file)
        // frames related stuffs
        $scope.dat       = response.data.dat;
        $scope.frame     = response.data.frame;
        $scope.max_frame = response.data.nb_frames;

        $scope.data      = {'exp':0,'sim':0};
        $scope.zmax      = response.data.zmax;
        $scope.nb_colors = response.data.nb_colors;
        $scope.heatmaps  = response.data.heatmaps;
        $scope.cmaps     = response.data.cmaps;
        $scope.caxis     = {'cmap':response.data.cmap};
        $scope.frames.offset = response.data.offset;
        $scope.frames.active_frame = response.data.frame;

        // mode : frames, bloch, felix
        $scope.mode = response.data.mode;
        $scope.modes = response.data.modes;
        $scope.mode_style[$scope.mode]=sel_style;

        $scope.update();
    });
  }

  $scope.changed=true;
  $scope.frame_offset_on=false;
  $scope.frames = {offset:0,active_frame:0,reload:true,manual:true}
  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.expand={};
  $scope.popup={};


  $scope.modes={'molecule':false};
  $scope.mode_style = {bloch:'',frames:'',felix:'',reload:''};
  $scope.titles={'frames':'Frames Viewer','bloch':'Bloch solver','ms':'Multislice solver','felix':'Felix Solver'}
  $scope.init();
}]);
