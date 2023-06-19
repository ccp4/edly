// var dialog, form;

$(document).ready(function(){
// elt=$( "#dialog" )[0]
// console.log(elt)
// scope=angular.element(elt).scope;
// dialog = elt.dialog({
//   autoOpen: false,
//   height: 500,
//   width: 400,
//   modal: true,
//   buttons: {
//     "create ": scope.new_structure,
//     Cancel: function() {
//       dialog.dialog( "close" );
//     },
//   },
//   // close: function() {
//   //   form[ 0 ].reset();
//   //   $('#cif_error').hide()
//   //   // allFields.removeClass( "ui-state-error" );
//   // }
});



// form = dialog.find( "form" ).on( "submit", function( event ) {
//   event.preventDefault();
//   scope.new_structure();
// });

function dialog_new_structure(){
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
      console.log('closing new project form');
      // form[ 0 ].reset();
      // $('#cif_error').hide()
      // allFields.removeClass( "ui-state-error" );
    }
  })

  $( "#dialog" ).dialog( "open" );
};

function new_structure(){
  elt=$( "#dialog" )[0];
  // console.log(elt);
  angular.element(elt).scope().new_structure();
}

function close_dialog(){
  $( "#dialog" ).dialog( "close" );
}
