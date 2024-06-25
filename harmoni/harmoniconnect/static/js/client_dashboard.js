
function openTab(event, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        tabcontent[i].classList.remove("active");
    }
    tablinks = document.getElementsByClassName("tab-button");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    document.getElementById(tabName).classList.add("active");
    event.currentTarget.className += " active";
}

    // JavaScript to handle modal display and review submission
    const writeReviewBtns = document.querySelectorAll('.write-review-btn');

    writeReviewBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const bookingId = this.getAttribute('data-booking-id');
            openReviewModal(bookingId);
        });
    });

    function openReviewModal(bookingId) {
        document.getElementById('reviewModal').style.display = 'flex';

        // Set the booking ID in the hidden input field inside the modal form
        document.getElementById('bookingIdInput').value = bookingId;
    }

    document.getElementById('cancelBtn').addEventListener('click', function () {
        document.getElementById('reviewModal').style.display = 'none';
    });

    const stars = document.querySelectorAll('.stars i');
    stars.forEach(star => {
        star.addEventListener('click', function () {
            stars.forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            let selected = false;
            for (let i = 0; i < stars.length; i++) {
                stars[i].classList.toggle('selected', selected);
                if (stars[i] === this) selected = true;
            }
        });
    });

    document.getElementById('submitBtn').addEventListener('click', function () {
        const selectedStar = document.querySelector('.stars i.selected');
        const rating = selectedStar ? selectedStar.getAttribute('data-value') : 0;
        const reviewText = document.querySelector('.review-textarea').value;
        const bookingId = document.getElementById('bookingIdInput').value;
        
        const reviewData = {
            booking: bookingId,
            rating: rating,
            comment: reviewText,
        };

        fetch('/api/reviews/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(reviewData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            document.getElementById('reviewModal').style.display = 'none';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
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
