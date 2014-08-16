django.jQuery(function(){

    var types_arr = ["country", "administrative_area_level_1",
                     "administrative_area_level_2",
                     "administrative_area_level_3",
                     "locality", "sublocality"]
    types_arr.forEach(function(geotype){
        $(".field-"+geotype).children("input").attr("readonly","readonly");
    }); 
    $("#id_address").on('gmaps-click-on-marker', function(e, data){
        /*clean previous types */
        types_arr.forEach(function(geotype){
            $(".field-"+geotype).children("input").val("");
        }); 
        data.address_components.forEach(function(add_comp){
            var use_this = false;
            add_comp.types.forEach(function(tp){
                if(django.jQuery.inArray(tp, types_arr) != -1){
                    use_this = tp; 
                }   
            }); 
            if(use_this){
                $(".field-"+use_this).children("input").val(add_comp.long_name);
            }   
        }); 

    }); 

});
