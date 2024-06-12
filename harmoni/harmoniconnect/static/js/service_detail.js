document.addEventListener('DOMContentLoaded', function() {
    const bookButton = document.querySelector('.book-button');
    const inquiryButton = document.querySelector('.inquiry-button');

    bookButton.addEventListener('click', function() {
        alert('Service booked successfully!');
    });

    inquiryButton.addEventListener('click', function() {
        alert('Inquiry sent successfully!');
    });
});