/**
 * Trading Journal - Core Application Utilities
 * Handles: Toast notifications, Loading indicators, Offline detection, Delete confirmations
 */

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            this.container.setAttribute('aria-live', 'polite');
            this.container.setAttribute('aria-atomic', 'true');
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        
        const iconMap = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };
        
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${iconMap[type] || iconMap.info}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()" aria-label="Close">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;
        
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }
        
        return toast;
    }

    remove(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Loading Indicator Manager
class LoadingManager {
    show(element, text = 'Loading...') {
        if (!element) return;
        
        // Store original content
        if (!element.dataset.originalContent) {
            element.dataset.originalContent = element.innerHTML;
            element.dataset.originalDisabled = element.disabled;
        }
        
        element.disabled = true;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        
        element.classList.add('loading');
    }

    hide(element) {
        if (!element || !element.dataset.originalContent) return;
        
        element.innerHTML = element.dataset.originalContent;
        element.disabled = element.dataset.originalDisabled === 'true';
        element.classList.remove('loading');
        delete element.dataset.originalContent;
        delete element.dataset.originalDisabled;
    }

    showGlobal() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-white">Loading...</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    hideGlobal() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
}

// Delete Confirmation Manager
class DeleteConfirmation {
    static show(itemName, callback) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'deleteConfirmModal';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-danger">
                        <h5 class="modal-title text-danger">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>Confirm Delete
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete <strong>${itemName}</strong>?</p>
                        <p class="text-muted small">This action cannot be undone.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                            <i class="bi bi-trash me-2"></i>Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
            bsModal.hide();
            if (callback) callback();
            setTimeout(() => modal.remove(), 300);
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
}

// Offline Detection Manager
class OfflineManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.banner = null;
        this.init();
    }

    init() {
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        this.checkStatus();
    }

    checkStatus() {
        if (!this.isOnline) {
            this.handleOffline();
        }
    }

    handleOffline() {
        this.isOnline = false;
        this.showBanner('You are currently offline. Some features may be unavailable.', 'warning');
        if (window.toastManager) {
            window.toastManager.warning('You are offline. Changes will be synced when connection is restored.');
        }
    }

    handleOnline() {
        this.isOnline = true;
        this.hideBanner();
        if (window.toastManager) {
            window.toastManager.success('Connection restored!');
        }
    }

    showBanner(message, type = 'warning') {
        if (this.banner) return;
        
        this.banner = document.createElement('div');
        this.banner.className = `alert alert-${type} alert-dismissible fade show offline-banner`;
        this.banner.setAttribute('role', 'alert');
        this.banner.innerHTML = `
            <i class="bi bi-wifi-off me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(this.banner, mainContent.firstChild);
        } else {
            document.body.insertBefore(this.banner, document.body.firstChild);
        }
    }

    hideBanner() {
        if (this.banner) {
            this.banner.remove();
            this.banner = null;
        }
    }
}

// Initialize utilities
window.toastManager = new ToastManager();
window.loadingManager = new LoadingManager();
window.offlineManager = new OfflineManager();

// Auto-convert Django messages to toasts
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(msg => {
        const text = msg.textContent.trim();
        const type = msg.classList.contains('alert-success') ? 'success' :
                    msg.classList.contains('alert-danger') ? 'error' :
                    msg.classList.contains('alert-warning') ? 'warning' : 'info';
        
        if (window.toastManager && text) {
            window.toastManager.show(text, type);
            msg.style.display = 'none'; // Hide original message
        }
    });
    
    // Add loading to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                window.loadingManager.show(submitBtn);
            }
        });
    });
    
    // Add delete confirmation to delete links
    document.querySelectorAll('a[href*="/delete/"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.dataset.itemName || 'this item';
            DeleteConfirmation.show(itemName, () => {
                window.location.href = this.href;
            });
        });
    });
});

