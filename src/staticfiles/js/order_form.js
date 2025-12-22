/**
 * JavaScript для роботи з формою створення замовлення
 * Підтримує AJAX запити, автозаповнення, множинні товари
 */

// Глобальні змінні
let selectedItems = []; // Масив вибраних товарів
let clientSearchTimeout = null;
let productSearchTimeout = null;
let selectedClient = null;

// Отримання CSRF токену
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

const csrftoken = getCookie('csrftoken');

// ==================== ПОШУК КЛІЄНТІВ ====================

document.getElementById('new_client_phone')?.addEventListener('input', function(e) {
    const phone = e.target.value.trim();

    // Очищення попереднього таймауту
    clearTimeout(clientSearchTimeout);

    if (phone.length < 3) {
        hideClientSuggestions();
        return;
    }

    // Затримка перед запитом (debounce)
    clientSearchTimeout = setTimeout(() => {
        searchClients(phone);
    }, 300);
});

function searchClients(phone) {
    fetch(`/api/orders/clients/search/?phone=${encodeURIComponent(phone)}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.clients && data.clients.length > 0) {
            showClientSuggestions(data.clients);
        } else {
            hideClientSuggestions();
            showNewClientStatus();
        }
    })
    .catch(error => {
        console.error('Помилка пошуку клієнтів:', error);
    });
}

function showClientSuggestions(clients) {
    const container = document.getElementById('phone_suggestions');
    container.innerHTML = '';

    clients.forEach(client => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-medium text-gray-800">${client.full_name}</p>
                    <p class="text-sm text-gray-500">${client.phone}</p>
                </div>
                <div class="text-right">
                    <p class="text-xs text-gray-500">Замовлень: ${client.orders_count}</p>
                    <p class="text-xs text-pink-600">₴${client.total_spent}</p>
                </div>
            </div>
        `;

        item.addEventListener('click', () => selectClient(client));
        container.appendChild(item);
    });

    container.classList.remove('hidden');
}

function hideClientSuggestions() {
    document.getElementById('phone_suggestions').classList.add('hidden');
}

function selectClient(client) {
    selectedClient = client;

    // Заповнення полів
    document.getElementById('new_client_phone').value = client.phone;
    document.getElementById('new_client_first_name').value = client.first_name;
    document.getElementById('new_client_last_name').value = client.last_name;
    document.getElementById('new_client_id').value = client.id;

    // Показ статусу
    const statusDiv = document.getElementById('client_status');
    statusDiv.className = 'p-3 rounded-lg bg-green-50 border border-green-200';
    statusDiv.querySelector('p').innerHTML = `
        ✓ Існуючий клієнт: <strong>${client.full_name}</strong> 
        (${client.orders_count} замовлень, ₴${client.total_spent})
    `;
    statusDiv.classList.remove('hidden');

    hideClientSuggestions();
}

function showNewClientStatus() {
    const statusDiv = document.getElementById('client_status');
    statusDiv.className = 'p-3 rounded-lg bg-blue-50 border border-blue-200';
    statusDiv.querySelector('p').innerHTML = '✨ Новий клієнт буде створений';
    statusDiv.classList.remove('hidden');

    // Очищення ID
    document.getElementById('new_client_id').value = '';
    selectedClient = null;
}

// ==================== ПОШУК ПРОДУКТІВ ====================

document.getElementById('new_product_search')?.addEventListener('input', function(e) {
    const query = e.target.value.trim();

    clearTimeout(productSearchTimeout);

    if (query.length < 2) {
        hideProductSuggestions();
        return;
    }

    productSearchTimeout = setTimeout(() => {
        searchProducts(query);
    }, 300);
});

