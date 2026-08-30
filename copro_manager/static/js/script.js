// Scripts personnalisés pour l'application de gestion de copropriétés

// Initialisation des tooltips Bootstrap (si besoin)
$(document).ready(function() {
    // Récupérer l'onglet actif depuis le localStorage
    const activeTab = localStorage.getItem('activeTab-' + window.location.pathname);

    if (activeTab) {
        // Activer l'onglet stocké
        $("#coproTabs button[data-bs-target='" + activeTab + "']").tab('show');
    }

    // Stocker l'onglet actif lors du clic
    $("#coproTabs button").on('shown.bs.tab', function (e) {
        localStorage.setItem('activeTab-' + window.location.pathname, $(e.target).attr('data-bs-target'));
    });

    // Filtre pour la page d'accueil (déjà géré dans index.html)
    // Cette partie est ici au cas où tu veux l'étendre
});

// Fonction pour formater les nombres en euros
function formatCurrency(value) {
    if (value === null || value === undefined || value === '') {
        return '0,00 €';
    }
    return parseFloat(value).toFixed(2).replace('.', ',') + ' €';
}

// Confirmation avant suppression avec message personnalisé
function confirmDelete(message) {
    return confirm(message || 'Voulez-vous vraiment supprimer cet élément ?');
}

// Animation des notifications (fermeture automatique après 5 secondes)
$(document).ready(function() {
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
});