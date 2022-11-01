$(document).ready(function(){
    //  tooltip
    $( '.content td[name="cheevodesc"]' ).tooltip({
       track:true,
       open: function( event, ui ) {
          var cheevodescid = $(this).attr('cheevo-descid');
          $.ajax({
              url:'/_cheevo_desc',
              type:'post',
              data:{cheevodescid},
              success: function(response){
                 $("#"+cheevodescid).tooltip('option','content',response);
              }
          });
       }
    });
  
    $('.content td[name="cheevodesc"]').mouseout(function(){
       // re-initializing tooltip
       $(this).attr('title','Please wait...');
       $(this).tooltip();
       $('.ui-tooltip').hide();
    });

    $.ajax(
      // get manifest version
      {
         type: "POST",
         dataType: "text",
         url: "/_manifest_version",
         data: {},
         success: function(response) {
            document.getElementById("manifest_version").innerHTML = response;
         }
      }
   );

   $.ajax(
      // get our last modified times
      {
         type: "POST",
         dataType: "text",
         url: "/_modified_time",
         data: {filename:"clan_data.sqlite3"},
         success: function(response) {
            document.getElementById("clan_data_modified").innerHTML = response;
         }
      }
   );
   $.ajax(
      {
         type: "POST",
         dataType: "text",
         url: "/_modified_time",
         data: {filename:"version.txt"},
         success: function(response) {
            document.getElementById("manifest_modified").innerHTML = response;
         }
      }
   );
    
});

function getComplete(elementid, playerid, cheevoid) {
   // ajax to find out if specific player/cheevo is complete
   elementid = elementid;
   $.ajax(
      {
         type: "POST",
         dataType: "text",
         url: "/_is_complete",
         data: {playerid, cheevoid},
         success: function(response) {
            document.getElementById(elementid).innerHTML = response;
            if (response == "Done"){
               $('#row' +cheevoid).attr( 'hideable','true');
            } else {
               $('#row' +cheevoid).attr( 'hideable','false');
            }
         }
      }
   );
}

function hideRows() {
   // simple js toggle to hide rows
   $('[hideable="true"]').toggle(); 
}

function getAbout() {
   // set up the about dialog
   $( "#about" ).dialog({
      resizable: false,
      modal: true,
      width: 400,
      buttons: {
         Close: function() {
            $( this ).dialog( "close" );
         }
      }
   });
 }
