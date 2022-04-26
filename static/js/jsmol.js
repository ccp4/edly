var myJmol = 'myJmol';
var JmolInfo = {
  color: "#FFFFFF", // white background (note this changes legacy default which was black)
  height: 500,      // pixels (but it may be in percent, like "100%")
  width: "95%",
  use: "HTML5",     // "HTML5" or "Java" (case-insensitive)
  j2sPath: "/static/jmol/jsmol/j2s",          // only used in the HTML5 modality
  // j2sPath: "/static/bower_components/jsmol/src/j2s",          // only used in the HTML5 modality
  src: '/static/data/test/alpha_glycine.cif',          // file to load
  // src: '{a cif a}',          // file to load
};
Jmol.setXHTML('myJmol');
Jmol.getApplet("myJmol",JmolInfo);
// jmolApplet(400,"myJmol","0");
// var cif='/static/data/test/pets/1ejg.pdb';
// load_cif(0);
// var
// function load_cif(val){
//   if (val==0){
//     var cif='/static/data/test/pets/1ejg.pdb'
//   }
//   else{
//     var cif=document.getElementById("cif_file").innerHTML;
//   }
//   console.log(cif);
//   $('#myJmol').html( Jmol.getAppletHtml(myJmol, JmolInfo) )
//   Jmol.script(myJmol, 'load cif')
// }
