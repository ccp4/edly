///////////////////////////////////////
// Draw frame
///////////////////////////////////////
function draw_frame(frame_type,dats,wh){

  const canvas = document.getElementById("canvas_"+frame_type);
  canvas.width=wh;
  canvas.height=wh;
  const ctx = canvas.getContext("2d");
  // Initialize a new ImageData object
  let imageData = new ImageData(dats, wh);
  // Draw image data to the canvas
  ctx.putImageData(imageData, 0, 0);
  // console.log('all drawn');
}


///////////////////////////////////////
// reflection table
///////////////////////////////////////
function addRow_tagTable(miller_indices) {
  var TABLE_MILLER=document.getElementById('table_Miller_indices')
    if (!extract_list_indices_from_table().includes(miller_indices)) {
      var row = TABLE_MILLER.insertRow(TABLE_MILLER.rows.length);
      row.insertCell(0).innerHTML= '<div class="btn btn-delete btn-primary" onclick="deleteRow(this)" > <span class="glyphicon glyphicon-remove" /></div>';
      // console.log(miller_indices)
      row.insertCell(1).innerHTML= `<div onmouseover="highlight('${miller_indices}',true)" onmouseout="highlight('${miller_indices}',false)" style="padding:2px;margin:0">${miller_indices}</div>`;
  }
}
function extract_list_indices_from_table() {
  var TABLE_MILLER=document.getElementById('table_Miller_indices')
  let listTags=[]
  let listrows= TABLE_MILLER.children[0].children
  for (let row of listrows) {
    // console.log(row.cells[1].children[0]);
    listTags.push(row.cells[1].children[0].innerHTML)
  }
  return listTags.slice(1,)
}

function deleteRow(obj) {
  var TABLE_MILLER=document.getElementById('table_Miller_indices')
    var index = obj.parentNode.parentNode.rowIndex;
    TABLE_MILLER.deleteRow(index);

    var element = angular.element(document.getElementById('clear_btn'));
    element.scope().update_refl();
}
function clearTable(){
  var TABLE_MILLER=document.getElementById('table_Miller_indices')
  let listrows= TABLE_MILLER.children[0].children
  // console.log('clear table',listrows.length);
  for (let i=listrows.length-1;i>0;i--) {
    // console.log(i,listrows[i].cells[1].children[0].innerHTML);
    TABLE_MILLER.deleteRow(i);
  }
}

// function hover row point table miller
function highlight(miller_indices,val){

  var found = false;
  var data  = document.getElementById('fig1').data[0].customdata;
  var idx = 0;
  while (!found && idx<data.length){
    found = data[idx][1]==miller_indices;
    idx++;
  }
  if (found){
    if (val){
      found=false;
      var c_nb=0;
      while (!found && c_nb<3){
        found=document.getElementById('fig1').data[c_nb].visible==true;
        c_nb++;
      }
      if (found){
        // console.log(idx);// data[idx][1], miller_indices)
        Plotly.Fx.hover('fig1',[
          { curveNumber:c_nb-1, pointNumber:idx-1 },
        ]);
      }
    }
    else{
      Plotly.Fx.unhover('fig1',[]);
    }
  }
}


///////////////////////////////////////
// help gif
///////////////////////////////////////
var gif_dialog;
$(document).ready(function(){
  gif_dialog = $( "#dialog-gif" ).dialog({
    autoOpen: false,
    height: 980,
    width: 1600,
    modal: true,
    buttons: {
      Cancel: function() {
        gif_dialog.dialog( "close" );
      },
    },
    close: function() {
    }
  });
});

function open_gif_dialog(elt,tle,gif){
  // console.log(tle,gif);
  $('#dialog-gif')[0].innerHTML=`<h2>${tle}</h2> <a href="/${gif}" > <img style="border:solid" src="/${gif}"  /></a>`
  gif_dialog.dialog( "open" );
};



///////////////////////////////////////
// Structure stuffs
///////////////////////////////////////
function set_structure(mol){
  console.log(mol)
  // var formData = {'mol':mol}
  $.ajax({
    type:'POST',
    url:'set_structure',
    data:{'mol':mol},
    success: function(data){
       dialog.dialog( "close" );
       window.location='viewer'
    }
  });
};


function upload_file(file_type){
  var files = $('#input_'+file_type+'_file')[0].files;
  elt = $('#input_'+file_type+'_file')[0]
  scope = angular.element(elt).scope()
  if (files.length>0) {
    var file = files[0];
    extension = file.name.split('.').pop();
    // console.log(extension);
    if (file_type=='cif' && extension!='cif'){
      scope.show_error('upload a '+file_type+' file thank you',1);return
    }
    else{
      // console.log(file.size);
      if (file_type=='cif' && file.size > 10000*1024) {
        scope.show_error('max upload size is 10Mo',1);return
      }
      else{
        var form = $('#form_'+file_type)[0];
        // console.log(files,form);
        $.ajax({
         url: 'upload_file',
         type: 'POST',
         // data: {'name':file.name},
         data: new FormData(form),
         cache: false,
         contentType: false,
         processData: false,
         success: function(data){
           if (file_type=='cif'){
             scope.show_error(data,data!='ok')
           }
           else if (file_type =='dat'){
             scope.check_dat();
           }
           else if (file_type =='Cif'){
             scope.check_cif();
           }
         },
       });
     }
   }
  }
}


function open_link(link){
  // console.log(link);
  window.open(link)
};


function open_file(link){
  window.open(link);
}

///////////////////////////////////////
// Mathjax
///////////////////////////////////////
function update_formula(formula){
  // window.MathJax = {
  //   startup: {
  //     ready: () => {
  //       console.log('MathJax is loaded, but not yet initialized');
  //       MathJax.startup.defaultReady();
  //       console.log('MathJax is initialized, and the initial typeset is queued');
  //     }
  //   }
  // };
  var math = MathJax.Hub.getAllJax("formula")[0];

  if (math){
    MathJax.Hub.Queue(["Text",math,formula]);
  }
  else{
    console.log('mathjax not init')    
  }
}

function get_input_value(id){
  return $('#'+id)[0].value;
}
function get_file_name(id){
  return $('#input_'+id+'_file')[0].files[0].name;
}
function clear_files(id){
  return $('#input_'+id+'_file')[0].value="";
}

function show_popup(elt){
  popup=document.getElementById(elt)
  popup.style.display="block";
  window.setTimeout(function(){
    popup.style.display = "none";
  }, 2000);
}
function focus(elt){
  // console.log('focus',elt);
  document.getElementById(elt).focus();
}
