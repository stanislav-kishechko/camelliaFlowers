// Order Modals JavaScript with Product Search and Client Autocomplete - FIXED VERSION

// ==================== GLOBAL VARIABLES ====================

let selectedProduct = null;
let selectedClient = null;
let clientSearchTimeout = null;
let productSearchTimeout = null;

// Products cache (loaded from backend)
let productsCache = [];
let clientsCache = [];

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Load products and clients cache when page loads
    loadProductsCache();
    loadClientsCache();

    console.log('Products loaded:', productsCache.length);
    console.log('Clients loaded:', clientsCache.length);

    // Initialize event listeners (they will work when modal opens)
    initializeEventListeners();
});

function initializeEventListeners() {
    // These listeners are added to the document, so they work even for dynamically shown elements

    // Product search input - using event delegation
    document.addEventListener('input', function(e) {
        if (e.target && e.target.id === 'new_product_search') {
            const query = e.target.value.trim().toLowerCase();

            clearTimeout(productSearchTimeout);

            if (query.length < 1) {
                hideProductSuggestions();
                return;
            }

            productSearchTimeout = setTimeout(() => {
                searchProducts(query);
            }, 300);
        }
    });

    // Product search focus
    document.addEventListener('focus', function(e) {
        if (e.target && e.target.id === 'new_product_search') {
            if (e.target.value.length >= 1) {
                searchProducts(e.target.value.trim().toLowerCase());
            }
        }
    }, true);

    // Client phone input
    document.addEventListener('input', function(e) {
        if (e.target && e.target.id === 'new_client_phone') {
            const phone = e.target.value.trim();

            clearTimeout(clientSearchTimeout);

            if (phone.length < 3) {
                hidePhoneSuggestions();
                clearClientStatus();
                return;
            }

            clientSearchTimeout = setTimeout(() => {
                searchClients(phone);
            }, 300);
        }
    });

    // Quantity change
    document.addEventListener('change', function(e) {
        if (e.target && e.target.id === 'new_quantity') {
            updateOrderPrice();
        }
    });
}

// ==================== NEW ORDER MODAL ====================

