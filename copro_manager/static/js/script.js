// Custom JavaScript for Copro Manager

// Fonction pour afficher/masquer les détails spécifiques selon le type de contrat
function toggleContratDetails(prefix, typeContrat) {
    const detailsDiv = document.getElementById(prefix + 'EspaceVertDetails');
    if (detailsDiv) {
        if (typeContrat === 'Espaces verts') {
            detailsDiv.style.display = 'block';
        } else {
            detailsDiv.style.display = 'none';
        }
    }
}

// Initialize tooltips
$(document).ready(function() {
    // Enable Bootstrap tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Confirm deletion
    $('form[onsubmit*="confirm"]').submit(function() {
        return confirm('\u00cates-vous s\u00fbr de vouloir supprimer cet \u00e9l\u00e9ment ?');
    });

    // Auto-focus on first input in modals
    $('.modal').on('shown.bs.modal', function() {
        $(this).find('input:first').focus();
    });

    // Smooth scrolling for anchor links
    $('a[href*="#"]').not('[href="#"]').click(function(e) {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            const target = $(this.hash);
            if (target.length) {
                e.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 500);
            }
        }
    });

    // Console welcome message
    console.log('%c Copro Manager ', 'background: #007bff; color: white; font-size: 20px; padding: 10px;');
    console.log('%c Logiciel de gestion de copropri\u00e9t\u00e9s ', 'color: #6c757d; font-size: 14px;');
});
