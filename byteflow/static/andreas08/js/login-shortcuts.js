function show_login()
{
  $("#openid-form").hide();
  $("#login-form").toggle();
  $("#login-form #email").focus();
  return false;
}

function show_openid()
{
  $("#login-form").hide();
  $("#openid-form").toggle();
  $("#openid-form #id_openid_url").focus();
  return false;
}

function form_close()
{
  $("#login-form").hide();
  $("#openid-form").hide();
  return false;
}
