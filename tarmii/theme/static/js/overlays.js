$(function($) {
    var url = location.href;

    $('#add-button-form input').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name=form.buttons.cancel]'
        });

    $('a.edit_link').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*',
        formselector: '#form',
        noform: 'reload',
        redirect: url,
        closeselector: '[name=form.buttons.cancel]'
        });

});
