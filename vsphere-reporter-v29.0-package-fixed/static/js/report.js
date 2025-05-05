document.addEventListener('DOMContentLoaded', function() {
    // Fortschrittsbalken-Handling
    const progressBar = document.querySelector('.progress-bar');
    const statusMessage = document.getElementById('status-message');
    
    // Polling-Funktion für den Berichtsstatus
    function pollReportStatus(reportId) {
        fetch(`/api/report/progress/${reportId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Aktualisiere Fortschrittsbalken
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.setAttribute('aria-valuenow', data.progress);
                    statusMessage.textContent = data.message;
                    
                    // Prüfe, ob der Bericht abgeschlossen ist
                    if (data.completed) {
                        if (data.success) {
                            // Bericht erfolgreich erstellt
                            document.getElementById('report-success').classList.remove('d-none');
                            document.getElementById('report-download-link').href = `/download/${reportId}/${data.output_file}`;
                            document.getElementById('report-view-link').href = `/report/view/${reportId}`;
                        } else {
                            // Fehler bei der Berichtserstellung
                            document.getElementById('report-error').classList.remove('d-none');
                            document.getElementById('error-message').textContent = data.error || 'Unbekannter Fehler';
                        }
                        // Verstecke den Fortschrittsbereich
                        document.getElementById('report-progress').classList.add('d-none');
                    } else {
                        // Bericht wird noch erstellt, weiter pollen
                        setTimeout(() => pollReportStatus(reportId), 1000);
                    }
                } else {
                    // Fehler beim Abrufen des Status
                    console.error('Fehler beim Abrufen des Berichtsstatus:', data.error);
                    document.getElementById('report-error').classList.remove('d-none');
                    document.getElementById('error-message').textContent = data.error || 'Fehler beim Abrufen des Berichtsstatus';
                    document.getElementById('report-progress').classList.add('d-none');
                }
            })
            .catch(error => {
                console.error('Netzwerkfehler:', error);
                document.getElementById('report-error').classList.remove('d-none');
                document.getElementById('error-message').textContent = 'Netzwerkfehler beim Abrufen des Berichtsstatus';
                document.getElementById('report-progress').classList.add('d-none');
            });
    }
    
    // Starte Bericht, wenn der Button geklickt wird
    const startReportButton = document.getElementById('start-report-button');
    if (startReportButton) {
        startReportButton.addEventListener('click', function() {
            // Verstecke den Start-Button
            startReportButton.disabled = true;
            document.getElementById('report-setup').classList.add('d-none');
            document.getElementById('report-progress').classList.remove('d-none');
            
            // Starte den Bericht
            fetch('/api/report/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Starte das Polling für den Berichtsstatus
                    pollReportStatus(data.report_id);
                } else {
                    // Fehler beim Starten des Berichts
                    document.getElementById('report-error').classList.remove('d-none');
                    document.getElementById('error-message').textContent = data.error || 'Fehler beim Starten des Berichts';
                    document.getElementById('report-progress').classList.add('d-none');
                    startReportButton.disabled = false;
                    document.getElementById('report-setup').classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Netzwerkfehler:', error);
                document.getElementById('report-error').classList.remove('d-none');
                document.getElementById('error-message').textContent = 'Netzwerkfehler beim Starten des Berichts';
                document.getElementById('report-progress').classList.add('d-none');
                startReportButton.disabled = false;
                document.getElementById('report-setup').classList.remove('d-none');
            });
        });
    }
    
    // Filterfunktionen für Tabellen
    const tableFilters = document.querySelectorAll('.table-filter');
    tableFilters.forEach(filter => {
        filter.addEventListener('input', function() {
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            if (!table) return;
            
            const term = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    });
    
    // Sortierfunktionen für Tabellen
    document.querySelectorAll('th.sortable').forEach(headerCell => {
        headerCell.addEventListener('click', function() {
            const table = this.closest('table');
            const index = Array.from(this.parentNode.children).indexOf(this);
            const isAscending = this.classList.contains('sort-asc');
            
            // Sortierrichtung umkehren
            this.classList.toggle('sort-asc', !isAscending);
            this.classList.toggle('sort-desc', isAscending);
            
            // Sortierungsklassen von anderen Spalten entfernen
            Array.from(this.parentNode.children).forEach(cell => {
                if (cell !== this) {
                    cell.classList.remove('sort-asc', 'sort-desc');
                }
            });
            
            // Tabelle sortieren
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            const sortedRows = rows.sort((a, b) => {
                const aValue = a.children[index].textContent.trim();
                const bValue = b.children[index].textContent.trim();
                
                // Versuche numerische Sortierung
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                }
                
                // Fallback auf String-Sortierung
                return isAscending 
                    ? aValue.localeCompare(bValue, undefined, {numeric: true, sensitivity: 'base'})
                    : bValue.localeCompare(aValue, undefined, {numeric: true, sensitivity: 'base'});
            });
            
            // Sortierte Zeilen einfügen
            const tbody = table.querySelector('tbody');
            sortedRows.forEach(row => tbody.appendChild(row));
        });
    });
});
