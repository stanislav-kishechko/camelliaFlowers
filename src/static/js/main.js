document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 1024) {
                toggleSidebar();
            }
        });
    });
});


function showTab(tabName) {
    // Hide all content
    const tabs = ['personal', 'security', 'notifications', 'preferences'];
    tabs.forEach(tab => {
        const content = document.getElementById('content-' + tab);
        const button = document.getElementById('tab-' + tab);

        if (content) content.classList.add('hidden');
        if (button) {
            button.classList.remove('border-pink-500', 'text-pink-600');
            button.classList.add('border-transparent', 'text-gray-500');
        }
    });

    const selectedContent = document.getElementById('content-' + tabName);
    const selectedTab = document.getElementById('tab-' + tabName);

    if (selectedContent) selectedContent.classList.remove('hidden');
    if (selectedTab) {
        selectedTab.classList.remove('border-transparent', 'text-gray-500');
        selectedTab.classList.add('border-pink-500', 'text-pink-600');
    }
}

function switchView(view) {
    const kanbanView = document.getElementById('orders-kanban');
    const tableView = document.getElementById('orders-table');
    const kanbanBtn = document.getElementById('view-kanban');
    const tableBtn = document.getElementById('view-table');

    if (!kanbanView || !tableView) return;

    if (view === 'kanban') {
        kanbanView.classList.remove('hidden');
        tableView.classList.add('hidden');
        kanbanBtn.classList.add('bg-white', 'shadow-sm');
        kanbanBtn.classList.remove('text-gray-600');
        tableBtn.classList.remove('bg-white', 'shadow-sm');
        tableBtn.classList.add('text-gray-600');
    } else {
        kanbanView.classList.add('hidden');
        tableView.classList.remove('hidden');
        tableBtn.classList.add('bg-white', 'shadow-sm');
        tableBtn.classList.remove('text-gray-600');
        kanbanBtn.classList.remove('bg-white', 'shadow-sm');
        kanbanBtn.classList.add('text-gray-600');
    }

    localStorage.setItem('ordersView', view);
}

document.addEventListener('DOMContentLoaded', function() {
    const savedView = localStorage.getItem('ordersView');
    if (savedView && (document.getElementById('orders-kanban') || document.getElementById('orders-table'))) {
        switchView(savedView);
    }
});


function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('modal-enter');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

function openNewOrderModal() {
    openModal('newOrderModal');
}

function closeNewOrderModal() {
    closeModal('newOrderModal');
}

function openNewClientModal() {
    openModal('newClientModal');
}

function closeNewClientModal() {
    closeModal('newClientModal');
}

function openNewProductModal() {
    openModal('newProductModal');
}

function closeNewProductModal() {
    closeModal('newProductModal');
}

function closeDeleteModal() {
    closeModal('deleteModal');
}

function confirmDelete() {
    const form = document.querySelector('#deleteModal form');
    if (form) {
        form.submit();
    }
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('fixed') && event.target.classList.contains('inset-0')) {
        const modals = ['newOrderModal', 'newClientModal', 'newProductModal', 'deleteModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal && !modal.classList.contains('hidden')) {
                closeModal(modalId);
            }
        });
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = ['newOrderModal', 'newClientModal', 'newProductModal', 'deleteModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal && !modal.classList.contains('hidden')) {
                closeModal(modalId);
            }
        });
    }
});

let draggedElement = null;

document.addEventListener('DOMContentLoaded', function() {
    const draggableCards = document.querySelectorAll('[draggable="true"]');

    draggableCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    const columns = document.querySelectorAll('.kanban-column > div:last-child');
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
    });
});

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    this.classList.add('bg-opacity-50');
    return false;
}

function handleDragLeave(e) {
    this.classList.remove('bg-opacity-50');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }

    this.classList.remove('bg-opacity-50');

    if (draggedElement && draggedElement !== this) {
        this.appendChild(draggedElement);

        // Here you can add HTMX request to update order status
        // Example:
        // const orderId = draggedElement.dataset.orderId;
        // const newStatus = this.dataset.status;
        // htmx.ajax('POST', `/orders/${orderId}/update-status/`, {values: {status: newStatus}});

        showToast('Статус замовлення оновлено', 'success');
    }

    return false;
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast px-6 py-4 rounded-lg shadow-lg text-white ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        type === 'warning' ? 'bg-yellow-500' : 
        'bg-blue-500'
    }`;
    toast.innerHTML = `
        <div class="flex items-center space-x-2">
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// ==========================================
// FORM VALIDATION
// ==========================================

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');

            // Show error message
            let errorMsg = field.parentElement.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('p');
                errorMsg.className = 'error-message text-red-500 text-xs mt-1';
                errorMsg.textContent = 'Це поле обов\'язкове';
                field.parentElement.appendChild(errorMsg);
            }
        } else {
            field.classList.remove('border-red-500');
            const errorMsg = field.parentElement.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });

    return isValid;
}

