// VMware vSphere Reporter v19 - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Aktiviere alle Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Automatisches Schließen von Alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Sortieren von Tabellen
    const sortableTables = document.querySelectorAll('table.sortable');
    sortableTables.forEach(function(table) {
        const headers = table.querySelectorAll('th');
        headers.forEach(function(header, index) {
            header.addEventListener('click', function() {
                sortTable(table, index);
            });
            header.style.cursor = 'pointer';
            header.title = 'Klicken zum Sortieren';
        });
    });

    // Export-Buttons
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const format = this.getAttribute('data-format');
            const url = this.getAttribute('href');
            
            // Zeige Spinner während des Exports
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exportiere...';
            this.disabled = true;
            
            // Führe Export aus
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ format: format })
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    throw new Error('Export fehlgeschlagen');
                }
            })
            .then(blob => {
                // Download der Datei
                const a = document.createElement('a');
                const url = window.URL.createObjectURL(blob);
                a.href = url;
                a.download = `vsphere_report.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Button zurücksetzen
                this.innerHTML = originalHTML;
                this.disabled = false;
            })
            .catch(error => {
                console.error('Fehler beim Export:', error);
                alert('Fehler beim Export: ' + error.message);
                this.innerHTML = originalHTML;
                this.disabled = false;
            });
        });
    });
});

// Funktion zum Sortieren von Tabellen
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const sortDirection = table.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc';
    
    // Sortieren der Zeilen
    rows.sort((a, b) => {
        const aValue = a.querySelectorAll('td')[columnIndex].textContent.trim();
        const bValue = b.querySelectorAll('td')[columnIndex].textContent.trim();
        
        if (sortDirection === 'asc') {
            return aValue.localeCompare(bValue, undefined, { numeric: true, sensitivity: 'base' });
        } else {
            return bValue.localeCompare(aValue, undefined, { numeric: true, sensitivity: 'base' });
        }
    });
    
    // Leere den Table Body
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Füge die sortierten Zeilen wieder ein
    rows.forEach(row => {
        tbody.appendChild(row);
    });
    
    // Aktualisiere die Sortierrichtung
    table.setAttribute('data-sort-direction', sortDirection);
}