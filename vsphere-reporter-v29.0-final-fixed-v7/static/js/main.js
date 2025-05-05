/**
 * VMware vSphere Reporter v29.0 - Web Edition
 * Copyright (c) 2025 Bechtle GmbH
 * 
 * Hauptskript für die vSphere Reporter Webanwendung
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisierung beim Laden der Seite
    console.log('VMware vSphere Reporter v29.0 initialized');

    // Bootstrap Tooltips initialisieren
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Bootstrap Popovers initialisieren
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Flash-Nachrichten nach 5 Sekunden automatisch ausblenden
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // DataTables initialisieren (falls vorhanden)
    if (typeof $.fn.DataTable !== 'undefined' && document.querySelector('.datatable')) {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/de-DE.json'
            },
            pageLength: 25,
            order: []
        });
    }

    // Verbindungsformular Validierung
    const connectForm = document.getElementById('connect-form');
    if (connectForm) {
        connectForm.addEventListener('submit', function(e) {
            const host = document.getElementById('host').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            let isValid = true;
            let errorMessage = '';
            
            if (!host.trim()) {
                isValid = false;
                errorMessage += 'Bitte geben Sie den vCenter-Host ein.\n';
            }
            
            if (!username.trim()) {
                isValid = false;
                errorMessage += 'Bitte geben Sie einen Benutzernamen ein.\n';
            }
            
            if (!password.trim()) {
                isValid = false;
                errorMessage += 'Bitte geben Sie ein Passwort ein.\n';
            }
            
            if (!isValid) {
                e.preventDefault();
                alert(errorMessage);
            } else {
                // Zeige Ladeindikator an
                document.getElementById('loading-indicator').classList.remove('d-none');
                document.getElementById('submit-button').disabled = true;
            }
        });
    }

    // Report-Generierungsformular Validierung
    const reportForm = document.getElementById('report-form');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            const vmwareTools = document.getElementById('include_vmware_tools').checked;
            const snapshots = document.getElementById('include_snapshots').checked;
            const orphanedVmdks = document.getElementById('include_orphaned_vmdks').checked;
            const topology = document.getElementById('include_topology').checked;
            
            if (!vmwareTools && !snapshots && !orphanedVmdks && !topology) {
                e.preventDefault();
                alert('Bitte wählen Sie mindestens einen Berichtsinhalt aus.');
            } else {
                // Zeige Ladeindikator an
                if (document.getElementById('loading-indicator')) {
                    document.getElementById('loading-indicator').classList.remove('d-none');
                }
                if (document.getElementById('submit-button')) {
                    document.getElementById('submit-button').disabled = true;
                }
            }
        });
    }

    // Logout-Bestätigung
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            const confirmed = confirm('Möchten Sie sich wirklich abmelden? Die Verbindung zum vCenter wird getrennt.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // Formatierung von Zeitstempeln und Zeitdauern
    formatTimestamps();
    formatDurations();
    formatDataSizes();
});

/**
 * Formatiert Zeitstempel in ein benutzerfreundliches Format
 */
function formatTimestamps() {
    document.querySelectorAll('.timestamp').forEach(function(element) {
        const timestamp = element.textContent.trim();
        if (timestamp) {
            try {
                const date = new Date(timestamp);
                if (!isNaN(date.getTime())) {
                    element.textContent = date.toLocaleString('de-DE', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                }
            } catch (e) {
                console.error("Fehler beim Formatieren des Zeitstempels:", e);
            }
        }
    });
}

/**
 * Formatiert Zeitdauern in ein benutzerfreundliches Format
 */
function formatDurations() {
    document.querySelectorAll('.duration').forEach(function(element) {
        const seconds = parseInt(element.textContent.trim());
        if (!isNaN(seconds)) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            
            if (days > 0) {
                element.textContent = `${days} Tage, ${hours} Std.`;
            } else if (hours > 0) {
                element.textContent = `${hours} Std., ${minutes} Min.`;
            } else {
                element.textContent = `${minutes} Minuten`;
            }
        }
    });
}

/**
 * Formatiert Datengrößen in ein benutzerfreundliches Format
 */
function formatDataSizes() {
    document.querySelectorAll('.data-size').forEach(function(element) {
        const bytes = parseInt(element.textContent.trim());
        if (!isNaN(bytes)) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
            if (bytes === 0) {
                element.textContent = '0 Bytes';
            } else {
                const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
                if (i === 0) {
                    element.textContent = bytes + ' ' + sizes[i];
                } else {
                    element.textContent = (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
                }
            }
        }
    });
}