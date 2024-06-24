// dashboard.js
function openTab(tabName) {
    var i;
    var x = document.getElementsByClassName("tab-content");
    var tabButtons = document.getElementsByClassName("tab-button");
    for (i = 0; i < x.length; i++) {
        x[i].classList.remove("active");
    }
    for (i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
    event.currentTarget.classList.add("active");
}
document.addEventListener('DOMContentLoaded', function() {
    // Function to update notification badge
    function updateNotificationBadge() {
        var badge = document.getElementById('notification-badge');
        if (badge) {
            var notificationsCount = parseInt(badge.innerText);
            badge.style.display = notificationsCount > 0 ? 'inline' : 'none';
        }
    }

    // Call the function initially
    updateNotificationBadge();

    // Optionally, you can use WebSocket or AJAX to update notifications in real-time
    // Example with WebSocket (requires backend WebSocket implementation)
    // var socket = new WebSocket('ws://localhost:8000/ws/notifications/');
    // socket.onmessage = function(event) {
    //     updateNotificationBadge();
    // };
});