// Remove error styling on input
document.addEventListener('input', function(e) {
    if (e.target.hasAttribute('required')) {
        e.target.classList.remove('border-red-500');
        const errorMsg = e.target.parentElement.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }
});

// ==========================================
// SEARCH FUNCTIONALITY
// ==========================================

function initSearch(inputId, targetClass) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;

    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const items = document.querySelectorAll(targetClass);

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// ==========================================
// CONFIRMATION DIALOG
// ==========================================

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==========================================
// LOADING STATE
// ==========================================

function showLoading() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        document.body.removeChild(overlay);
    }
}

// ==========================================
// HTMX INTEGRATION
// ==========================================

// Show loading on HTMX requests
document.addEventListener('htmx:beforeRequest', function() {
    showLoading();
});

document.addEventListener('htmx:afterRequest', function() {
    hideLoading();
});

// Show toast on HTMX success
document.addEventListener('htmx:afterOnLoad', function(event) {
    try {
        const xhr = event.detail.xhr;
        const response = JSON.parse(xhr.responseText || '{}');

        if (response.message) {
            showToast(response.message, response.type || 'success');
        }
    } catch (e) {
        // Response is not JSON, ignore
    }
});

// ==========================================
// PRODUCT EDIT PAGE
// ==========================================

// Live preview update
function updateProductPreview() {
    const name = document.getElementById('id_name')?.value || 'Назва продукту';
    const price = document.getElementById('id_price')?.value || '0';
    const stock = document.getElementById('id_stock')?.value || '0';
    const emoji = document.getElementById('id_emoji')?.value || '🌸';
    const description = document.getElementById('id_description')?.value || 'Опис продукту';

    // Update preview
    const previewName = document.getElementById('preview-name');
    const previewPrice = document.getElementById('preview-price');
    const previewStock = document.getElementById('preview-stock');
    const previewEmoji = document.getElementById('preview-emoji');
    const previewDescription = document.getElementById('preview-description');

    if (previewName) previewName.textContent = name;
    if (previewPrice) previewPrice.textContent = `₴${price}`;
    if (previewStock) previewStock.textContent = `${stock} шт`;
    if (previewEmoji) previewEmoji.textContent = emoji;
    if (previewDescription) previewDescription.textContent = description;

    // Update stock badge
    const stockBadge = document.getElementById('preview-stock-badge');
    if (stockBadge) {
        if (stock > 10) {
            stockBadge.className = 'px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium';
            stockBadge.textContent = 'В наявності';
        } else if (stock > 0) {
            stockBadge.className = 'px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium';
            stockBadge.textContent = 'Закінчується';
        } else {
            stockBadge.className = 'px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium';
            stockBadge.textContent = 'Немає в наявності';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const productForm = document.querySelector('form[action*="product"]');
    if (productForm) {
        ['id_name', 'id_price', 'id_stock', 'id_emoji', 'id_description'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', updateProductPreview);
            }
        });
    }
});

function duplicateProduct() {
    const form = document.querySelector('form[action*="duplicate"]');
    if (form) {
        form.submit();
    }
}

function viewOrders() {
    window.location.href = '/orders/';
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('uk-UA', {
        style: 'currency',
        currency: 'UAH',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format date
function formatDate(date, format = 'short') {
    const options = format === 'long'
        ? { year: 'numeric', month: 'long', day: 'numeric' }
        : { year: 'numeric', month: '2-digit', day: '2-digit' };

    return new Intl.DateTimeFormat('uk-UA', options).format(new Date(date));
}

// Debounce function for search
function debounce(func, wait) {
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

document.addEventListener('DOMContentLoaded', function() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.classList.add('tooltip');
    });

    const messages = document.querySelectorAll('.alert, [role="alert"]');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.3s ease-out';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('mobile-overlay');

            // Close mobile menu on resize to desktop
            if (window.innerWidth >= 1024) {
                if (sidebar) sidebar.classList.remove('open');
                if (overlay) overlay.classList.add('hidden');
            }
        }, 250);
    });
});

function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');

        if (window.innerWidth < 1024) {
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('hidden');
        }
    }

    // Handle window resize
    window.addEventListener('resize', function () {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');

        if (window.innerWidth >= 1024) {
            sidebar.classList.remove('mobile-open');
            overlay.classList.add('hidden');
        }
    });