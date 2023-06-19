angular.module('app').
  controller('mainCtrl',['$scope','$rootScope','$log','$http', '$interval','$timeout',function ($scope,$rootScope,$log,$http,$interval,$timeout) {


  var timer;
  var sel_style = {"border-style":'solid','background-color':'#18327c'};

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

  $scope.update = function(init=0){
    switch ($scope.mode){
      case 'bloch':
          $rootScope.$emit('update_frame',$scope.frame,init);
          if ($scope.dat['pets']){
            $http.post('get_u',$scope.frame)
            .then(function(response){
              $scope.frames.u=response.data;
              // $log.log($scope.frames.u);
            });
          }
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
  //Import
  ///////////////////////////////////////////////////////////////////
  $scope.set_import=function(val){
    $scope.import_style[$scope.import_mode]=false;
    $scope.import_mode = val;
    $scope.import_style[val]=sel_style;
  }

  $scope.update_link=function(file){
    $scope.download_link='https://zenodo.org'+file.link;
    $scope.check_dl_frames();
  }

  $scope.check_dl_frames=function(){
    $http.post('check_dl_frames',$scope.download_link)
    .then(function(response){
      $scope.frames_downloaded=response.data.dl;
      if ($scope.frames_downloaded){
        $scope.data_folders=response.data.folders;
      }
    })
  }

  $scope.change_files_table=function(){
    // $log.log($scope.zenodo.record)
    $scope.update_link($scope.zenodo.record.files[Object.keys($scope.zenodo.record.files)[0]])
    $scope.download_info='done';
  }

  $scope.download_frames=function(){
    $http.post('import_frames',$scope.download_link)
    .then(function(response){
      $scope.download_info=response.data.msg;

      // $log.log($scope.download_info,$scope.download_info=='ready to download' )
      if ($scope.download_info=='ready to download'){
        var interval = $interval(function () {
          $http.get('get_dl_state')
          .then(function(response) {
            $scope.download_info=response.data;
          })
        },500);
        $http.post('download_frames',$scope.download_link)
        .then(function(response){
          $interval.cancel(interval);
          $scope.download_info='done';
          $scope.check_dl_frames();
        })
      }
    })
  }

  $scope.import_frames=function(folder){
    $http.post('create_sym_link',folder)
    .then(function(response){
      $scope.dat                 = response.data.dat;
      $scope.max_frame           = response.data.nb_frames;
      $scope.exp_folder          = response.data.folder;
      $scope.frame               = 1;
      $scope.frames.active_frame = $scope.frame;
      $scope.update();
    })
  }

  //////////
  // import processed data
  $scope.check_dat=function(){
    filename=get_file_name("dat");
    // $log.log('dat',$scope.dat.dat_type, ' ' ,filename)
    $http.post('check_dat',filename)
    .then(function(response){
      $scope.dat_valid = response.data.dat_type!='unknown' && response.data.missing_files=='';
      $scope.dat_info  = response.data;
      // $log.log('valid dat',$scope.dat_valid)
    })
    return 1;
  }

  $scope.import_dat=function(){
    $http.post('import_dat')
    .then(function(response){
        $log.log(response.data);
        $scope.dat.dat_type=$scope.dat_info.dat_type;
        $scope.load_dat_type()
        $scope.dat_info={'dat_type':'unknown','missing_files':'?'};
        $scope.dat_valid=false;
        clear_files('dat');
    })
  }

  $scope.load_dat_type=function(){
    $http.post('load_dat_type',$scope.dat.dat_type)
    .then(function(response){
      $scope.dat=response.data;
    })
  }

  //////////
  // import cif
  $scope.check_cif=function(){
    filename  = get_file_name("Cif");
    file_type = filename.split('.').pop();
    $scope.valid_cif = file_type=='cif';
    // $scope.valid_cif = true;
    $scope.$apply()
    // $log.log(filename,file_type,file_type=='cif',$scope.cif_valid);
  }

  $scope.import_cif=function(){
    filename=get_file_name("Cif");
    $log.log(filename);
    $scope.cif_imported=false;
    $http.post('import_cif',filename)
    .then(function(response){
        $scope.cif_imported=true;
        $scope.valid_cif=false;
        $scope.crys=response.data;
        clear_files('Cif');
        $scope.cif_file  = $scope.crys.file!='?';
        // $log($scope.cif_file)
        $scope.show_structure(1)
    })
  }

  ///////////////////////////////////////////////////////////////////
  // Frames
  ///////////////////////////////////////////////////////////////////
  $scope.set_frame=function(s){
      switch (s){
        case 'i':$scope.frames.active_frame  = 1               ;break;
        case '-':$scope.frames.active_frame -= 1               ;break;
        case '+':$scope.frames.active_frame += 1               ;break;
        case 'f':$scope.frames.active_frame  = $scope.max_frame;break;
      }
      $scope.update_frame();
  }
  $scope.inc_frame=function(){
    $scope.frames.active_frame+=1;
    $scope.update_frame();
  };
  $scope.dec_frame=function(){
    $scope.frames.active_frame-=1;
    $scope.update_frame();
  };
  $scope.change_frame=function(s){
    $scope.frames.active_frame+=s;
    $scope.update_frame();
  };

  $scope.update_frame_event=function(e){
    switch (e.keyCode){
      case 83 : $scope.change_frame(-1);break;
      case 87 : $scope.change_frame(+1);break;
      case 68 : $scope.change_frame(+$scope.frames.jump_frames);break;
      case 65 : $scope.change_frame(-$scope.frames.jump_frames);break;
      case 81 : $scope.frames.jump_frames=Math.max($scope.frames.jump_frames/2,1);break;
      case 69 : $scope.frames.jump_frames=Math.min($scope.frames.jump_frames*2,200);break;
      case 8  : $scope.frames.jump_frames=10;break;
    }
  };

  $scope.update_frame=function(){
    $scope.frame=Math.max(1,Math.min($scope.frames.active_frame,$scope.max_frame));
    // $log.log($scope.frame,$scope.frames.active_frame)
    if ($scope.frame == $scope.frames.active_frame){
      $scope.changed=true;
      $scope.update();
    }
    $scope.frames.active_frame=$scope.frame;
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
    vm = $scope.frames.pedestal;
    vM = $scope.zmax[frame_type];
    for (let i = 0; i < vals.length; i += 1) {
      vals[i] = Math.floor(( Math.min(Math.max(dats[i]-vm,0),vM-1)/(vM-vm) )*$scope.nb_colors);
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
    $http.post('get_frame',JSON.stringify({'frame':$scope.frame-1,'type':'exp'}))
    .then(function(response){
        $scope.data['exp'] = response.data;
        $scope.draw_frame("exp");
      });
      if ($scope.dat['sim']==true){
        $http.post('get_frame',JSON.stringify({'frame':$scope.frame-1,'type':'sim'}))
        .then(function(response){
            $scope.data['sim'] = response.data;
            $scope.draw_frame("sim");
        });
      }
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
  $scope.update_omega=function (e) {
    if (event.key=='Enter') {
      $http.post('update_omega',JSON.stringify({'omega':$scope.dat['omega']}))
      .then(function(response){
        $rootScope.$emit('load_fig1',response.data)
        // $scope.fig1 = response.data;
      })
    }
  }

  $scope.show_structure = function(val=-1){
    if (val<0){
      $scope.expand['struct']=!$scope.expand['struct']
    }
    else{
      $scope.expand['struct']=val;
    }
    // $log.log($scope.crys.chemical_formula)
    update_formula($scope.crys.chemical_formula);
  }

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
        $scope.dat                 = response.data.dat;
        $scope.frame               = response.data.frame;
        $scope.max_frame           = response.data.nb_frames;
        $scope.exp_folder          = response.data.folder;
        $scope.frames.active_frame = response.data.frame;
        $scope.frames.offset       = response.data.offset;
        $scope.frames.u            = '';
        $scope.frames.pedestal     = 0;

        $scope.data      = {'exp':0,'sim':0};
        $scope.zmax      = response.data.zmax;
        $scope.nb_colors = response.data.nb_colors;
        $scope.heatmaps  = response.data.heatmaps;
        $scope.cmaps     = response.data.cmaps;
        $scope.caxis     = {'cmap':response.data.cmap};


        // $scope.zenodo_records = response.data.zenodo_records;
        $http.get('/static/spg/records.json')
        .then(function(response){
          $scope.zenodo.records = response.data;
          $scope.zenodo.record  = $scope.zenodo.records[Object.keys($scope.zenodo.records)[0]];
          $scope.update_link($scope.zenodo.record.files[Object.keys($scope.zenodo.record.files)[0]])
        })

        // mode : frames, bloch, felix
        $scope.mode = response.data.mode;
        $scope.modes = response.data.modes;
        $scope.mode_style[$scope.mode]=sel_style;
        $rootScope.$emit('init_bloch_panel',$scope.frame,0);
    });
  }
  $rootScope.$on('update',function(event,data){
      $scope.update();
  })
  $scope.zenodo={'record':'','records':''}
  $scope.changed=true;
  $scope.frames_downloaded=false;
  $scope.download_info='done';
  $scope.import_mode='frames';
  $scope.import_style = {frames:'',dat:'',cif:''};
  $scope.import_style[$scope.import_mode]=sel_style;
  $scope.dat_type_files = {
      'xds'   : 'A single XDS_ASCII.HKL file ' ,
      'pets'  : 'A zip file containing .pts .rpl .xyz .cor .hkl .cenloc files, .dyn_cif_pets and a cif file.' ,
      'dials' : 'A zip file containing at least imported.expt, indexed.refl and reflections.txt files',
  }
  $scope.dat_types = Object.keys($scope.dat_type_files);
  $scope.dat_valid = false;
  $scope.valid_cif = false;
  $scope.cif_imported=true;
  $scope.dat_info={'dat_type':'unknown','missing_files':'?'};
  // $scope.frame_offset_on=false;

  $scope.frames = {offset:0,active_frame:0,reload:true,manual:true,jump_frames:10}
  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.expand={'rock_settings':true,'importer':false, 'struct':false};
  $scope.popup={};


  $scope.modes={'molecule':false};
  $scope.mode_style = {bloch:'',frames:'',felix:'',reload:''};
  $scope.titles={'frames':'Frames Viewer','bloch':'Bloch solver','ms':'Multislice solver','felix':'Felix Solver'}
  $scope.init();
}]);
