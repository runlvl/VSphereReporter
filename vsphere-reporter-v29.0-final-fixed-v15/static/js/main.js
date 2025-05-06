/*
 * VMware vSphere Reporter v29.0
 * Main JavaScript File
 * Copyright (c) 2025 Bechtle GmbH
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Initialize alerts auto-close
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                } else {
                    alert.style.display = 'none';
                }
            }
        }, 5000); // Auto-close after 5 seconds
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-target'));
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('bi-eye');
            this.querySelector('i').classList.toggle('bi-eye-slash');
        });
    });

    // Handle report options select/deselect all
    const selectAllBtn = document.getElementById('select-all-options');
    const deselectAllBtn = document.getElementById('deselect-all-options');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="option_"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
    }
    
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="option_"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
    }

    // Handle table sorting
    const sortableTables = document.querySelectorAll('.sortable');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const sortKey = this.getAttribute('data-sort');
                const sortDirection = this.getAttribute('data-direction') === 'asc' ? 'desc' : 'asc';
                
                // Update sort direction
                headers.forEach(h => h.setAttribute('data-direction', ''));
                this.setAttribute('data-direction', sortDirection);
                
                // Update sort indicators
                headers.forEach(h => {
                    h.querySelectorAll('.sort-indicator').forEach(i => i.remove());
                });
                
                const indicator = document.createElement('span');
                indicator.classList.add('sort-indicator', 'ms-1');
                indicator.innerHTML = sortDirection === 'asc' ? '&#9650;' : '&#9660;';
                this.appendChild(indicator);
                
                // Sort the table
                sortTable(table, sortKey, sortDirection);
            });
        });
    });

    function sortTable(table, sortKey, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Sort the rows
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-${sortKey}]`).getAttribute(`data-${sortKey}`);
            const bValue = b.querySelector(`td[data-${sortKey}]`).getAttribute(`data-${sortKey}`);
            
            if (direction === 'asc') {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            } else {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            }
        });
        
        // Remove existing rows
        rows.forEach(row => row.remove());
        
        // Add sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    // Handle filter inputs
    const filterInputs = document.querySelectorAll('.table-filter');
    filterInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const tableId = this.getAttribute('data-target');
            const table = document.getElementById(tableId);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    let matchFound = false;
                    const cells = row.querySelectorAll('td');
                    cells.forEach(cell => {
                        if (cell.textContent.toLowerCase().indexOf(filterValue) > -1) {
                            matchFound = true;
                        }
                    });
                    
                    row.style.display = matchFound ? '' : 'none';
                });
            }
        });
    });

    // Check for demo mode and add notice
    const demoMode = document.body.getAttribute('data-demo-mode') === 'true';
    if (demoMode) {
        console.log('Running in demo mode with sample data');
    }
});