function searchProducts(query) {
    fetch(`/api/orders/products/search/?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.products && data.products.length > 0) {
            showProductSuggestions(data.products);
        } else {
            hideProductSuggestions();
        }
    })
    .catch(error => {
        console.error('Помилка пошуку продуктів:', error);
    });
}

function showProductSuggestions(products) {
    const container = document.getElementById('product_suggestions');
    container.innerHTML = '';

    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'product-suggestion-item';

        const stockStatus = product.stock > 0
            ? `<span class="text-green-600 text-xs">✓ В наявності: ${product.stock}</span>`
            : '<span class="text-red-600 text-xs">✗ Немає в наявності</span>';

        item.innerHTML = `
            <div class="flex items-center space-x-3">
                <span class="text-2xl">${product.emoji || '🌹'}</span>
                <div>
                    <p class="font-medium text-gray-800">${product.name}</p>
                    <p class="text-sm text-gray-500">${product.category || 'Без категорії'}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-lg font-bold text-pink-600">₴${product.price}</p>
                ${stockStatus}
            </div>
        `;

        if (product.stock > 0) {
            item.addEventListener('click', () => addProductToOrder(product));
        } else {
            item.style.opacity = '0.5';
            item.style.cursor = 'not-allowed';
        }

        container.appendChild(item);
    });

    container.classList.remove('hidden');
}

function hideProductSuggestions() {
    document.getElementById('product_suggestions').classList.add('hidden');
}

// ==================== УПРАВЛІННЯ ТОВАРАМИ В ЗАМОВЛЕННІ ====================

function addProductToOrder(product) {
    // Перевірка чи товар вже доданий
    const existingIndex = selectedItems.findIndex(item => item.product.id === product.id);

    if (existingIndex !== -1) {
        // Збільшити кількість
        selectedItems[existingIndex].quantity++;
    } else {
        // Додати новий товар
        selectedItems.push({
            product: product,
            quantity: 1
        });
    }

    // Очищення пошуку
    document.getElementById('new_product_search').value = '';
    hideProductSuggestions();

    renderSelectedItems();
    updateTotalPrice();
}

function removeProductFromOrder(productId) {
    selectedItems = selectedItems.filter(item => item.product.id !== productId);
    renderSelectedItems();
    updateTotalPrice();
}

function updateItemQuantity(productId, newQuantity) {
    const item = selectedItems.find(item => item.product.id === productId);
    if (item && newQuantity > 0) {
        item.quantity = parseInt(newQuantity);
        updateTotalPrice();

        // Оновити відображення підсумку для конкретного товару
        const subtotalEl = document.getElementById(`subtotal_${productId}`);
        if (subtotalEl) {
            const subtotal = item.product.price * item.quantity;
            subtotalEl.textContent = `₴${subtotal.toFixed(2)}`;
        }
    }
}

function renderSelectedItems() {
    const container = document.getElementById('selected_items_container');
    const noItemsMessage = document.getElementById('no_items_message');

    if (selectedItems.length === 0) {
        container.innerHTML = '';
        noItemsMessage.classList.remove('hidden');
        return;
    }

    noItemsMessage.classList.add('hidden');
    container.innerHTML = '';

    selectedItems.forEach(item => {
        const subtotal = item.product.price * item.quantity;

        const itemCard = document.createElement('div');
        itemCard.className = 'order-item-card item-enter';
        itemCard.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3 flex-1">
                    <span class="text-3xl">${item.product.emoji || '🌹'}</span>
                    <div class="flex-1">
                        <p class="font-semibold text-gray-800">${item.product.name}</p>
                        <p class="text-sm text-gray-500">₴${item.product.price} / шт</p>
                    </div>
                </div>
                
                <div class="flex items-center space-x-4">
                    <!-- Кількість -->
                    <div class="flex items-center space-x-2">
                        <button type="button" 
                                onclick="updateItemQuantity(${item.product.id}, ${item.quantity - 1})"
                                class="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded-full transition"
                                ${item.quantity <= 1 ? 'disabled class="opacity-50 cursor-not-allowed"' : ''}>
                            −
                        </button>
                        <input type="number" 
                               value="${item.quantity}" 
                               min="1"
                               onchange="updateItemQuantity(${item.product.id}, this.value)"
                               class="w-16 px-2 py-1 text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500">
                        <button type="button" 
                                onclick="updateItemQuantity(${item.product.id}, ${item.quantity + 1})"
                                class="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded-full transition">
                            +
                        </button>
                    </div>
                    
                    <!-- Підсумок -->
                    <div class="text-right min-w-[100px]">
                        <p class="text-xs text-gray-500">Сума</p>
                        <p class="text-lg font-bold text-pink-600" id="subtotal_${item.product.id}">₴${subtotal.toFixed(2)}</p>
                    </div>
                    
                    <!-- Видалити -->
                    <button type="button" 
                            onclick="removeProductFromOrder(${item.product.id})"
                            class="text-red-500 hover:text-red-700 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        container.appendChild(itemCard);
    });

    // Оновити лічильник
    document.getElementById('items_count').textContent = `${selectedItems.length} ${selectedItems.length === 1 ? 'товар' : 'товарів'}`;
    document.getElementById('new_items_total').textContent = selectedItems.length;
}

function updateTotalPrice() {
    const total = selectedItems.reduce((sum, item) => {
        return sum + (item.product.price * item.quantity);
    }, 0);

    document.getElementById('new_total_price').textContent = `₴${total.toFixed(2)}`;
}

// ==================== ВІДПРАВКА ФОРМИ ====================

document.getElementById('newOrderForm')?.addEventListener('submit', function(e) {
    e.preventDefault();

    // Валідація
    if (selectedItems.length === 0) {
        alert('Додайте хоча б один товар до замовлення');
        return;
    }

    const phone = document.getElementById('new_client_phone').value.trim();
    const firstName = document.getElementById('new_client_first_name').value.trim();
    const deliveryAddress = document.getElementById('new_delivery_address').value.trim();
    const deliveryDate = document.getElementById('new_delivery_date').value;

    if (!phone || !firstName || !deliveryAddress || !deliveryDate) {
        alert('Заповніть всі обов\'язкові поля');
        return;
    }

    // Підготовка даних
    const formData = {
        client_id: document.getElementById('new_client_id').value || null,
        client_phone: phone,
        client_first_name: firstName,
        client_last_name: document.getElementById('new_client_last_name').value.trim(),
        items: selectedItems.map(item => ({
            product_id: item.product.id,
            quantity: item.quantity
        })),
        delivery_address: deliveryAddress,
        delivery_date: deliveryDate,
        delivery_time: document.getElementById('new_delivery_time').value || null,
        notes: document.getElementById('new_notes').value.trim()
    };

    // Відправка запиту
    const submitBtn = document.getElementById('submit_order_btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="flex items-center justify-center">⏳ Створення...</span>';

    fetch('/api/orders/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Успіх
            alert(data.message);
            closeNewOrderModal();
            // Перезавантаження сторінки для відображення нового замовлення
            window.location.reload();
        } else {
            // Помилка
            console.error('Помилки валідації:', data.errors);
            alert('Помилка при створенні замовлення. Перевірте введені дані.');
        }
    })
    .catch(error => {
        console.error('Помилка:', error);
        alert('Виникла помилка при створенні замовлення');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <span class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Створити замовлення
            </span>
        `;
    });
});

// ==================== MODAL УПРАВЛІННЯ ====================

function openNewOrderModal() {
    document.getElementById('newOrderModal').classList.remove('hidden');
    resetOrderForm();

    // Встановити мінімальну дату доставки на сьогодні
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('new_delivery_date').setAttribute('min', today);
    document.getElementById('new_delivery_date').value = today;
}

function closeNewOrderModal() {
    document.getElementById('newOrderModal').classList.add('hidden');
    resetOrderForm();
}

function resetOrderForm() {
    selectedItems = [];
    selectedClient = null;

    document.getElementById('newOrderForm').reset();
    document.getElementById('new_client_id').value = '';
    document.getElementById('client_status').classList.add('hidden');

    hideClientSuggestions();
    hideProductSuggestions();
    renderSelectedItems();
    updateTotalPrice();
}

// Закриття модалки по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeNewOrderModal();
    }
});

// Закриття підказок при кліку поза ними
document.addEventListener('click', function(e) {
    if (!e.target.closest('#new_client_phone') && !e.target.closest('#phone_suggestions')) {
        hideClientSuggestions();
    }
    if (!e.target.closest('#new_product_search') && !e.target.closest('#product_suggestions')) {
        hideProductSuggestions();
    }
});