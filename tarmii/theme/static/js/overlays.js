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
        closeselector: '[name="form.button.Cancel"]',
        });

        $('a.add_to_assessment').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name="form.button.Cancel"]',
        });

    $('a.edit_link').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name="form.button.Cancel"]',
        });

    $('a.delete_confirmation').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name="form.button.Cancel"]',
        });

});

// disable multi submit on add forms (save button)
$(function() {
    $("#form-buttons-save").live("click", function() {
        $('.formControls').addClass('hidden');
    });
});
