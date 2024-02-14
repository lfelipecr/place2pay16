odoo.define('module.placetopay', function(require) 
{
    "use strict";
    
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var param_partner_id = null
    var name_address = "";
    var firstName = "";
    var lastName = "";
    var location_first_time = 'yes';

    $(document).ready(function() 
    {
        var url_string = window.location.href;
        var url = new URL(url_string);
        param_partner_id = url.searchParams.get("partner_id");

        // INIT PAYMENT ACQUIRER
        var default_button = $("form.o_payment_form").find("button#o_payment_form_pay");
        if ($("#payment_method").length > 0) {
            $("#o_payment_form_pay").after(function() {
                initPlaceToPayAcquirer();                              
            });
        }
        if ($(".placetopay-transaction").length > 0 && $("#portal_sale_content").length > 0) {
            $( ".placetopay-transaction" ).clone().appendTo( "#informations" ).find("row").last();     
            $( "#informations" ).find( ".placetopay-transaction" ).fadeIn();
        }
        if ($("img[alt='PlaceToPay']").length > 0) {
            
            $("img[alt='PlaceToPay']").attr('onclick', "window.open('//www.placetopay.com/web/', '_blank');");
            $(document).on("img[alt='PlaceToPay']", 'click', function()
            {
                window.location.href="//www.placetopay.com/web/";
            });
        }
        var intervalName = window.setInterval(function(){
            if($("form.checkout_autoformat").length>0)
            {
                name_address = $("input[name='name']").val();
                firstName = $("input[name='firstname']").val();
                lastName = $("input[name='lastname']").val();
            }
            clearInterval(intervalName);
        }, 500);
        
        

        // INIT PAYMENT REQUEST
        $("#o_payment_form_pay").on("click",function(event)
        {   
            event.preventDefault();
            var data_provider = $("input[name='pm_id']:checked").attr("data-provider");
            
            if(data_provider=="place2pay")
            {
                initPlaceToPayPaymentRequest();
            }
            else
            {
                $("form.o_payment_form").submit(); 
            }                  
        });

        if($("select#identification_id").length > 0)
        {
            if($("select#country_id").length > 0)
            {  
                window.setInterval(function(){
                    $("div.div_zip").find("label").removeAttr('required');
                }, 1);
                var country_id = $("select#country_id").val();  
                console.log(country_id);
                if(country_id>0)
                {}
                else
                {
                    $('select#country_id option:contains("Costa Rica")').attr('selected', true);
                    $('select#country_id option:contains("Costa Rica")').prop('selected', true);
                }
                getDocumentTypes();
                setDocumentType();
                setLocation('country_id');                                
            }
        }

        $("select#country_id").on("change", function()
        {
            getDocumentTypes();
            setLocation('country_id');
            location_first_time = 'no'
        });

        $("select[name='state_id']").on("change", function()
        {
            setLocation('state_id');
        });

        $("select[name='county_id']").on("change", function()
        {
            setLocation('county_id');
        });

        $("select[name='district_id']").on("change", function()
        {
            setLocation('district_id');
        });

        $("select#identification_id").on("change", function()
        {
            setDocumentType();
        });

        $("input[name='firstname']").on("blur", function()
        {
            updateFullName();
            $("input[name='name']").blur();
        });

        $("input[name='lastname']").on("blur", function()
        {
            updateFullName();
            $("input[name='name']").blur();
        });

        $("input[name='name']").on("blur", function()
        {
            var _name = $(this).val();   
            var first_Name = $("input[name='firstname']").val();
            var last_Name = $("input[name='lastname']").val();
            if(_name=="" || first_Name=="" || last_Name=="")
            {
                return false;
            }
            else{
                var expression_reg = /^[a-z\u00C0-\u02AB'´`]+\.?\s([a-z\u00C0-\u02AB'´`]+\.?\s?)+$/i;
                try
                {
                    if(expression_reg.exec(_name))
                    {}
                    else
                    {
                        Dialog.alert(null, "Nombre: No se aceptan carácteres extraños.", {"title":"PLACETOPAY"});
                        $("input[name='name']").val(name_address);
                        $("input[name='firstname']").val(firstName);
                        $("input[name='lastname']").val(lastName);
                        
                    }
                }
                catch (error)
                {
                    console.log(error);
                    Dialog.alert(null, error, {"title":"PLACETOPAY"});
                }
            }

            
        });

    });

    function updateFullName()
    {
        var firstname = $('input[name="firstname"]').val();
        var lastname = $('input[name="lastname"]').val();
        var fullname = String(firstname) + String(" ") + String(lastname);
        $('input[name="name"]').val(fullname);
    }

    function setLocation(from)
    {
        var _country_id = null;
        if(from=="country_id")
            _country_id = $("select[name=country_id]").val();

        var _state_id = null;
        if(from=="state_id")
        {
            _country_id = $("select[name=country_id]").val();
            _state_id = $("select[name=state_id]").val();
        }
            
        var _county_id = null;
        if(from=="county_id")
        {
            _country_id = $("select[name=country_id]").val();
            _state_id = $("select[name=state_id]").val();
            _county_id = $("select[name=county_id]").val();
        }
            
        var _district_id = null;
        if(from=="district_id")
        {
            _country_id = $("select[name=country_id]").val();
            _state_id = $("select[name=state_id]").val();
            _county_id = $("select[name=county_id]").val();
            _district_id = $("select[name=district_id]").val();
        }
            
        var _neighborhood_id = null;
        if(from=="neighborhood_id")
        {
            _country_id = $("select[name=country_id]").val();
            _state_id = $("select[name=state_id]").val();
            _county_id = $("select[name=county_id]").val();
            _district_id = $("select[name=district_id]").val();
            _neighborhood_id = $("select[name=neighborhood_id]").val();
        }            

        var _partner_id = $("input[name='partner_id']").val();

        var data = { "params": { 
                                    "partner_id":  _partner_id, 
                                    "country_id":  _country_id, 
                                    "state_id":    _state_id, 
                                    "county_id":   _county_id, 
                                    "district_id": _district_id,
                                    "neighborhood_id": _neighborhood_id,
                                    "from": from,
                                    "location_first_time":location_first_time
                                } 
                    }
            $.ajax({
                type: "POST",
                url: '/place2pay/set_partner_location',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) 
                {

                    var country_id = response.result.country_id;
                    var state_id = response.result.state_id;
                    var county_id = response.result.county_id;
                    var district_id = response.result.district_id;
                    var neighborhood_id = response.result.neighborhood_id;

                    var country = response.result.country;
                    var state = response.result.state;
                    var counties = response.result.counties;
                    var districts = response.result.districts;
                    var neighborhoods = response.result.neighborhoods;
                    
                    try 
                    {
                        var options = "";
                        counties.forEach(function(county, indice, counties) {
                            var county_id = String(county.id);
                            var county_name = String(county.name);
                            var option = "<option value='" + String(county_id) + "'>" + String(county_name) + "</option>";
                            options = String(options) + String(option);
                        });
                        $("select[name='county_id']").html(options);
                        try
                        {
                            if(_county_id>0)
                            {
                                $("select[name='county_id']").val(_county_id); 
                                var county_value =  $("select[name='county_id']").val(); 
                                if(county_value==null)
                                {$("select[name='county_id']").prop("selectedIndex", 0).val();}
                            }
                        }
                        catch (error)
                        {$("select[name='county_id']").prop("selectedIndex", 0).val();}  
                            
                    } catch (error)
                    {$("select[name='county_id']").prop("selectedIndex", 0).val();}  
                    
                    try 
                    {
                        var options = "";
                        districts.forEach(function(district, indice, districts) {
                            var district_id = String(district.id);
                            var district_name = String(district.name);
                            var option = "<option value='" + String(district_id) + "'>" + String(district_name) + "</option>";
                            options = String(options) + String(option);
                        });
                        $("select[name='district_id']").html(options);
                        try
                        {
                            if(_district_id>0)
                            {
                                $("select[name='district_id']").val(_district_id);
                                var district_value =  $("select[name='district_id']").val();
                                if(district_value==null)
                                {$("select[name='district_id']").prop("selectedIndex", 0).val();}

                            }
                        }
                        catch (error)
                        {$("select[name='district_id']").prop("selectedIndex", 0).val();} 
                    } catch (error)
                    {$("select[name='district_id']").prop("selectedIndex", 0).val();} 

                    try 
                    {
                        var options = "";
                        neighborhoods.forEach(function(neighborhood, indice, neighborhoods) {
                            var neighborhood_id = String(neighborhood.id);
                            var neighborhood_name = String(neighborhood.name);
                            var option = "<option value='" + String(neighborhood_id) + "'>" + String(neighborhood_name) + "</option>";
                            options = String(options) + String(option);
                        });
                        $("select[name='neighborhood_id']").html(options);
                        try
                        {
                            if(_neighborhood_id>0)
                            {
                                $("select[name='neighborhood_id']").val(_neighborhood_id); 
                                var neighborhood_value =  $("select[name='neighborhood_id']").val(); 
                                if(neighborhood_value==null)
                                {$("select[name='neighborhood_id']").prop("selectedIndex", 0).val();}
                            }
                        }
                        catch (error)
                        {$("select[name='neighborhood_id']").prop("selectedIndex", 0).val();} 
                    } catch (error)
                    {$("select[name='neighborhood_id']").prop("selectedIndex", 0).val();}

                    if(parseFloat(_partner_id) <= 0)
                    {
                                               
                    }
                    else
                    {
                        if(location_first_time == 'yes')
                        {
                            if(county_id!=false)
                                $("select[name='county_id']").val(county_id);
                            if(district_id!=false)
                                $("select[name='district_id']").val(district_id);
                            if(neighborhood_id!=false)
                                $("select[name='neighborhood_id']").val(neighborhood_id);
                        }
                    }
                    
                }
            }); 
    }

    function initLocation()
    {
        var _partner_id = $("input[name='partner_id']").val();
        
        var data = { "params": { 
                                    "partner_id":  _partner_id,
                                } 
                    }
            $.ajax({
                type: "POST",
                url: '/place2pay/init_partner_location',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) 
                {

                    var country_id = response.result.country_id;
                    var state_id = response.result.state_id;
                    var county_id = response.result.county_id;
                    var district_id = response.result.district_id;
                    var neighborhood_id = response.result.neighborhood_id;
                    
                    if(parseFloat(_partner_id) <= 0)
                    {
                                               
                    }
                    else
                    {
                        if(state_id!=false)
                            $("select[name='state_id']").val(state_id);
                        if(county_id!=false)
                            $("select[name='county_id']").val(county_id);
                        if(district_id!=false)
                            $("select[name='district_id']").val(district_id);
                        if(neighborhood_id!=false)
                            $("select[name='neighborhood_id']").val(neighborhood_id);
                    }
                    
                }
            }); 
    }

    function getDocumentTypes()
    {
        try
        {
            var country_id = $("select#country_id").val();
            var data = { "params": { "country_id": country_id } }
                $.ajax({
                    type: "POST",
                    url: '/place2pay/get_document_types',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function(response) 
                    {
                        try 
                        {
                            var documents_types = response.result.document_types;
                            var options = response.result.options;
                            $("select#identification_id").html(options);
                        } catch (error) 
                        {}                                      
                    }
                });
        }
        catch(e)
        {}
        
    }

    function setDocumentType()
    {
        var identification_id = $("select#identification_id");
        var code = $('option:selected', identification_id).attr('code');
        var data = { "params": { "code": code } }
            $.ajax({
                type: "POST",
                url: '/place2pay/set_document_type',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) 
                {}
            });
    }

    // INIT PAYMENT ACQUIRER
    function initPlaceToPayAcquirer()
    {
        var data = { "params": {  } }
            $.ajax({
                type: "POST",
                url: '/place2pay/get_acquirer',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) 
                {
                    console.log(response);
                    var acquirer = response.result.acquirer;
                    if(Boolean(acquirer.website_published))
                    {

                    }                    
                }
            });
    }

    // INIT PAYMENT REQUEST
    function initPlaceToPayPaymentRequest()
    {
        var partner_id = $(".o_payment_form").attr("data-partner-id");

        var online_payment = "no";
        if($("#quote_content").length>0)
        { 
            online_payment = "yes"; 
            partner_id = param_partner_id;
        }

        var data = { "params": { partner_id: partner_id, online_payment: online_payment }};

        $.ajax({
                    type: "POST",
                    url: "/place2pay/payment_request",
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function(response)
                    {
                        console.log(response);    
                        var result = response.result;
                        if(result.status=="FAIL")
                        {
                            var $message = $('<div/>').html(result.message);
                            $message.html($message.html());
                            $("button#o_payment_form_pay").removeAttr('disabled');
                            Dialog.alert(null, '', {"title":"PLACETOPAY", $content:$message});
                            
                        }
                        else
                        {
                            var $message = $('<div/>').html(result.message);
                            $message.html($message.html());
                            $("button#o_payment_form_pay").removeAttr('disabled');
                            Dialog.alert(null, '', {"title":"PLACETOPAY", $content:$message});
                            window.location.href = result.url;
                        }
                    }
                });
    }

});

