// Table sorting initialization for SFAI SDK Documentation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize table sorting for all tables
    const tables = document.querySelectorAll('table');

    tables.forEach(function(table) {
        // Add sorting capability if tablesort is available
        if (typeof Tablesort !== 'undefined') {
            new Tablesort(table);

            // Add visual indicators for sortable columns
            const headers = table.querySelectorAll('th');
            headers.forEach(function(header) {
                header.style.cursor = 'pointer';
                header.style.userSelect = 'none';
                header.setAttribute('title', 'Click to sort');

                // Add sort indicator
                const indicator = document.createElement('span');
                indicator.style.cssText = `
                    margin-left: 5px;
                    opacity: 0.5;
                    font-size: 0.8em;
                `;
                indicator.textContent = '↕';
                header.appendChild(indicator);
            });
        }
    });

    // Add table responsiveness
    tables.forEach(function(table) {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = `
            overflow-x: auto;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);

        // Add hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'var(--md-default-bg-color--light)';
            });

            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });

    console.log('Table sorting initialized for', tables.length, 'tables');
});
