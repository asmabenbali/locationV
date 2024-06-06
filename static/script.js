// Show loading animation
function showLoadingAnimation() {
    document.getElementById('loading-animation').style.display = 'block';
}

// Hide loading animation
function hideLoadingAnimation() {
    document.getElementById('loading-animation').style.display = 'none';
}

// Example: Show loading animation when moving between pages
document.addEventListener('DOMContentLoaded', function() {
    // Show loading animation before page content is loaded
    showLoadingAnimation();
});


// Example: Hide loading animation when page content is fully loaded
window.addEventListener('load', function() {
    // Hide loading animation after page content is loaded
    hideLoadingAnimation();
});
