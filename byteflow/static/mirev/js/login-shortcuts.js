$(document).ready(login_shortcuts);

function login_shortcuts() {
    $('#show-pass').click(function () {
            $('#openid-form').hide();
            $('#login-form').toggle();
            $('#login-form #email').focus();
            return false;
        });
    $('#show-openid').click(function () {
            $('#login-form').hide();
            $('#openid-form').toggle();
            $('#openid-form #openid_url').focus();
            return false;
        });
}
