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
  

});

function getComplete(elementid, playerid, cheevoid) {
   elementid = elementid;
   $.ajax(
      {
         type: "POST",
         dataType: "text",
         url: "/_is_complete",
         data: {playerid, cheevoid},
         success: function(response) {
               document.getElementById(elementid).innerHTML = response;   
         }
      }
   );     
}
