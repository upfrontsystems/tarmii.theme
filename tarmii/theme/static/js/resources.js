$(function() {

    $(".resourcetree").each(function(index) {
        // get the content_node_uid
        var context_node_uid = $(this).attr('uid');
        var ajax_call = '@@gettreedata?context_node_uid=' + context_node_uid;

        $(this).bind("loaded.jstree", function (event, data) {
            // bind click handlers to correct urls when the tree is fully loaded
            $('.resourcetree li a').bind('click', function() {
                var url = $(this).parents().attr('url');
                if ( url != '#' ) {
                    window.location.href = $(this).parent().attr('url')
                }
            });
        })
        .jstree({ 
            "core": {
                "animation": 100,
            },
            // List of active plugins
            "plugins" : [ 
                "themes", "ui", "crrm", "json_data", "types"
            ],
            "json_data" : {
                // get the UID from the attr attribute
                // call treedata view with that parameter
                "ajax" : { "url" : ajax_call },
            },
            "themes" : {
                "theme" : "default",
                "dots" : false,
                "icons" : false
            },
            "types" : {
                // Want only root nodes to be root nodes. This will prevent
                // moving or creating any other type as a rootnode
                "valid_children" : [ "root" ],
                "types" : {
                    "topic" : {
                        // can have topics inside, but NOT root nodes
                        "valid_children" : [ "topic" ],
                    },
                    "root" : {
                       // can have topics inside, but NOT other root nodes
                       "valid_children" : [ "topic" ],
                       // those prevent the functions with the same name to
                       // be used on root nodes internally the `before` 
                       // event is used
                       "start_drag" : false,
                       "move_node" : false,
                       "delete_node" : false,
                       "remove" : false,
                       "rename_node" : false
                    }
                }
            },
        });
    });
});
