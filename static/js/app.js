var app = angular.module('app', ['ngTouch','ngAria']);
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


// Plotly directive
app.directive('linePlot', function () {
  function linkFunc(scope, element, attrs) {
      scope.$watch(attrs.fig, function (new_fig,fig) {
          Plotly.newPlot(element[0].id, new_fig.data, new_fig.layout);
          if (element[0].id=='fig1'){
            scope.initPlotly=true
            document.getElementById(element[0].id).on('plotly_click', scope.addRow_tagTable);
            document.getElementById(element[0].id).on('plotly_legendclick', scope.leg_click);
        }
      }, true);
  }
  return {
      link: linkFunc
  };
});

app.directive('ngKeyEnter', function() {
  function linkFunc(scope, element, attrs) {
    element.bind("keydown keypress", function(event) {
      if (event.which == 13) {
        scope.$apply(function() {
            scope.$eval(attrs.ngKeyEnter);
        });
      }
    });
  }
  return {
    link:linkFunc
  };
});



app.controller('viewer', ['$scope','$rootScope','$log','$http', '$interval','$timeout', function ($scope,$rootScope,$log,$http,$interval,$timeout) {

  $scope.initPlotly=false
  /////////////////////////////////
  //// plotly cb
  /////////////////////////////////
  $scope.update_refl = function(){
    $scope.refl = extract_list_indices_from_table();
    $http.post('update_refl',JSON.stringify({'refl':$scope.refl}))
      .then(function(response){
        // $log.log(response.data);
    });
  }

  $scope.addRow_tagTable=function(data){
    let h=data.points[0].customdata[1];
    addRow_tagTable(h);
    $scope.update_refl();
    // $log.log($scope.expand)
    $scope.expand['refl']=true;
    // $log.log($scope.expand)
  }

  $scope.leg_click=function(event){
    var curve_nb=event.curveNumber;
    if ( !(curve_nb<$scope.rings[0])){
      curve_nb=$scope.rings[0];
    }
    let dat = event.data[curve_nb];
    if (dat.visible==true){
      var visible='legendonly';
    }
    else{
      var visible=true;
    }
    $scope.set_visible(dat.name,curve_nb,visible);
    return false;
  }

  $scope.set_visible=function(name,curve_nb,visible){
    if ( curve_nb<$scope.rings[0]){
      Plotly.restyle('fig1', {'visible':visible},[curve_nb]);
      $http.post('set_visible',JSON.stringify({'key':name,'v':visible}))
      .then(function(response){
        // $log.log(response.data);
      });
    }
    else{
      Plotly.restyle('fig1', {'visible':visible},$scope.rings);
      $http.post('set_visible',JSON.stringify({'key':'rings','v':visible}))
      .then(function(response){
        // $log.log(response.data);
      });
    }
  }

  ///////////////////////////////////////////////////////////////////
  // uploads
  ///////////////////////////////////////////////////////////////////
  $scope.new_structure=function(){
    $http.post('new_structure',JSON.stringify({'name':name,'cif':'cif'}))
    .then(function(response){
      $scope.cif_file=response.data;
      // $log.log(response.data);
    });
  }

  $scope.set_structure=function(mol){
    $http.post('set_structure',JSON.stringify({'mol':mol}))
    .then(function(response){
      // $log.log(response.data);
      $scope.init()
    });
  }

  $scope.upload=function(val){
    // $log.log(val);
  }

  ///////////////////////////////////////////////////////////////////
  // Toggles
  ///////////////////////////////////////////////////////////////////
  $scope.set_mode=function(key){
    $http.post('set_mode',JSON.stringify({'key':key,'val':$scope.modes[key]}))
    // .then(function(response){
      //   $log.log(response.data);
      // });
    if (!$scope.modes['manual'] && key=='rock' ){
    }
    else{
      if  ($scope.graph==$scope.graphs['rock']){
        $scope.graph=$scope.graphs['thick'];
      }
      $scope.set_available_graphs('rock',false);
    }
  }

  $scope.toggle_mode=function(key){
    $scope.modes[key]=!$scope.modes[key];
    $scope.set_mode(key);
  }

  $scope.set_analysis_mode=function(val){
    $scope.modes['analysis']=val;
    $scope.set_mode('analysis',val);
    $scope.mode_style = {'bloch':'','frames':''};
    $scope.mode_style[val]=mode_style;
    if (changed){
      // $log.log('updating')
      $scope.update();
      changed=false;
    }
  }

  $scope.toggle_manual_mode=function(){
    $scope.toggle_mode('manual');
    if (!$scope.modes['manual']){
      $scope.update();
    }
  }

  var timer;
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

  $scope.set_input=function(key,v){
    $scope.input[key]=false;
    switch(v){
      case 'move':
        $scope.update_theta_phi();
        break;
      case 'rock':
        $scope.get_rock_sim();
        break;
    }
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
    $scope.bloch_solve_reset();
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
  // Bloch
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update_bloch=function(){
    // $log.log($scope.bloch['Smax'],$scope.bloch['Nmax'])
    if ($scope.bloch_solve_btn=='Solve'){
        $scope.bloch_solve_set('Preparing');
        $http.post('bloch_u',JSON.stringify({'frame':$scope.frame,'bloch':$scope.bloch,'manual_mode':$scope.modes['manual']}))
        .then(function(response){
          $scope.load_bloch(response.data);
          // FELIX
          if ($scope.bloch['felix']){
            var interval;
            interval = $interval(function () {
              $http.get('bloch_state')
              .then(function(response) {
                $scope.bloch_solve_set(response.data);
              });
            }, 250);
            $http.post('solve_bloch')
            .then(function(response){
              $log.log('completed');
              $scope.fig1 = response.data;//JSON.parse(response.data.fig);
              $scope.update_graph();
              $scope.bloch_solve_set('Completed');
              $interval.cancel(interval);
            })
            // $interval.cancel(interval);
          }
          // BLOCHWAVE
          else{
            if (response.data.nbeams>1000){
              $log.log('too many beams sorry');
              $scope.bloch_solve_set('Solve');
            }
            else{
              $scope.bloch_solve_set('Solving');
              $http.post('solve_bloch',JSON.stringify())
              .then(function(response){
                $scope.fig1 = response.data;//JSON.parse(response.data.fig);
                $scope.update_graph();
                $scope.bloch_solve_set('Completed');
              });
            }
          }
        });
        $scope.expand['thick']=true
    }
  };

  // $scope.solve_bloch=function(){
  //   $http.post('solve_bloch',JSON.stringify())
  //   .then(function(response){
  //     $scope.fig1 = response.data;//JSON.parse(response.data.fig);
  //     $scope.update_graph();
  //     $scope.bloch_solve_set('Completed');
  //   });
  // }

  $scope.bloch_solve_set=function(state){
    $scope.bloch_solve_btn=state;
    c = 'red'
    if (state in bloch_colors){
      c = bloch_colors[state]
    }
    $scope.bloch_solve_style={'background-color':c};
  }
  $scope.bloch_solve_reset=function(){
    $scope.bloch_solve_set('Solve');
  }

  $scope.load_bloch = function (data){
    $scope.fig1 = JSON.parse(data.fig);
    $scope.bloch     = data.bloch;
    $scope.rings     = data.rings;
    $scope.nbeams    = data.nbeams;
    $scope.theta_phi = data.theta_phi.split(',');
    // $log.log($scope.rings)
  }

  $scope.show_u=function(){
    $scope.graph=$scope.graphs['u3d']
    $scope.modes['single']=false;
    $http.post('show_u',JSON.stringify({'rock':$scope.rock,'u':$scope.bloch['u']}))
      .then(function(response){
        $scope.fig2 = response.data;
        // $log.log()
    });
  }

  $scope.show_scat=function(){
    $scope.graph=$scope.graphs['scat']
    $scope.modes['single']=false;
    $http.post('show_sf')
      .then(function(response){
        $scope.fig2 = response.data;
        // $log.log()
    });
  }

  $scope.set_u_mode=function(val){
    $scope.modes['u']=val;
    $scope.set_mode('u');
    $scope.u_style = {'edit':'','move':'','rock':''};
    $scope.u_style[val]={"border-style":'solid'};
    switch (val){
    //   case 'edit':
    //     break;
      // case 'move':
        // break;
      case 'rock':
        // $log.log($scope.rock_state=='done');
        $scope.set_available_graphs('rock',$scope.rock_state=='done');
        break;
    }
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Rock mode
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.set_rock=function(opt){
    // $log.log(opt);
    $http.post('set_rock_frame',JSON.stringify({'frame':$scope.frame,'opt':opt}))
    .then(function(response){
      $scope.rock = response.data.rock;
      $scope.rock_reset();
    })
  }

  $scope.solve_rock=function(){
    $log.log($scope.solve_rock_btn,$scope.rock_state)
    if ($scope.solve_rock_btn=='Solve rock'){
    // if ($scope.solve_rock_btn[$scope.rock_state]=='Solve rock'){
      $http.post('set_rock',JSON.stringify({'rock':$scope.rock,'bloch':$scope.bloch}))
      .then(function(response){
        $scope.rock = response.data.rock;
        $scope.rock_state='init';
        $scope.solve_rock_btn=$scope.rock_state;
        $scope.rock_style={'background-color':'red'};
        var interval;
        interval = $interval(function () {
          $http.get('rock_state')
          .then(function(response) {
            $scope.rock_state = response.data;
            $scope.solve_rock_btn=$scope.rock_state;
            $log.log($scope.rock_state);
          });
        }, 100);
        $http.post('solve_rock')
        .then(function(response){
          $scope.nrock_beams = response.data.nbeams;
          $scope.rock_style = {'background-color':'green'};
          $scope.rock_state = 'done';
          $scope.solve_rock_btn = 'done';
          $scope.set_available_graphs('rock',true);
          $scope.set_rock_sim(1);
          $log.log('completed');
          $interval.cancel(interval);
          // $scope.rock_state = 'done';
          // $scope.solve_rock_btn = 'done';
        })
      })
      $scope.rock_state = 'done';
      $scope.solve_rock_btn = 'done';
    }
  }

  $scope.show_rock=function(){
    $scope.modes['single']=false;
    $scope.update_refl();
    $scope.graph=$scope.graphs['rock']
    $http.post('show_rock',JSON.stringify({'refl':$scope.refl}))
      .then(function(response){
        $scope.fig2 = response.data;
    });
  }

  $scope.update_rock_sim=function(e){
    s=''
    switch (e.keyCode){
      case 37: s='-';break;
      case 39: s='+';break;
      case 38: s='f';break;
      case 40: s='i';break;
    }
    if (s){
      // $log.log(s);
      $scope.set_rock_sim(s);}
  }

  $scope.set_rock_sim=function(s){
    switch (s){
      case 'i':$scope.rock_sim  = 1;break;
      case '-':$scope.rock_sim -= 1;break;
      case '+':$scope.rock_sim += 1;break;
      case 'f':$scope.rock_sim  = 100;break;
    }
    $scope.get_rock_sim();
  }

  $scope.get_rock_sim=function(){
    $http.post('get_rock_sim',JSON.stringify({'sim':Number($scope.rock_sim),'frame':$scope.frame}))
      .then(function(response){
        $scope.fig1 = JSON.parse(response.data.fig);
        $scope.rock_sim = response.data.sim;
        $scope.sim_rock = $scope.rock_sim;
        $scope.update_graph();
    });
  }
  $scope.all_rock_sim=function(){
    $http.post('overlay_rock')
    .then(function(response){
      $scope.fig1 = response.data;
      $scope.sim_rock = 'all';
    });
  }

  $scope.rock_reset=function(){
    $scope.solve_rock_btn='Solve rock';
    // $log.log($scope.rock_state);
    $scope.rock_style={'background-color':'#286090'};
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Rotate mode
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.theta_phi_cb=function(e){
    $scope.bloch_solve_reset()
    var updated = false;
    var theta_phi=[Number($scope.theta_phi[0]),Number($scope.theta_phi[1])];
    $scope.dtheta_phi=Number($scope.dtheta_phi);
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
      $scope.theta_phi=theta_phi;
      $scope.update_theta_phi();
    }
  }
  $scope.update_theta_phi=function(){
    $scope.theta_phi[0]%=180;
    $scope.theta_phi[1]%=360;
    $http.post('bloch_rotation',JSON.stringify({'theta_phi':$scope.theta_phi}))
      .then(function(response){
        $scope.load_bloch(response.data);
      });
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Thickness
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update_thickness = function (e) {
    var updated=false;
    switch (e.keyCode) {
        case 37:
          $scope.bloch['thick']-=10*$scope.dthick;
          updated=true;
          break;
        case 38:
          $scope.bloch['thick']+=$scope.dthick;
          updated=true;
          break;
        case 39:
          $scope.bloch['thick']+=10*$scope.dthick;
          updated=true;
          break;
        case 40:
          $scope.bloch['thick']-=$scope.dthick;
          updated=true;
          break;
        case 34:
          $scope.dthick+=1;
          break;
        case 33:
          $scope.dthick-=1;
          break;
        case 8:
          $scope.dthick=5;
          break;
        case 13:
          updated=true;
          break;
    }
    if (updated){
      $http.post('update_thickness',JSON.stringify({'thick':$scope.bloch['thick']}))
      .then(function(response){
        $scope.fig1 = response.data;
        if ($scope.modes['u']=='rock'){
          $scope.show_rock();
        }
      });
    }
  }

  $scope.beam_vs_thickness = function () {
    $scope.update_refl();
    $scope.graph=$scope.graphs['thick']
    $http.post('beam_vs_thick',JSON.stringify({'thicks':$scope.bloch['thicks'],'refl':$scope.refl}))
      .then(function(response){
        $scope.modes['single']=false;
        $scope.fig2 = response.data;
    });
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // misc stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.toggle_felix=function(){
    $scope.bloch_solve_reset()
  }

  $scope.update_omega=function (e) {
    if (event.key=='Enter') {
      $http.post('update_omega',JSON.stringify({'omega':$scope.omega}))
      .then(function(response){
        $scope.fig1 = response.data;
      })
    }
  }

  $scope.update=function(){
    // return new Promise(function(resolve, reject){
    switch ($scope.modes['analysis']){
      case 'bloch':
        if ( ! ($scope.modes['manual'] && $scope.modes['u']=='rock')){
          $scope.update_bloch();
        }
        else{
          $scope.get_rock_sim();
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

  $scope.update_graph=function(){
    // $log.log($scope.graph);
    if (!$scope.modes['single']){
      switch ($scope.graph.type){
        case 'thick':
          $scope.beam_vs_thickness();
          break;
        case 'rock':
          $scope.show_rock();
          break;
        case '3d':
          $scope.show_u();
          break;
        case 'scat':
          $scope.show_scat();
          break;
        default :
          $scope.graph = $scope.graphs['thick'];
          $scope.beam_vs_thickness();
          break;
      }
    }
  }

  $scope.set_available_graphs = function(key,val){
    if(val){
      $scope.graphs[key]=JSON.parse(JSON.stringify($scope.all_graphs[key]));
    }
    else{
      delete $scope.graphs[key];
    }
    // $log.log($scope.all_graphs);
  }

  $scope.set_fig1 = function(){
    $http.post('set_fig1',JSON.stringify({'max_res':$scope.max_res,'dq_ring':$scope.dq_ring}))
      .then(function(response){
        $scope.fig1 = response.data;
      });
  }
  $scope.set_max_res=function(){
    $scope.set_fig1();
    if ($scope.graph.type=='scat' && !$scope.modes['single']){
      $scope.show_scat();
    }
  }
  $scope.set_ring_spacing=function(){
    $scope.set_fig1();
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
        $scope.max_frame = response.data.max_frame;
        $scope.zmax      = response.data.zmax;
        $scope.crys      = response.data.crys;
        $scope.cif_file  = response.data.cif_file;
        $scope.bloch     = response.data.bloch;
        $scope.modes     = response.data.modes;
        $scope.rock      = response.data.rock;
        $scope.theta_phi = response.data.theta_phi.split(',');
        $scope.omega     = response.data.omega;
        $scope.expand    = response.data.expand;
        $scope.rock_state= response.data.rock_state;
        $scope.set_available_graphs('rock',$scope.rock_state=='done');
        $scope.graph = $scope.graphs[response.data.graph];
        $scope.u_style[$scope.modes['u']]={"border-style":'solid'};
        $scope.mode_style[$scope.modes['analysis']]=mode_style;
        $scope.max_res=response.data.max_res;
        $scope.dq_ring=response.data.dq_ring;
        $scope.rings=$scope.rings;
        var refl=response.data.refl;
        for (let h of refl){
          addRow_tagTable(h);
        }
        $scope.structures = response.data.structures;
        // $scope.gifs = response.data.gifs;
        $scope.bloch_solve_reset();

        $scope.update()
    });
  }

  var changed=true;
  $scope.fig1={};
  $scope.fig2={};
  // $scope.frame = 1;
  $scope.nbeams=0;
  $scope.nrock_beams=0;
  $scope.show_buttons=false;
  $scope.dtheta_phi=0.1;
  $scope.dthick=5;
  $scope.refl=[[0,0,0]];
  $scope.u_style = {'edit':'','move':'','rock':''};
  $scope.mode_style = {'bloch':'','frames':''};
  $scope.rock_style = '';
  $scope.solve_rock_btn='Solve rock';
  $scope.popup={}
  $scope.sim_rock = 1;
  $scope.rock_sim = 1;
  // $scope.rock_done = false;
  $scope.input={'theta':false,'phi':false,'dtp':false ,'rock_sim':true};
  $scope.structures = [];
  $scope.all_graphs={thick:{type:'thick',desc:'thickness'},
    u3d:{type:'3d',desc:'3d view'},rock:{type:'rock',desc:'rocking curve'},
    scat:{type:'scat',desc:'scattering factors'}}
  $scope.graphs=JSON.parse(JSON.stringify($scope.all_graphs));
  var mode_style = {"border-style":'solid','background-color':'#18327c'};
  var bloch_colors={'Solve':'#337ab7','Solving':'red','Completed':'green'}
  $scope.show={}

  // $scope.expand = {'omega':false,'thick':false,'refl':false,'sim':false,'u':true,}
  $scope.expand_str={false:'expand',true:'minimize'};
  $scope.init();

}]);
