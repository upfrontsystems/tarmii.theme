$(function($) {
    var url = location.href;

    $('#add-button-form input').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'redirect',
        redirect: function (overlay, responseText) {
            var href = location.href;
            // look to see if there has been a server redirect
            var newTarget = $("<div>").html(responseText).find("base").attr("href"); 
            if ($.trim(newTarget) && newTarget !== location.href) { 
                return newTarget; 
            }
            // if not, simply reload
            return href;
        },
        //closeselector: '[name=form.buttons.cancel]'
        });

    $('a.add_to_assessment').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        //closeselector: '[name=form.buttons.cancel]'
        });

    $('a.edit_link').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        //closeselector: '[name=form.buttons.cancel]'
        });

});
