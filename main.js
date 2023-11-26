// Get the button element by its id
var button = document.getElementById('redirectButton');

// Add a click event listener to the button
button.addEventListener('click', function() {
    // Redirect to another HTML page
    window.location.href = 'http://127.0.0.1:5500/MedCycle/main.html';
});
