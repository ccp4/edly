angular.module('app').
  controller('mainCtrl',['$scope','$rootScope','$log','$http', '$interval','$timeout',function ($scope,$rootScope,$log,$http,$interval,$timeout) {


  var timer;
  var sel_style = {"border-style":'solid','background-color':'#18327c'};

  // mouseenter event
  $scope.showIt = function (val) {
      timer = $timeout(function () {
          $scope.popup[val] = true;
      }, 750);
      $scope.popup[val] = false;
  };
  // mouseleave event
  $scope.hideIt = function (val) {
    $timeout.cancel(timer);
    $scope.popup[val]=false;
  };

  $scope.reset_search=function(id){
    $scope.search_name({'key':'Escape'},id)
  }

  $scope.show_search=function(id){
    $scope.search_name({'key':''},id)
  }

  $scope.search_name=function(e,id){
    var filter, a, i, txtValue,values,options;
    filter=get_input_value("search_"+id).toUpperCase();
    options=[];
    if (e.key!='Escape'){
      switch (id){
        case 'struct'      :values=$scope.structures;break;
        case 'frames'      :values=Object.keys($scope.zenodo.titles);break;
        case 'local_frames':values=$scope.local_frames.folders;break;
      }
      // $log.log(filter);
      for (i = 0; i <values.length ; i++) {
          txtValue = values[i];
          if (txtValue.toUpperCase().indexOf(filter) > -1) {
              options.push(txtValue);
          }
      }
    }

    switch (id){
      case 'struct'       : $scope.structures_filtered=options;break;
      case 'frames'       : $scope.zenodo.frames_filtered=options;break;
      case 'local_frames' : $scope.local_frames.filtered=options;break;
    }
    // $log.log(filter,options)
  }

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

  $scope.toggle_sync_frames=function(){
    // $log.log('sync frames')
    $scope.sync_frame=!$scope.sync_frame;
    $scope.styles['sync_frame']='';
    if ($scope.sync_frame){
      $scope.styles['sync_frame']=sel_style;
    }
    $rootScope.$emit('toggle_sync_frames');

  }

  $scope.update=function(init=0){
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
  //New structure
  ///////////////////////////////////////////////////////////////////
  $scope.new_structure=function(){
    $http.post('new_structure',JSON.stringify($scope.new_project))
    .then(function(response){
      $log.log('new_structure response : ',response.data);
      if(response.data.msg){
        $scope.new_project.error = true;
        $scope.show_error(response.data.msg,1)
      }
      else{
        $log.log('ok')
        $scope.structures=response.data.structures;
        close_dialog();
        $scope.set_structure($scope.new_project.name)
      }
    })
  }

  ///////////////////////////////////////////////////////////////////
  //Import
  ///////////////////////////////////////////////////////////////////
  $scope.set_import=function(val){
    $scope.import_style[$scope.import_mode]=false;
    $scope.import_mode = val;
    $scope.import_style[val]=sel_style;
  }

  ////////////////////////////////////////
  // import folder molecule
  ////////////////////////////////////////
  $scope.set_structure=function(mol){
    $http.post('set_structure',JSON.stringify({'mol':mol}))
    .then(function(response){
        $scope.init();
    })
  }

  $scope.delete_structure=function(){
    $log.log('deleting : ',$scope.open_mol.name)
    $http.post('delete_structure',JSON.stringify({'mol':$scope.open_mol.name}))
    .then(function(response){
        $scope.structures=response.data.structures;
        if ($scope.structure==$scope.open_mol.name){
          $scope.init();
        }
        $scope.open_mol.name="";//$scope.structures[0];
    })
  }

  $scope.get_structure_info=function(mol){
    $http.post('get_structure_info',JSON.stringify({'mol':mol}))
    .then(function(response){
      // $log.log(response.data)
      $scope.open_mol=response.data;
    })
  }
  $scope.get_structure_info_e=function(){
    $scope.get_structure_info($scope.open_mol.name);
  }

  $scope.select_mol=function(x){
    // $log.log($scope.open_mol);
    $scope.open_mol.name=x;
    $scope.structures_filtered=[];
    $scope.get_structure_info(x);
  }

  $scope.show_error=function(msg,err){
    $scope.new_project.error_msg = msg;
    color = {0:'green',1:'red'}[err];
    $scope.new_project.error_color={'color':color}
    // $log.log($scope.new_project.error_color)
  }

  ////////////////////////////////////////
  // import Frames
  ////////////////////////////////////////
  $scope.update_zenodo=function(fetch=false){

    // $http.get('/static/spg/records.json')
    $http.post('/update_zenodo',JSON.stringify({'fetch':fetch}))
    .then(function(response){
      $scope.zenodo.records = response.data;
      $scope.zenodo.record  = $scope.zenodo.records[Object.keys($scope.zenodo.records)[0]];
      $scope.zenodo.titles  = {};
      for (let s in $scope.zenodo.records){
        // $log.log(s)
        $scope.zenodo.titles[$scope.zenodo.records[s].title]=s;
      }//$log.log($scope.zenodo.titles);
      $scope.frames_filtered=[];//Object.keys($scope.zenodo.titles);
      $scope.zenodo.name = $scope.zenodo.record.title;

      $scope.update_link($scope.zenodo.record.files[Object.keys($scope.zenodo.record.files)[0]])
    })
  }

  $scope.update_link=function(file){
    $scope.download.link='https://zenodo.org'+file.link;
    $scope.check_dl_frames();
  }

  $scope.check_dl_frames=function(){
    // $log.log('check link',$scope.download.link)
    $http.post('check_dl_frames',$scope.download.link)
    .then(function(response){
      $scope.download.downloaded=response.data.dl;
      if ($scope.download.downloaded){
        $scope.data_folders=response.data.folders;
      }
    })
  }

  $scope.select_local_frames=function(x){
    $scope.download.link=x;
    $scope.local_frames.name=x
    $scope.local_frames.filtered=[];
    $scope.check_dl_frames();
  }

  $scope.select_record=function(x){
    $scope.zenodo.record = $scope.zenodo.records[$scope.zenodo.titles[x]];
    // $log.log($scope.zenodo.record)
    $scope.change_files_table()
    $scope.zenodo.frames_filtered=[];
  }

  $scope.change_files_table=function(){
    $scope.zenodo.name=$scope.zenodo.record.title;
    // $log.log($scope.zenodo.record)
    $scope.update_link($scope.zenodo.record.files[Object.keys($scope.zenodo.record.files)[0]])
    $scope.download.info='done';
  }

  var interval_dl;
  $scope.download_frames=function(){
    $http.post('check_dl_format',$scope.download.link)
    .then(function(response){
      $scope.download.info=response.data.msg;
      if ($scope.download.info=='ready to download'){
        interval_dl = $interval(function () {
          $http.post('get_dl_state',$scope.download.link)
          .then(function(response) {
            $scope.download.info=response.data;
            if(response.data.includes('done')){
              $scope.download.info='done';
              $scope.download.downloading=false;
              $interval.cancel(interval_dl);
              if (response.data.split(':')[1]=='0'){
                $log.log('download success')
                $scope.check_dl_frames();
              }
            }
          })
        },200);

        $scope.download.downloading=true;
        $http.post('download_frames',$scope.download.link)
        .then(function(response){
          $log.log('download_frames request complete')
        })
      }
    })
  }

  $scope.cancel_download=function(){
    $log.log('cancelling download')
    $http.post('cancel_download',$scope.download.link)
  }

  $scope.import_frames=function(folder){
    $http.post('load_frames',folder)
    .then(function(response){
      $scope.dat                 = response.data.dat;
      $scope.max_frame           = response.data.nb_frames;
      $scope.frame_folder['exp'] = response.data.folder;
      $scope.frame               = 1;
      $scope.frames.active_frame = $scope.frame;
      $scope.set_mode('frames');
      $scope.expand['struct']=false;
      $scope.update();
    })
  }

  $scope.remove_frames=function(){
    $http.post('remove_frames',$scope.open_mol.name)
    .then(function(response){
      if (response.data.refresh){
        $scope.get_structure_info($scope.open_mol.name);
        $scope.dat=false;
      }
    })
  }

  ////////////////////////////////////////
  // import processed data
  ////////////////////////////////////////
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
        // $log.log(response.data);
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

  ////////////////////////////////////////
  // import cif
  ////////////////////////////////////////
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
    // $log.log(filename);
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
        $scope.set_mode('bloch')
    })
  }

  ///////////////////////////////////////////////////////////////////
  ///////////////////////////////////////////////////////////////////
  // Frames mode
  ///////////////////////////////////////////////////////////////////
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
      v = Math.max(Math.min(dats[i],vM)-vm,0)/(vM-vm);//between 0 and 1
      vals[i] = Math.floor(v*($scope.nb_colors-1))   ;//#index into the colormap
    }
    // const max = vals.reduce((a, b) => Math.max(a, b), -Infinity);
    // $log.log(max)

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


  //////////////////////////////////////////////////////////////////////////////
  // misc
  //////////////////////////////////////////////////////////////////////////////
  $scope.change_show_input_link = function(){
  $scope.show_input_link=!$scope.show_input_link
  if (!$scope.show_input_link){
    $scope.check_dl_frames();
    }
  }
  //////////////////////////////////////////////////////////////////////////////
  // init stuffs
  //////////////////////////////////////////////////////////////////////////////

  $scope.init = function(){
    $http.get('init')
      .then(function(response){
        $scope.structures = response.data.structures//;$log.log($scope.structures)
        $scope.builtins   = response.data.builtins  //;$log.log($scope.builtins)
        $scope.structure  = response.data.mol;      //;$log.log($scope.structure)
        $scope.crys       = response.data.crys;     //;$log.log($scope.crys)
        $scope.cif_file   = $scope.crys.file!='?';  //;$log.log('cif present:',$scope.cif_file)


        // frames related stuffs
        $scope.dat                 = response.data.dat;
        $scope.frame               = response.data.frame;
        $scope.max_frame           = response.data.nb_frames;
        $scope.frame_folder        = response.data.folder   ;//$log.log($scope.frame_folder)
        $scope.frames.active_frame = response.data.frame;
        $scope.frames.offset       = response.data.offset;
        $scope.frames.u            = '';
        $scope.frames.pedestal     = 0;
        $scope.local_frames.folders = response.data.local_frames;
        // $log.log('frames : ',  $scope.dat,$scope.max_frame)

        $scope.data      = {'exp':0,'sim':0};
        $scope.zmax      = response.data.zmax;
        $scope.nb_colors = response.data.nb_colors;
        $scope.heatmaps  = response.data.heatmaps;
        $scope.cmaps     = response.data.cmaps;
        $scope.caxis     = {'cmap':response.data.cmap};


        // $scope.zenodo_records = response.data.zenodo_records;
        $scope.update_zenodo();

        update_formula($scope.crys.chemical_formula);
        $scope.get_structure_info($scope.structure );
        // mode : frames, bloch, felix
        $scope.mode  = response.data.mode           //;$log.log('mode  : ',$scope.mode)
        $scope.modes = response.data.bloch_modes    //;$log.log('modes : ',$scope.modes)
        $scope.mode_style[$scope.mode]=sel_style;
        $rootScope.$emit('init_bloch_panel',$scope.frame,0);
        if ($scope.structure==''){$scope.expand['importer']=true;}
    });
  }
  $rootScope.$on('update',function(event,data={}){
    // $log.log(data)
    if ('frame' in data){
      $scope.frame=data.frame;
      $scope.frames.active_frame=$scope.frame;
    }
    $scope.update();
  })
  $scope.changed=true;
  $scope.download={'zenodo':true,'link':'','info':'done','downloaded':false, 'downloading':false};
  $scope.zenodo={'record':'','records':''}
  $scope.local_frames={'name':'','filtered':[],'folders':[]}
  $scope.show_input_link=false;
  $scope.import_style = {open_struct:'',frames:'',dat:'',cif:''};
  $scope.import_mode  ='open_struct';
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
  $scope.sync_frames=false;
  $scope.dat_info={'dat_type':'unknown','missing_files':'?'};
  // $scope.frame_offset_on=false;

  $scope.new_project={'name':'',
    'is_struct':false,'struct_type':'cif',
    'builtin':'Ac','pdb':'','cif':'',
    'error':false,'error_color':{'color':'green'},'error_msg':''};


  $scope.frames = {offset:0,active_frame:0,reload:true,manual:true,jump_frames:10}
  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.expand={
      'importer':true,'struct':false,
      //'rock_settings':true,'load_rock':true,
    };

  $scope.popup={};//{'u_edit':true};//,'rot_help':true};
  $scope.structures_filtered=[];

  $scope.modes={'molecule':false};
  $scope.mode_style = {bloch:'',frames:'',felix:'',reload:''};
  $scope.mode_titles={'frames':'Frames Viewer','bloch':'Bloch solver','ms':'Multislice solver','felix':'Felix Solver'}
  $scope.sync_frame=true;
  $scope.styles={'sync_frame':sel_style};
  $scope.init();
}]);
