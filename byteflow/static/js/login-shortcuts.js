function show_login()
{
    $("#login-form").show();
    $("#login-shortcuts").hide();
    $("#login-form #email").focus();
    return false;
}

function form_close()
{
    $("#login-form").hide();
    $("#openid-form").hide();
    $("#login-shortcuts").show();
    return false;
}

function show_openid()
{
    $("#openid-form").show();
    $("#login-shortcuts").hide();
    $("#openid-form #id_openid_url").focus();
    return false;
}
