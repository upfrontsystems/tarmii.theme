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
        formselector: '#add-to-assessment-form',
        noform: 'close',
        closeselector: '[name="buttons.add.to.assessment.cancel"]',
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

// reports menu - show report images on hover
$(function() {
    $("a.class_performance_link").hover(
        function(){
            $("#class_performance_for_activity_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#class_performance_for_activity_graph").addClass("hidden");
        });
    $("a.class_progress_link").hover(
        function(){
            $("#class_progress_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#class_progress_graph").addClass("hidden");
        });
    $("a.learner_progress_link").hover(
        function(){
            $("#learner_progress_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#learner_progress_graph").addClass("hidden");
        });
    $("a.strengths_weaknesses_link").hover(
        function(){
            $("#strengths_weaknesses_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#strengths_weaknesses_graph").addClass("hidden");
        });
    $("a.evaluationsheet_link").hover(
        function(){
            $("#evaluationsheet_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#evaluationsheet_graph").addClass("hidden");
        });
    $("a.composite_learner_link").hover(
        function(){
            $("#composite_learner_graph.hidden").removeClass("hidden");
        },
        function(){
            $("#composite_learner_graph").addClass("hidden");
        });
});





