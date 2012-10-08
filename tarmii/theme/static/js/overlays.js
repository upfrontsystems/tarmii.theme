$(function($) {
    var url = location.href;

    $('#add-resource-form input').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name=form.buttons.cancel]'
        });

});
