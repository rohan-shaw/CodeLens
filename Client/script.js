// Get all nav links
const navLinks = document.querySelectorAll('.nav-link');

// Add a click event listener to each link
navLinks.forEach(link => {
  link.addEventListener('click', () => {
    // Remove the 'active' class from all links
    navLinks.forEach(link => link.classList.remove('active'));

    // Add the 'active' class to the clicked link
    link.classList.add('active');
  });
});

// Initially set the active link based on the current page URL
const currentPageUrl = window.location.href;
navLinks.forEach(link => {
  if (link.href === currentPageUrl) {
    link.classList.add('active');
  }
});
