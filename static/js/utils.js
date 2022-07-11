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
}

////// function hover row point table miller
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

var gif_dialog;
$(document).ready(function () {
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


var dialog, form;
$(document).ready(function () {

  dialog = $( "#dialog" ).dialog({
    autoOpen: false,
    height: 500,
    width: 400,
    modal: true,
    buttons: {
      "create ": new_structure,
      Cancel: function() {
        dialog.dialog( "close" );
      },
    },
    close: function() {
      form[ 0 ].reset();
      $('#cif_error').hide()
      // allFields.removeClass( "ui-state-error" );
    }
  });

  form = dialog.find( "form" ).on( "submit", function( event ) {
    event.preventDefault();
    new_structure();
  });


  function new_structure(){
  //   // e.preventDefault();
    var val='';
    if      ($('#radio_cif')[0].checked)  {val='cif'}
    else if ($('#radio_pdb')[0].checked)  {val='pdb'}
    else if ($('#radio_file')[0].checked) {val='file'}
    else{return};
    var formData = {
        'name':$('#name')[0].value,
        'cif':$('#cif')[0].value,
        'pdb':$('#pdb')[0].value,
        'file':$('#file_cif')[0].value.replace('C:\\fakepath\\',''),
        'val':val,
      };
    // console.log(formData);
    $.ajax({
      type:'POST',
      url:'new_structure',
      data:formData,
      success: function(data){
         // console.log(data);
         if (data=='ok'){
           dialog.dialog( "close" );
           window.location='viewer'
         }
         else{
           show_error(data,true)
         }
      }
    });
  };

});

function show_error(data,err){
  var msg='',color='green';
  if (err){
    msg='error : ';
    color='red'
  }
  $('#cif_error')[0].innerHTML=msg+data;
  $('#cif_error')[0].style.color=color;
  $('#cif_error').show()
}

// $(':file_cif').on('change', function () {
function upload_cif(){
  var files = $('#file_cif')[0].files;
  if (files.length>0) {
    var file = files[0];
    extension = file.name.split('.').pop();
    // console.log(extension);
    if (extension !='cif'){
      show_error('upload a cif file thank you',true);return
    }
    else{
      // console.log(file.size);
      if (file.size > 10000*1024) {
        show_error('max upload size is 10Mo',true);return
      }
      else{
        // console.log(file);
        $.ajax({
         url: 'upload_cif',
         type: 'POST',
         // data: {'name':file.name},
         data: new FormData($('form')[0]),
         cache: false,
         contentType: false,
         processData: false,
         success: function(data){
           if (data!='ok'){show_error(data,true)}
          else{show_error(data,false)}
         },
       });
     }
   }
  }
}
// });


function dialog_new_structure(){
  dialog.dialog( "open" );
};

function set_cif(){
  $('#cif_cif').hide()
  $('#cif_pdb').hide()
  $('#cif_file').hide()
  // $(`#cif_${id}`).show()
  if      ($('#radio_cif')[0].checked)  {$('#cif_cif').show()}
  else if ($('#radio_pdb')[0].checked)  {$('#cif_pdb').show()}
  else if ($('#radio_file')[0].checked) {$('#cif_file').show()}
};
set_cif();
// console.log(new FormData($('form')[0]));

function open_link(link){
  // console.log(link);
  window.open(link)
};
