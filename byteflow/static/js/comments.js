$(document).ready(init);

jQuery.fn.extend({
    scrollBottom: function(speed) {
        return this.each(function() {
            var bottomOffset = $(this).offset().top + $(this).height();
            $('html').animate({scrollTop: bottomOffset - $(window).height()},
                              speed);
            });
        },
    scrollBottomCond: function(speed) {
        return this.each(function() {
            var bottomOffset = $(this).offset().top + $(this).height();
            if (bottomOffset > $(window).scrollTop() + $(window).height()) {
                $('html').animate({scrollTop: bottomOffset - $(window).height()},
                                  speed);
            }});
        }
    });

function init() {
    saved_posts = {};
    comment_form = $("#comment-form");
    input_reply = $("#id_reply_to", comment_form);
    comment_link = $("a.comment-link");
    // actions
    if ((!comment_form.find(".errorlist").length)&&(!get_get('comment'))) {
        comment_form.hide();
        var show_comment_link = true;
    }
    else {
        var id = input_reply.val();
        var show_comment_link = id;
        if (id) {$("#c" + id).append(comment_form);}
        comment_form.scrollBottomCond(1);
    }
    if (show_comment_link) {
        comment_link.show();
    }
    $("a.edit-comment").css("display", "inline");

    // spinner
    $('#ajaxload').ajaxStart(function(){$(this).show();}).ajaxStop(function(){$(this).hide();});
};

function get_get(name) {
    if (window.location.search!='') {
        var args = window.location.search.substr(1).split('&'); // 1 == '?'.length
        var data;
        for(var i=0; i<args.length; i++){
            data = args[i].split('=');
            if(data[0] == name){
                return data[1];
            }
        }
    }
    return false;
}

function get_json(data) {
    return eval('(' + data + ')');
};

function replyto(id) {
    cancel_comment();
    input_reply.val(id);
    $("#c" + id).append(comment_form);
    comment_form.show();
    $("#reply-link-" + id).hide();
    $('#id_body', comment_form).focus();
    comment_form.scrollBottomCond(1);
    return false;
};

function comment(location, after) {
    cancel_comment();
    input_reply.val('');
    if (!location) {
        location = ".post";
    }
    if (!after) {
        $(location).append(comment_form);
    } else {
        $(location).after(comment_form);
    }
    comment_form.show();
    comment_link.hide();
    $('#id_body', comment_form).focus();
    comment_form.scrollBottomCond(1);
    return false;
};

function cancel_comment() {
    id = input_reply.val();
    if (id) {
        $("#reply-link-" + id).show();
    }
    else {
        comment_link.show();
    }
    comment_form.hide();
    return false;
};

function edit_comment(id, url) {
    comment_div = $("#c" + id + " .text");
    saved_posts[id] = comment_div.html();
    $.post(url,
           {'get_body': ''},
           function (data) {
               json = get_json(data);
               comment_div.html('<textarea class="comment-edit-area">' + json.body + '</textarea>');
               $("#edit-comment-" + id).hide();
               $("#cancel-edit-" + id).css("display", "inline");
               $("#edit-submit-" + id).css("display", "inline");
               $("#c" + id).scrollBottomCond(1);
           });
    return false;
};

function cancel_edit(id) {
    comment_div = $("#c" + id + " .text");
    comment_div.html(saved_posts[id]);
    $("#cancel-edit-" + id).hide();
    $("#edit-submit-" + id).hide();
    $("#edit-comment-" + id).css("display", "inline");
    return false;
};

function submit_edit(id, url) {
    comment_div = $("#c" + id + " .text");
    text = $("#c" + id + " .text textarea.comment-edit-area").val();
    $.post(url,
           {'body': text},
           function (data) {
               json = get_json(data);
               comment_div.html(json.body_html);
               $("#cancel-edit-" + id).hide();
               $("#edit-submit-" + id).hide();
               $("#edit-comment-" + id).css("display", "inline");
           });
    return false;
};

function delete_comment(id, url) {
    if (confirm("Are you sure to delete this comment?"))
        {
            $.post(url,
                   {'delete': true},
                   function (data) {
                       json = get_json(data);
                       $('#c' + json.id).remove();
                   });
        };
    return false;
};

function preview_comment(url) {
    text = $("#id_body", comment_form).val();
    preview_div = $("#comment-preview", comment_form);
    $.post(url,
          {'body': text},
          function (data) {
              json = get_json(data);
              preview_div.html(json.body_preview);
              preview_div.css("display", "block");
          });
    return false;
};
