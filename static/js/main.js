/**
 * Derivco Stores Administration - Main JavaScript
 * Handles dynamic functionality for the web application
 */

// Global application object
const DerivcoStores = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        refreshInterval: 30000 // 30 seconds
    },

    // Initialize the application
    init: function() {
        console.log('Initializing Derivco Stores Administration...');
        this.bindEvents();
        this.loadInitialData();
        this.startPeriodicRefresh();
    },

    // Bind event listeners
    bindEvents: function() {
        // Search functionality
        const searchInput = document.getElementById('store-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch.bind(this));
        }

        // Status filter buttons (if they exist)
        const statusFilters = document.querySelectorAll('.status-filter');
        statusFilters.forEach(filter => {
            filter.addEventListener('click', this.handleStatusFilter.bind(this));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshData.bind(this));
        }

        // Modal close events
        this.bindModalEvents();
    },

    // Handle search functionality
    handleSearch: function(event) {
        const searchTerm = event.target.value.toLowerCase();
        const storeCards = document.querySelectorAll('.store-card');
        
        storeCards.forEach(card => {
            const storeName = card.dataset.storeName || '';
            const location = card.dataset.location || '';
            const manager = card.dataset.manager || '';
            
            const isMatch = storeName.includes(searchTerm) || 
                           location.includes(searchTerm) || 
                           manager.includes(searchTerm);
            
            card.style.display = isMatch ? 'block' : 'none';
        });

        // Update search results count
        const visibleCards = document.querySelectorAll('.store-card[style="display: block"], .store-card:not([style])');
        const hiddenCards = document.querySelectorAll('.store-card[style="display: none"]');
        
        if (searchTerm && visibleCards.length === 0 && hiddenCards.length > 0) {
            this.showNoResults(searchTerm);
        } else {
            this.hideNoResults();
        }
    },

    // Handle status filter
    handleStatusFilter: function(event) {
        const filterType = event.target.dataset.filter;
        const storeCards = document.querySelectorAll('.store-card');
        
        // Remove active class from all filters
        document.querySelectorAll('.status-filter').forEach(f => f.classList.remove('active'));
        event.target.classList.add('active');
        
        storeCards.forEach(card => {
            if (filterType === 'all') {
                card.style.display = 'block';
            } else {
                const hasMaintenanceIssue = card.querySelector('.status-indicator.maintenance');
                const shouldShow = (filterType === 'maintenance' && hasMaintenanceIssue) ||
                                  (filterType === 'operational' && !hasMaintenanceIssue);
                card.style.display = shouldShow ? 'block' : 'none';
            }
        });
    },

    // Show no results message
    showNoResults: function(searchTerm) {
        let noResultsDiv = document.getElementById('no-results');
        if (!noResultsDiv) {
            noResultsDiv = document.createElement('div');
            noResultsDiv.id = 'no-results';
            noResultsDiv.className = 'no-results';
            noResultsDiv.innerHTML = `
                <div class="no-results-content">
                    <i class="fas fa-search"></i>
                    <h3>No stores found</h3>
                    <p>No stores match "${searchTerm}". Try a different search term.</p>
                </div>
            `;
            
            const storesContainer = document.getElementById('stores-container');
            if (storesContainer) {
                storesContainer.appendChild(noResultsDiv);
            }
        } else {
            noResultsDiv.style.display = 'block';
            noResultsDiv.querySelector('p').textContent = `No stores match "${searchTerm}". Try a different search term.`;
        }
    },

    // Hide no results message
    hideNoResults: function() {
        const noResultsDiv = document.getElementById('no-results');
        if (noResultsDiv) {
            noResultsDiv.style.display = 'none';
        }
    },

    // Load initial data
    loadInitialData: function() {
        console.log('Loading initial data...');
        this.updateStatistics();
        this.checkSystemHealth();
    },

    // Update statistics on dashboard
    updateStatistics: function() {
        // This would typically fetch from API, but for now we'll calculate from DOM
        const storeCards = document.querySelectorAll('.store-card');
        const maintenanceIssues = document.querySelectorAll('.status-indicator.maintenance');
        
        // Update maintenance count if element exists
        const maintenanceCountElement = document.getElementById('maintenance-count');
        if (maintenanceCountElement) {
            maintenanceCountElement.textContent = maintenanceIssues.length;
        }

        // Update infrastructure stats if on infrastructure page
        this.updateInfrastructureStats();
    },

    // Update infrastructure statistics
    updateInfrastructureStats: function() {
        const powerOp = document.getElementById('power-operational');
        const networkOp = document.getElementById('network-operational');
        const hvacOp = document.getElementById('hvac-operational');
        const totalMaint = document.getElementById('total-maintenance');
        
        if (powerOp && networkOp && hvacOp && totalMaint) {
            // Count operational systems
            const powerOperational = document.querySelectorAll('#power-systems .status-indicator.operational').length;
            const networkOperational = document.querySelectorAll('#network-systems .status-indicator.operational').length;
            const hvacOperational = document.querySelectorAll('#hvac-systems .status-indicator.operational').length;
            const maintenanceNeeded = document.querySelectorAll('.status-indicator.maintenance').length;
            
            powerOp.textContent = powerOperational;
            networkOp.textContent = networkOperational;
            hvacOp.textContent = hvacOperational;
            totalMaint.textContent = maintenanceNeeded;
        }
    },

    // Check system health
    checkSystemHealth: function() {
        const criticalIssues = document.querySelectorAll('.status-indicator.maintenance').length;
        
        if (criticalIssues > 0) {
            this.showHealthAlert(criticalIssues);
        }
    },

    // Show health alert
    showHealthAlert: function(issueCount) {
        // Create alert banner if it doesn't exist
        let alertBanner = document.getElementById('health-alert');
        if (!alertBanner && issueCount > 2) { // Only show for multiple issues
            alertBanner = document.createElement('div');
            alertBanner.id = 'health-alert';
            alertBanner.className = 'alert-banner warning';
            alertBanner.innerHTML = `
                <div class="alert-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>System Alert: ${issueCount} infrastructure components require maintenance attention.</span>
                    <button class="alert-close" onclick="this.parentElement.parentElement.style.display='none'">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            const main = document.querySelector('.main');
            if (main) {
                main.insertBefore(alertBanner, main.firstChild);
            }
        }
    },

    // Refresh data
    refreshData: function() {
        console.log('Refreshing data...');
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (refreshBtn) {
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
            
            // Simulate data refresh
            setTimeout(() => {
                this.updateStatistics();
                this.checkSystemHealth();
                
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
                
                this.showToast('Data refreshed successfully', 'success');
            }, 1500);
        }
    },

    // Start periodic refresh
    startPeriodicRefresh: function() {
        setInterval(() => {
            this.updateStatistics();
            this.checkSystemHealth();
        }, this.config.refreshInterval);
    },

    // Modal functionality
    bindModalEvents: function() {
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // Close modal with escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                const visibleModals = document.querySelectorAll('.modal[style*="display: block"]');
                visibleModals.forEach(modal => {
                    modal.style.display = 'none';
                });
            }
        });
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.getElementById('toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Create new toast
        const toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast && toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    },

    // Get icon for toast type
    getToastIcon: function(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // Utility functions
    utils: {
        // Format date
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-ZA', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        // Format time
        formatTime: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleTimeString('en-ZA', {
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    }
};

// Store management functions
const StoreManager = {
    // View store details
    viewStore: function(storeId) {
        window.location.href = `/store/${storeId}`;
    },

    // Schedule maintenance (placeholder)
    scheduleMaintenance: function(storeId, system) {
        console.log(`Scheduling maintenance for store ${storeId}, system: ${system}`);
        DerivcoStores.showToast('Maintenance scheduling feature coming soon', 'info');
    },

    // Generate report (placeholder)
    generateReport: function(storeId) {
        console.log(`Generating report for store ${storeId}`);
        DerivcoStores.showToast('Report generation feature coming soon', 'info');
    },

    // View maintenance history (placeholder)
    viewHistory: function(storeId) {
        console.log(`Viewing history for store ${storeId}`);
        DerivcoStores.showToast('History view feature coming soon', 'info');
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    DerivcoStores.init();
});

// Global functions for HTML onclick handlers
function showSystemDetail(storeId, system) {
    StoreManager.viewStore(storeId);
}

function scheduleMaintenace() {
    StoreManager.scheduleMaintenance();
}

function generateReport() {
    StoreManager.generateReport();
}

function viewHistory() {
    StoreManager.viewHistory();
}

function closeModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DerivcoStores, StoreManager };
}