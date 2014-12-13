jQuery(function($){

    /* set array with geographic types to fill  */
    var types_arr = ["country", "administrative_area_level_1",
                     "administrative_area_level_2",
                     "administrative_area_level_3",
                     "administrative_area_level_4",
                     "administrative_area_level_5",
                     "locality", "sublocality", 'neighborhood',
                     "premise", "subpremise", "postal_code",
                     "natural_feature", "airport", "park",
                     "street_address", "route", "intersection"]
    var types_arr_reverse = Array.prototype.slice.call(types_arr);
    types_arr_reverse.reverse();

    /* set them readonly */
    types_arr.forEach(function(geotype){
        $("#id_"+geotype).attr("readonly","readonly");
    });

    $("#id_address").on('gmaps-click-on-marker', function(e, data){
        /*clean previous types */
        types_arr.forEach(function(geotype){
            $("#id_"+geotype).val("");
            $("#id_"+geotype).data('original', '');
        }); 
        data.address_components.forEach(function(add_comp){
            var use_this = false;
            add_comp.types.forEach(function(tp){
                if(jQuery.inArray(tp, types_arr) != -1){
                    use_this = tp; 
                }   
            }); 
            if(use_this){
                $("#id_"+use_this).val(add_comp.long_name);
                $("#id_"+use_this).data('original', add_comp.long_name);
            }   
        }); 
    }); 

    if($("#id_geo_type").length != 0){
        $("#id_geo_type").change(function(){
            var val_tp = $("#id_geo_type").val();
            var use_this = false
            types_arr_reverse.forEach(function(geotype){
                var curr_field = $("#id_"+geotype)
                if(val_tp == geotype || use_this){
                    use_this = true;
                    curr_field = $("#id_"+geotype)
                    curr_field.val(curr_field.data('original'));
                }else{
                    curr_field.val("");
                };
            });
        });
    }

});
