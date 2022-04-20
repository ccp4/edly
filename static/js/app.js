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
            // console.log("here");
            // console.log(element[0].id);
            scope.initPlotly=true
            document.getElementById(element[0].id).on('plotly_click', scope.addRow_tagTable);
            document.getElementById(element[0].id).on('plotly_legendclick', scope.leg_click);
            // document.getElementById(element[0].id).on('plotly_click', function(data){
            // console.log(data.points);
            // let datapts=data.points[0]
            // addRow_tagTable(datapts.customdata)
            // console.log(element[0].id);
          // })
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
      if (event.which === 13) {
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



app.controller('viewer', ['$scope','$rootScope','$log','$http', '$interval', function ($scope,$rootScope,$log,$http,$interval) {

  /////////////////////////////////
  //// plotly cb
  /////////////////////////////////
  $scope.update_refl = function(){
    $scope.refl = extract_list_indices_from_table();
  }
  $scope.addRow_tagTable=function(data){
    let h=data.points[0].customdata[1];
    addRow_tagTable(h);
  }

  $scope.leg_click=function(data){
    let dat = data.data[data.curveNumber];
    if (dat.visible==true){
      var update={'visible':'legendonly'};
    }
    else{
      var update={'visible':true};
    }
    $http.post('/set_visible',JSON.stringify({'key':dat.name,'v':update.visible}))
    .then(function(response){
      // $log.log(response.data);
      Plotly.restyle('fig1', update,[data.curveNumber]);
    });
    return false;
  }

  ///////////////////////////////////////////////////////////////////
  // uploads
  ///////////////////////////////////////////////////////////////////
  $scope.initPlotly=false
  $scope.set_structure=function(){
    $http.post('/set_structure',JSON.stringify({'cif':$scope.crys['file']}))
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
  $scope.set_mode=function(key){
    $http.post('/set_mode',JSON.stringify({'key':key,'val':$scope.modes[key]}))
    // .then(function(response){
    //   $log.log(response.data);
    // });
  }

  $scope.toggle_mode=function(key){
    $scope.modes[key]=!$scope.modes[key];
    $scope.set_mode(key);
  }

  $scope.toggle_analysis_mode=function(){
    $scope.toggle_mode('analysis');
    $scope.update()
  }

  $scope.toggle_manual_mode=function(){
    $scope.toggle_mode('manual');
    if (!$scope.modes['manual']){
      $scope.update();
    }
    else{

    }
  }

  $scope.toggle_popup=function(key){
    $scope.popup[key]=!$scope.popup[key];
  }

  $scope.set_input=function(key){
    $scope.input[key]=false;
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
      $scope.frame=Math.max(1,Math.min($scope.frame,$scope.max_frame));
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
        // $log.log($scope.bloch['u'])
        if (!$scope.modes['single']){
          $scope.beam_vs_thickness()
        }
    });
  };

  $scope.load_bloch = function (data){
    $scope.fig1      = JSON.parse(data.fig);
    $scope.bloch     = data.bloch;
    $scope.nbeams    = data.nbeams;
    $scope.theta_phi = data.theta_phi.split(',');
  }


  $scope.show_u=function(){
    $http.post('/show_u',JSON.stringify({'rock':$scope.rock,'u':$scope.bloch['u']}))
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
    // switch (val){
    //   case 'edit':
    //     break;
    //   case 'move':
    //     break;
    //   case 'rock':
    //     break;
    // }
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Rock mode
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.set_rock=function(){
    $http.post('/set_rock_frame',JSON.stringify({'frame':$scope.frame}))
    .then(function(response){
      $scope.rock = response.data.rock;
      $scope.rock_reset();
    })
  }

  $scope.solve_rock=function(){
    if ($scope.solve_rock_btn=='Solve rock'){
      $http.post('/set_rock',JSON.stringify({'rock':$scope.rock,'bloch':$scope.bloch}))
      .then(function(response){
        $scope.rock = response.data.rock;
        $scope.rock_state='init';
        $scope.solve_rock_btn=$scope.rock_state;
        $scope.rock_style={'background-color':'red'};
        var interval;
        interval = $interval(function () {
          $http.get('/rock_state')
          .then(function(response) {
            $scope.rock_state = response.data;
            $scope.solve_rock_btn=$scope.rock_state;
            $log.log($scope.rock_state);
          });
        }, 100);
        $http.post('/solve_rock')
        .then(function(response){
          $interval.cancel(interval);
          $scope.nrock_beams = response.data.nbeams;
          $scope.rock_style = {'background-color':'green'};
          $scope.rock_state = 'done';
          $scope.solve_rock_btn=$scope.rock_state;
          $scope.set_rock_sim(1);
        })
      })
    }
  }

  $scope.show_rock=function(){
    $scope.update_refl();
    $http.post('/show_rock',JSON.stringify({'refl':$scope.refl}))
      .then(function(response){
        $scope.fig2 = response.data;
    });
  }

  $scope.set_rock_sim=function(s){
    switch (s){
      case 'i':$scope.rock_sim  = 1;break;
      case '-':$scope.rock_sim -= 1;break;
      case '+':$scope.rock_sim += 1;break;
      case 'f':$scope.rock_sim  = 100;break;
    }
    $log.log($scope.rock_sim);
    // $scope.rock_sim=Math.max(Math.min($scope.rock_sim,$scope.rock['npts']),1)
    $http.post('/get_rock_sim',JSON.stringify({'sim':$scope.rock_sim}))
      .then(function(response){
        $scope.fig1 = JSON.parse(response.data.fig);
        $scope.rock_sim = response.data.sim;
        $scope.sim_rock = $scope.rock_sim;
    });
  }
  $scope.all_rock_sim=function(){
    $http.post('/overlay_rock')
    .then(function(response){
      $scope.fig1 = response.data;
      $scope.sim_rock = 'all';
    });
  }

  $scope.rock_reset=function(){
    $scope.solve_rock_btn='Solve rock';
    $scope.rock_style={'background-color':'#286090'};
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // Rotate mode
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update_theta_phi=function(e){
    // $log.log(e.keyCode);
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
      theta_phi[0]%=180;
      theta_phi[1]%=360;
      // $log.log(theta_phi);
      $http.post('/bloch_rotation',JSON.stringify({'theta_phi':theta_phi}))
        .then(function(response){
          $scope.load_bloch(response.data);
        });
    }
  }

  $scope.update_omega = function (e) {
    if (event.key=='Enter') {
      $http.post('/update_omega',JSON.stringify({'omega':$scope.omega}))
      .then(function(response){
        $scope.fig1 = response.data;
      })
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
        $scope.fig1 = response.data;
      });
    }
  }

  $scope.update_beam_vs_thickness = function (event) {
    if (event.key=='Enter'){
      $scope.beam_vs_thickness()
    }
  }

  $scope.beam_vs_thickness = function () {
    $scope.update_refl();
    $http.post('/beam_vs_thick',JSON.stringify({'thicks':$scope.bloch['thicks'],'refl':$scope.refl}))
      .then(function(response){
        $scope.modes['single']=false;
        $scope.fig2 = response.data;
    });
  }


  ////////////////////////////////////////////////////////////////////////////////////////////////
  // misc/init stuffs
  ////////////////////////////////////////////////////////////////////////////////////////////////
  $scope.update = function(){
    if ($scope.modes['analysis']){
      if ( ! ($scope.modes['manual'] && $scope.modes['u']=='rock')){
        $scope.update_bloch();
      }
    }
    else{
      $scope.update_img();
    }
  }



  // $scope.popup={'pets':false,'mol':false,'exp':false,'sim':false,'ana':false,
  //   'keV':false, 'u':false,'Smax':false, 'Nmax':false,'thicks':false,'thick':false,
  //   'nbms':false};

  $scope.fig1={};
  $scope.fig2={};
  $scope.nbeams=0;
  $scope.nrock_beams=0;
  $scope.show_buttons=false;
  $scope.dtheta_phi=0.1;
  $scope.dthick=5;
  $scope.refl=[[0,0,0]];
  $scope.u_style = {'edit':'','move':'','rock':''};
  $scope.rock_style = '';
  $scope.rock_state='';
  $scope.solve_rock_btn='Solve rock'
  $scope.popup={}
  $scope.sim_rock = 1;
  $scope.rock_sim = 1;
  $scope.input={'theta':false,'phi':false,'dtp':false};

  $scope.expand = {'omega':false,'thick':false,'refl':false,'sim':false,'u':true,}
  $scope.expand_str={false:'expand',true:'minimize'};
  $http.get('/init')
    .then(function(response){
      $scope.structure = response.data.mol;
      $scope.frame     = response.data.frame;
      $scope.max_frame = response.data.max_frame;
      $scope.zmax      = response.data.zmax;
      $scope.bloch     = response.data.bloch;
      $scope.crys      = response.data.crys;
      $scope.cif_file  = response.data.cif_file;
      $scope.modes     = response.data.modes;
      $scope.rock      = response.data.rock;
      $scope.theta_phi = response.data.theta_phi.split(',');
      $scope.omega     = response.data.omega;
      // $scope.expand    = response.data.expand;
      $scope.u_style[$scope.modes['u']]={"border-style":'solid'};
      $scope.update()
    });


}]);
