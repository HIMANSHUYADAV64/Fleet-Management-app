document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality when DOM is loaded
    
    // 1. Flash message auto hide
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
    
    // 2. Table sorting functionality
    function setupTableSorting() {
        const sortTables = document.querySelectorAll('table[data-sortable]');
        sortTables.forEach(table => {
            const headers = table.querySelectorAll('th[data-sort]');
            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.getAttribute('data-sort');
                    const direction = header.classList.contains('asc') ? 'desc' : 'asc';
                    
                    // Remove existing sort classes
                    headers.forEach(h => {
                        h.classList.remove('asc', 'desc');
                        const icon = h.querySelector('i');
                        if (icon) icon.className = 'fas fa-sort';
                    });
                    
                    // Set new sort class and icon
                    header.classList.add(direction);
                    const icon = header.querySelector('i');
                    if (icon) {
                        icon.className = direction === 'asc' 
                            ? 'fas fa-sort-up' 
                            : 'fas fa-sort-down';
                    }
                    
                    // Sort table
                    sortTable(table, column, direction);
                });
            });
        });
    }
    
    function sortTable(table, column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td:nth-child(${getColumnIndex(table, column) + 1})`).textContent;
            const bValue = b.querySelector(`td:nth-child(${getColumnIndex(table, column) + 1})`).textContent;
            
            if (column === 'rps_closing_date' || column === 'insurance_expiry_date' || 
                column === 'expiry_date' || column === 'purchase_date') {
                const aDate = new Date(aValue);
                const bDate = new Date(bValue);
                return direction === 'asc' ? aDate - bDate : bDate - aDate;
            } else if (column === 'net_payment' || column === 'tds') {
                const aNum = parseFloat(aValue.replace(/[^\d.]/g, ''));
                const bNum = parseFloat(bValue.replace(/[^\d.]/g, ''));
                return direction === 'asc' ? aNum - bNum : bNum - aNum;
            } else {
                return direction === 'asc' 
                    ? aValue.localeCompare(bValue) 
                    : bValue.localeCompare(aValue);
            }
        });
        
        // Remove existing rows
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }
        
        // Append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
    
    function getColumnIndex(table, columnName) {
        const headers = table.querySelectorAll('th');
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].getAttribute('data-sort') === columnName) {
                return i;
            }
        }
        return 0;
    }
    
    // 3. Routes filter form functionality
    function setupRouteFilters() {
        const filterForm = document.getElementById('filter-form');
        if (filterForm) {
            const applyBtn = document.getElementById('apply-filter');
            const resetBtn = document.getElementById('reset-filter');
            
            applyBtn.addEventListener('click', applyFilters);
            resetBtn.addEventListener('click', resetFilters);
        }
    }
    
    function applyFilters() {
        const vehicleId = document.getElementById('vehicle_id').value;
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const paymentStatus = document.getElementById('payment_status').value;
        
        const params = new URLSearchParams({
            vehicle_id: vehicleId,
            start_date: startDate,
            end_date: endDate,
            payment_status: paymentStatus
        });
        
        fetch(`/api/routes/filter?${params}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('routes-container');
                if (data.length > 0) {
                    container.innerHTML = `
                        <table id="routes-table" data-sortable>
                            <thead>
                                <tr>
                                    <th data-sort="rps_no">RPS No <i class="fas fa-sort"></i></th>
                                    <th data-sort="vehicle_no">Vehicle <i class="fas fa-sort"></i></th>
                                    <th data-sort="from_location">Route <i class="fas fa-sort"></i></th>
                                    <th data-sort="rps_closing_date">Closing Date <i class="fas fa-sort"></i></th>
                                    <th data-sort="net_payment">Net Payment <i class="fas fa-sort"></i></th>
                                    <th data-sort="payment_status">Status <i class="fas fa-sort"></i></th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.map(route => `
                                    <tr>
                                        <td>${route.rps_no}</td>
                                        <td>${route.vehicle_no}</td>
                                        <td>${route.from_location} to ${route.to_location}</td>
                                        <td>${route.rps_closing_date}</td>
                                        <td>${route.net_payment.toFixed(2)}</td>
                                        <td><span class="status ${route.payment_status.toLowerCase()}">${route.payment_status}</span></td>
                                        <td class="actions">
                                            <a href="/route/edit/${route.id}" class="btn-icon"><i class="fas fa-edit"></i></a>
                                            <form action="/route/delete/${route.id}" method="POST" class="inline-form">
                                                <button type="submit" class="btn-icon danger" onclick="return confirm('Are you sure you want to delete this route?')">
                                                    <i class="fas fa-trash-alt"></i>
                                                </button>
                                            </form>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                    
                    // Reinitialize sorting for the new table
                    setupTableSorting();
                } else {
                    container.innerHTML = '<div class="empty-state"><i class="fas fa-route fa-3x"></i><h3>No routes found with the selected filters.</h3></div>';
                }
            })
            .catch(error => {
                console.error('Error fetching filtered routes:', error);
                alert('An error occurred while filtering routes. Please try again.');
            });
    }
    
    function resetFilters() {
        document.getElementById('vehicle_id').value = '';
        document.getElementById('start_date').value = '';
        document.getElementById('end_date').value = '';
        document.getElementById('payment_status').value = 'all';
        
        // Reload original routes
        const container = document.getElementById('routes-container');
        fetch('/routes')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newContainer = doc.getElementById('routes-container');
                if (newContainer) {
                    container.innerHTML = newContainer.innerHTML;
                    setupTableSorting();
                }
            });
    }
    
    // 4. Document preview functionality
    function setupDocumentPreview() {
        document.querySelectorAll('.document-preview').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('href');
                
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <span class="modal-close">&times;</span>
                        <iframe src="${url}" frameborder="0"></iframe>
                    </div>
                `;
                
                document.body.appendChild(modal);
                
                modal.querySelector('.modal-close').addEventListener('click', () => {
                    modal.remove();
                });
                
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        modal.remove();
                    }
                });
            });
        });
    }
    
    // 5. Notification functionality
    function setupNotifications() {
        document.querySelectorAll('.notification').forEach(notification => {
            if (!notification.classList.contains('unread')) {
                setTimeout(() => {
                    notification.style.opacity = '0';
                    setTimeout(() => notification.remove(), 500);
                }, 5000);
            }
        });
    }
    
    // 6. Form validation
    function setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = form.querySelectorAll('[required]');
                let valid = true;
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        valid = false;
                        const error = document.createElement('span');
                        error.className = 'error';
                        error.textContent = 'This field is required';
                        
                        const existingError = field.parentNode.querySelector('.error');
                        if (!existingError) {
                            field.parentNode.appendChild(error);
                        }
                    }
                });
                
                if (!valid) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Initialize all components
    setupTableSorting();
    setupRouteFilters();
    setupDocumentPreview();
    setupNotifications();
    setupFormValidation();
    
    // Date picker initialization (if using any)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });
});
