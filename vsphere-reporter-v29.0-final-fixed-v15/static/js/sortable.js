/**
 * Sortable.js - A simple sorting script for tables
 * For VMware vSphere Reporter v29.0
 * 
 * This script enables sorting of table columns by clicking on table headers.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all tables with the 'sortable' class
    const sortableTables = document.querySelectorAll('table.sortable');
    
    // Add click event listeners to all sortable table headers
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                sortTable(table, this.getAttribute('data-sort'), this);
            });
            // Add sort indicator and cursor style
            header.classList.add('sortable-header');
            header.innerHTML += '<span class="sort-indicator"></span>';
        });
    });
});

/**
 * Sort a table by the specified column
 * 
 * @param {HTMLTableElement} table - The table to sort
 * @param {string} column - The data attribute to sort by
 * @param {HTMLTableCellElement} header - The header element that was clicked
 */
function sortTable(table, column, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = header.classList.contains('sort-asc');
    
    // Remove sort classes from all headers in this table
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Set sort direction class
    if (isAsc) {
        header.classList.add('sort-desc');
    } else {
        header.classList.add('sort-asc');
    }
    
    // Sort the rows
    const sortedRows = rows.sort((a, b) => {
        const aValue = getCellValue(a, column);
        const bValue = getCellValue(b, column);
        
        // Compare values based on data types
        if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
            // Numeric comparison
            return isAsc 
                ? parseFloat(bValue) - parseFloat(aValue) 
                : parseFloat(aValue) - parseFloat(bValue);
        } else {
            // String comparison
            return isAsc 
                ? bValue.localeCompare(aValue, undefined, {sensitivity: 'base'}) 
                : aValue.localeCompare(bValue, undefined, {sensitivity: 'base'});
        }
    });
    
    // Clear tbody and append sorted rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    sortedRows.forEach(row => tbody.appendChild(row));
}

/**
 * Get cell value for sorting
 * 
 * @param {HTMLTableRowElement} row - The table row
 * @param {string} column - The data attribute to get the value from
 * @returns {string} - The cell value for sorting
 */
function getCellValue(row, column) {
    const cell = row.querySelector(`td[data-${column}]`);
    if (cell) {
        return cell.getAttribute(`data-${column}`) || cell.textContent.trim();
    }
    return '';
}

/**
 * Filter table rows based on search input
 * 
 * @param {Event} event - The input event
 */
function filterTable(event) {
    const input = event.target;
    const filter = input.value.toLowerCase();
    const tableId = input.getAttribute('data-target');
    const table = document.getElementById(tableId);
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        let shouldShow = false;
        
        cells.forEach(cell => {
            if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                shouldShow = true;
            }
        });
        
        row.style.display = shouldShow ? '' : 'none';
    });
}

// Add event listeners to table filters
document.addEventListener('DOMContentLoaded', function() {
    const tableFilters = document.querySelectorAll('.table-filter');
    tableFilters.forEach(filter => {
        filter.addEventListener('input', filterTable);
    });
});