function openNewOrderModal() {
    document.getElementById('newOrderModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Set default delivery date to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('new_delivery_date');
    if (dateInput) {
        dateInput.value = today;
    }

    // Focus on phone input
    setTimeout(() => {
        const phoneInput = document.getElementById('new_client_phone');
        if (phoneInput) {
            phoneInput.focus();
        }
    }, 100);
}

function closeNewOrderModal() {
    const modal = document.getElementById('newOrderModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';

    const form = document.getElementById('newOrderForm');
    if (form) {
        form.reset();
    }

    // Clear selections
    clearProductSelection();
    clearClientSelection();
}

// ==================== PRODUCT SEARCH ====================

function loadProductsCache() {
    const productsData = document.getElementById('products-data');

    if (!productsData) {
        console.error('Products data element not found! Make sure <script id="products-data"> exists in template.');
        return;
    }

    try {
        const rawData = productsData.textContent.trim();
        console.log('Raw products data length:', rawData.length);

        productsCache = JSON.parse(rawData);
        console.log('Successfully loaded products:', productsCache.length);

        if (productsCache.length > 0) {
            console.log('First product example:', productsCache[0]);
        }
    } catch (e) {
        console.error('Failed to parse products data:', e);
        console.error('Data content:', productsData.textContent.substring(0, 200));
        productsCache = [];
    }
}

function searchProducts(query) {
    const suggestions = document.getElementById('product_suggestions');
    if (!suggestions) {
        console.error('Product suggestions element not found');
        return;
    }

    console.log('Searching products for:', query);
    console.log('Products cache size:', productsCache.length);

    // Filter products
    const filtered = productsCache.filter(product => {
        const matchName = product.name.toLowerCase().includes(query);
        const matchCategory = product.category && product.category.toLowerCase().includes(query);
        return matchName || matchCategory;
    });

    console.log('Found products:', filtered.length);

    if (filtered.length === 0) {
        suggestions.innerHTML = '<div class="p-4 text-center text-gray-500 text-sm">Продукти не знайдено</div>';
        suggestions.classList.remove('hidden');
        return;
    }

    // Build suggestions HTML
    let html = '';
    filtered.slice(0, 8).forEach(product => {
        // Escape special characters in product data
        const productName = escapeHtml(product.name);
        const productCategory = escapeHtml(product.category || '');

        html += `
            <div class="product-suggestion-item" onclick="selectProduct(${product.id})">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">${product.emoji || '🌹'}</span>
                    <div>
                        <p class="font-medium text-gray-800">${productName}</p>
                        <p class="text-xs text-gray-500">${productCategory}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-semibold text-pink-600">₴${parseFloat(product.price).toFixed(2)}</p>
                    ${product.stock !== undefined && product.stock !== null ? `<p class="text-xs text-gray-500">${product.stock} шт</p>` : ''}
                </div>
            </div>
        `;
    });

    suggestions.innerHTML = html;
    suggestions.classList.remove('hidden');

    console.log('Rendered suggestions HTML');
}

function selectProduct(productId) {
    const product = productsCache.find(p => p.id === productId);

    if (!product) {
        console.error('Product not found:', productId);
        return;
    }

    console.log('Selected product:', product);

    selectedProduct = product;

    // Update hidden input
    const productInput = document.getElementById('new_product');
    if (productInput) {
        productInput.value = product.id;
    }

    // Update display
    const emojiEl = document.getElementById('selected_product_emoji');
    const nameEl = document.getElementById('selected_product_name');
    const categoryEl = document.getElementById('selected_product_category');
    const priceEl = document.getElementById('selected_product_price');

    if (emojiEl) emojiEl.textContent = product.emoji || '🌹';
    if (nameEl) nameEl.textContent = product.name;
    if (categoryEl) categoryEl.textContent = product.category || '';
    if (priceEl) priceEl.textContent = `₴${parseFloat(product.price).toFixed(2)}`;

    // Show selected product card
    const selectedCard = document.getElementById('selected_product');
    if (selectedCard) {
        selectedCard.classList.remove('hidden');
    }

    // Clear search input and hide suggestions
    const searchInput = document.getElementById('new_product_search');
    if (searchInput) {
        searchInput.value = '';
    }
    hideProductSuggestions();

    // Update price calculation
    updateOrderPrice();
}

function clearProductSelection() {
    selectedProduct = null;

    const productInput = document.getElementById('new_product');
    if (productInput) productInput.value = '';

    const selectedCard = document.getElementById('selected_product');
    if (selectedCard) selectedCard.classList.add('hidden');

    const searchInput = document.getElementById('new_product_search');
    if (searchInput) searchInput.value = '';

    updateOrderPrice();
}

function hideProductSuggestions() {
    const suggestions = document.getElementById('product_suggestions');
    if (suggestions) {
        suggestions.classList.add('hidden');
    }
}

// ==================== CLIENT AUTOCOMPLETE ====================

function loadClientsCache() {
    const clientsData = document.getElementById('clients-data');

    if (!clientsData) {
        console.error('Clients data element not found! Make sure <script id="clients-data"> exists in template.');
        return;
    }

    try {
        const rawData = clientsData.textContent.trim();
        console.log('Raw clients data length:', rawData.length);

        clientsCache = JSON.parse(rawData);
        console.log('Successfully loaded clients:', clientsCache.length);

        if (clientsCache.length > 0) {
            console.log('First client example:', clientsCache[0]);
        }
    } catch (e) {
        console.error('Failed to parse clients data:', e);
        console.error('Data content:', clientsData.textContent.substring(0, 200));
        clientsCache = [];
    }
}

function searchClients(phone) {
    const suggestions = document.getElementById('phone_suggestions');
    if (!suggestions) return;

    // Search for exact match first
    const exactMatch = clientsCache.find(c => c.phone === phone);

    if (exactMatch) {
        // Client exists - auto-fill data
        selectExistingClient(exactMatch);
        hidePhoneSuggestions();
        return;
    }

    // Search for partial matches
    const filtered = clientsCache.filter(client =>
        client.phone.includes(phone) ||
        client.full_name.toLowerCase().includes(phone.toLowerCase())
    );

    if (filtered.length === 0) {
        // New client
        showNewClientStatus();
        hidePhoneSuggestions();
        return;
    }

    // Show suggestions
    let html = '';
    filtered.slice(0, 5).forEach(client => {
        const clientData = JSON.stringify({
            id: client.id,
            phone: client.phone,
            full_name: client.full_name,
            first_name: client.first_name,
            last_name: client.last_name
        }).replace(/"/g, '&quot;');

        html += `
            <div class="suggestion-item" onclick='selectExistingClient(${clientData})'>
                <p class="font-medium text-gray-800">${escapeHtml(client.full_name)}</p>
                <p class="text-sm text-gray-600">${escapeHtml(client.phone)}</p>
            </div>
        `;
    });

    suggestions.innerHTML = html;
    suggestions.classList.remove('hidden');
}

function selectExistingClient(client) {
    selectedClient = client;

    // Fill in client data
    const phoneInput = document.getElementById('new_client_phone');
    const firstNameInput = document.getElementById('new_client_first_name');
    const lastNameInput = document.getElementById('new_client_last_name');
    const clientIdInput = document.getElementById('new_client_id');

    if (phoneInput) phoneInput.value = client.phone;
    if (firstNameInput) {
        firstNameInput.value = client.first_name;
        firstNameInput.readOnly = true;
    }
    if (lastNameInput) {
        lastNameInput.value = client.last_name || '';
        lastNameInput.readOnly = true;
    }
    if (clientIdInput) clientIdInput.value = client.id;

    // Show status
    showExistingClientStatus(client.full_name);
    hidePhoneSuggestions();
}

function clearClientSelection() {
    selectedClient = null;

    const clientIdInput = document.getElementById('new_client_id');
    const phoneInput = document.getElementById('new_client_phone');
    const firstNameInput = document.getElementById('new_client_first_name');
    const lastNameInput = document.getElementById('new_client_last_name');

    if (clientIdInput) clientIdInput.value = '';
    if (phoneInput) phoneInput.value = '';
    if (firstNameInput) {
        firstNameInput.value = '';
        firstNameInput.readOnly = false;
    }
    if (lastNameInput) {
        lastNameInput.value = '';
        lastNameInput.readOnly = false;
    }

    clearClientStatus();
}

function showExistingClientStatus(clientName) {
    const statusDiv = document.getElementById('client_status');
    if (!statusDiv) return;

    statusDiv.className = 'p-3 rounded-lg bg-green-50 border border-green-200';
    const p = statusDiv.querySelector('p');
    if (p) {
        p.innerHTML = `✓ Існуючий клієнт: <strong>${escapeHtml(clientName)}</strong>`;
    }
    statusDiv.classList.remove('hidden');
}

function showNewClientStatus() {
    const statusDiv = document.getElementById('client_status');
    if (!statusDiv) return;

    statusDiv.className = 'p-3 rounded-lg bg-blue-50 border border-blue-200';
    const p = statusDiv.querySelector('p');
    if (p) {
        p.innerHTML = '➕ Буде створено нового клієнта';
    }
    statusDiv.classList.remove('hidden');

    // Clear client ID to create new
    const clientIdInput = document.getElementById('new_client_id');
    if (clientIdInput) clientIdInput.value = '';

    // Make name fields editable
    const firstNameInput = document.getElementById('new_client_first_name');
    const lastNameInput = document.getElementById('new_client_last_name');

    if (firstNameInput) firstNameInput.readOnly = false;
    if (lastNameInput) lastNameInput.readOnly = false;
}

function clearClientStatus() {
    const statusDiv = document.getElementById('client_status');
    if (statusDiv) {
        statusDiv.classList.add('hidden');
    }
}

function hidePhoneSuggestions() {
    const suggestions = document.getElementById('phone_suggestions');
    if (suggestions) {
        suggestions.classList.add('hidden');
    }
}

// ==================== PRICE CALCULATION ====================

function updateOrderPrice() {
    const quantityInput = document.getElementById('new_quantity');
    const totalPriceElement = document.getElementById('new_total_price');
    const unitPriceElement = document.getElementById('new_unit_price');

    if (!totalPriceElement || !unitPriceElement) return;

    if (!selectedProduct) {
        unitPriceElement.textContent = '₴0.00';
        totalPriceElement.textContent = '₴0.00';
        return;
    }

    const price = parseFloat(selectedProduct.price) || 0;
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
    const total = price * quantity;

    unitPriceElement.textContent = `₴${price.toFixed(2)}`;
    totalPriceElement.textContent = `₴${total.toFixed(2)}`;
}

// ==================== FORM SUBMISSION ====================

// Add form validation on submit
document.addEventListener('submit', function(e) {
    if (e.target && e.target.id === 'newOrderForm') {
        // Validate product selection
        if (!selectedProduct) {
            e.preventDefault();
            alert('Будь ласка, оберіть продукт');
            return false;
        }

        // Validate client data
        const phoneInput = document.getElementById('new_client_phone');
        const firstNameInput = document.getElementById('new_client_first_name');

        const phone = phoneInput ? phoneInput.value.trim() : '';
        const firstName = firstNameInput ? firstNameInput.value.trim() : '';

        if (!phone || !firstName) {
            e.preventDefault();
            alert('Будь ласка, заповніть телефон та ім\'я клієнта');
            return false;
        }

        // If new client (no client_id), add name fields to form
        const clientIdInput = document.getElementById('new_client_id');
        if (!clientIdInput || !clientIdInput.value) {
            const form = e.target;
            const lastNameInput = document.getElementById('new_client_last_name');

            // Create hidden inputs for new client
            const phoneHidden = document.createElement('input');
            phoneHidden.type = 'hidden';
            phoneHidden.name = 'client_phone';
            phoneHidden.value = phone;

            const firstNameHidden = document.createElement('input');
            firstNameHidden.type = 'hidden';
            firstNameHidden.name = 'client_first_name';
            firstNameHidden.value = firstName;

            const lastNameHidden = document.createElement('input');
            lastNameHidden.type = 'hidden';
            lastNameHidden.name = 'client_last_name';
            lastNameHidden.value = lastNameInput ? lastNameInput.value.trim() : '';

            form.appendChild(phoneHidden);
            form.appendChild(firstNameHidden);
            form.appendChild(lastNameHidden);
        }

        return true;
    }
});

// ==================== EDIT ORDER MODAL ====================

function openEditOrderModal(orderId) {
    // Fetch order data
    fetch(`/orders/${orderId}/data/`)
        .then(response => response.json())
        .then(data => {
            // Populate form fields
            const form = document.getElementById('editOrderForm');
            if (!form) return;

            const fields = {
                'edit_order_id': data.id,
                'edit_client': data.client_id,
                'edit_product': data.product_id,
                'edit_quantity': data.quantity,
                'edit_delivery_date': data.delivery_date,
                'edit_delivery_time': data.delivery_time || '',
                'edit_delivery_address': data.delivery_address,
                'edit_status': data.status,
                'edit_notes': data.notes || ''
            };

            for (const [fieldId, value] of Object.entries(fields)) {
                const field = document.getElementById(fieldId);
                if (field) field.value = value;
            }

            // Update prices
            updateEditOrderPrice();

            // Set form action
            form.action = `/orders/${orderId}/edit/`;

            // Show modal
            const modal = document.getElementById('editOrderModal');
            if (modal) {
                modal.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при завантаженні даних замовлення');
        });
}

function closeEditOrderModal() {
    const modal = document.getElementById('editOrderModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';

    const form = document.getElementById('editOrderForm');
    if (form) {
        form.reset();
    }
}

function updateEditOrderPrice() {
    const productSelect = document.getElementById('edit_product');
    const quantityInput = document.getElementById('edit_quantity');
    const totalPriceElement = document.getElementById('edit_total_price');
    const unitPriceElement = document.getElementById('edit_unit_price');

    if (!productSelect || !totalPriceElement || !unitPriceElement) return;

    const selectedOption = productSelect.options[productSelect.selectedIndex];
    const price = parseFloat(selectedOption.getAttribute('data-price')) || 0;
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

    const total = price * quantity;

    unitPriceElement.textContent = `₴${price.toFixed(2)}`;
    totalPriceElement.textContent = `₴${total.toFixed(2)}`;
}

// ==================== DELETE ORDER MODAL ====================

function confirmDeleteOrder(orderId, clientName, productName) {
    const modal = document.getElementById('deleteOrderModal');
    if (!modal) return;

    // Populate modal with order info
    const orderNumber = document.getElementById('delete_order_number');
    const orderClient = document.getElementById('delete_order_client');
    const orderProduct = document.getElementById('delete_order_product');

    if (orderNumber) orderNumber.textContent = `Замовлення #${orderId}`;
    if (orderClient && clientName) orderClient.textContent = `Клієнт: ${clientName}`;
    if (orderProduct && productName) orderProduct.textContent = `Продукт: ${productName}`;

    // Set form action
    const form = document.getElementById('deleteOrderForm');
    if (form) {
        form.action = `/orders/${orderId}/delete/`;
    }

    // Show modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeDeleteOrderModal() {
    const modal = document.getElementById('deleteOrderModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

// ==================== UTILITY FUNCTIONS ====================

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close modals on ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeNewOrderModal();
        closeEditOrderModal();
        closeDeleteOrderModal();
    }
});

// Close modals on outside click
document.addEventListener('click', function(event) {
    if (event.target.id === 'newOrderModal') {
        closeNewOrderModal();
    } else if (event.target.id === 'editOrderModal') {
        closeEditOrderModal();
    } else if (event.target.id === 'deleteOrderModal') {
        closeDeleteOrderModal();
    }
});

// Close suggestions when clicking outside
document.addEventListener('click', function(event) {
    const productSearch = document.getElementById('new_product_search');
    const productSuggestions = document.getElementById('product_suggestions');
    const phoneInput = document.getElementById('new_client_phone');
    const phoneSuggestions = document.getElementById('phone_suggestions');

    // Close product suggestions
    if (productSearch && productSuggestions &&
        !productSearch.contains(event.target) &&
        !productSuggestions.contains(event.target)) {
        hideProductSuggestions();
    }

    // Close phone suggestions
    if (phoneInput && phoneSuggestions &&
        !phoneInput.contains(event.target) &&
        !phoneSuggestions.contains(event.target)) {
        hidePhoneSuggestions();
    }
});