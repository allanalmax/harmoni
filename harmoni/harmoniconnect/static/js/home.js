$(document).ready(function() {
    var messages = "{{ messages|escapejs }}";
    if (messages) {
        $('#popup-message').text(messages).fadeIn().delay(3000).fadeOut();
    }
});