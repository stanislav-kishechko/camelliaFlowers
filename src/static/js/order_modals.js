/**
 * order_modals.js
 * Обробка модальних вікон для створення та редагування замовлень
 * з динамічним пошуком клієнтів та товарів
 * ОНОВЛЕНО: підтримка опціональної доставки
 */

// =====================================
// ГЛОБАЛЬНІ ЗМІННІ
// =====================================

let selectedItems = []; // Масив вибраних товарів
let selectedClient = null; // Обраний клієнт
let debounceTimer = null; // Таймер для debounce
let clientSearchInitialized = false; // Флаг ініціалізації пошуку клієнтів
let productSearchInitialized = false; // Флаг ініціалізації пошуку товарів

// =====================================
// ВІДКРИТТЯ/ЗАКРИТТЯ МОДАЛЬНИХ ВІКОН
// =====================================

function openNewOrderModal() {
    const modal = document.getElementById('newOrderModal');
    if (!modal) {
        console.error('❌ Modal #newOrderModal not found!');
        return;
    }

    modal.classList.remove('hidden');
    resetNewOrderForm();

    // ВАЖЛИВО: Ініціалізувати пошук після відкриття модалки
    setupClientSearch();
    setupProductSearch();

    console.log('✅ Modal opened and search initialized');
}

function closeNewOrderModal() {
    document.getElementById('newOrderModal').classList.add('hidden');
    resetNewOrderForm();
}

function resetNewOrderForm() {
    document.getElementById('newOrderForm').reset();
    selectedItems = [];
    selectedClient = null;
    document.getElementById('new_client_id').value = '';
    document.getElementById('client_status').classList.add('hidden');

    // Скинути тип замовлення на самовивіз
    const pickupRadio = document.querySelector('input[name="order_type"][value="pickup"]');
    if (pickupRadio) {
        pickupRadio.checked = true;
        toggleDeliveryFields(false);
    }

    updateItemsList();
    updateTotalPrice();
}

// =====================================
// ПЕРЕМИКАННЯ ПОЛІВ ДОСТАВКИ
// =====================================

function toggleDeliveryFields(show) {
    const deliveryFields = document.getElementById('delivery_fields');
    const deliveryDateInput = document.getElementById('new_delivery_date');
    const deliveryAddressInput = document.getElementById('new_delivery_address');

    if (show) {
        deliveryFields.classList.remove('hidden');
        deliveryFields.classList.add('delivery-fields-show');

        // Встановити мінімальну дату (сьогодні)
        const today = new Date().toISOString().split('T')[0];
        deliveryDateInput.setAttribute('min', today);

        // Зробити поля обов'язковими
        deliveryDateInput.setAttribute('required', 'required');
        deliveryAddressInput.setAttribute('required', 'required');
    } else {
        deliveryFields.classList.add('hidden');
        deliveryFields.classList.remove('delivery-fields-show');

        // Очистити значення
        deliveryDateInput.value = '';
        document.getElementById('new_delivery_time').value = '';
        deliveryAddressInput.value = '';

        // Зняти обов'язковість
        deliveryDateInput.removeAttribute('required');
        deliveryAddressInput.removeAttribute('required');
    }
}

// =====================================
// ПОШУК КЛІЄНТІВ
// =====================================

function setupClientSearch() {
    if (clientSearchInitialized) {
        console.log('⚠️ Client search already initialized, skipping');
        return;
    }

    const phoneInput = document.getElementById('new_client_phone');
    const suggestionsContainer = document.getElementById('phone_suggestions');

    console.log('📞 Setup client search, input:', phoneInput, 'container:', suggestionsContainer);

    if (!phoneInput || !suggestionsContainer) {
        console.error('❌ Client search elements not found!');
        return;
    }

    console.log('✅ Client search elements found, adding event listener');

    phoneInput.addEventListener('input', function () {
        const phone = this.value.trim();
        console.log('📝 Phone input changed:', phone);

        // Очистити попередній таймер
        clearTimeout(debounceTimer);

        if (phone.length < 3) {
            suggestionsContainer.classList.add('hidden');
            suggestionsContainer.innerHTML = '';
            return;
        }

        // Встановити новий таймер (debounce 300ms)
        debounceTimer = setTimeout(() => {
            searchClients(phone);
        }, 300);
    });

    // Закриття підказок при кліку поза ними
    document.addEventListener('click', function (e) {
        if (!phoneInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.classList.add('hidden');
        }
    });

    clientSearchInitialized = true;
}

function searchClients(phone) {
    const suggestionsContainer = document.getElementById('phone_suggestions');

    // Додаємо індикатор завантаження
    suggestionsContainer.innerHTML = `
        <div class="p-3 text-sm text-gray-500 text-center">
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Пошук...
        </div>
    `;
    suggestionsContainer.classList.remove('hidden');

    console.log('🔍 Пошук клієнтів:', phone);

    fetch(`/api/orders/clients/search/?phone=${encodeURIComponent(phone)}`)
        .then(response => {
            console.log('📡 Відповідь статус:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📦 Отримані дані:', data);

            if (data.clients && data.clients.length > 0) {
                displayClientSuggestions(data.clients);
            } else {
                suggestionsContainer.innerHTML = `
                    <div class="p-3 text-sm text-gray-500 text-center">
                        Клієнта не знайдено. Буде створено нового.
                    </div>
                `;
                suggestionsContainer.classList.remove('hidden');
                selectedClient = null;
                document.getElementById('new_client_id').value = '';
            }
        })
        .catch(error => {
            console.error('❌ Помилка пошуку клієнтів:', error);
            suggestionsContainer.innerHTML = `
                <div class="p-3 text-sm text-red-500 text-center">
                    Помилка: ${error.message}
                </div>
            `;
            suggestionsContainer.classList.remove('hidden');
        });
}

function displayClientSuggestions(clients) {
    const suggestionsContainer = document.getElementById('phone_suggestions');

    suggestionsContainer.innerHTML = clients.map(client => `
        <div class="suggestion-item" onclick="selectClient(${client.id}, '${client.first_name}', '${client.last_name}', '${client.phone}', ${client.orders_count}, '${client.total_spent}')">
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-semibold text-gray-800">${client.full_name}</p>
                    <p class="text-xs text-gray-500">${client.phone}</p>
                </div>
                <div class="text-right">
                    <p class="text-xs text-gray-500">${client.orders_count} замовлень</p>
                    <p class="text-sm font-semibold text-pink-600">₴${client.total_spent}</p>
                </div>
            </div>
        </div>
    `).join('');

    suggestionsContainer.classList.remove('hidden');
}

function selectClient(id, firstName, lastName, phone, ordersCount, totalSpent) {
    selectedClient = {id, firstName, lastName, phone, ordersCount, totalSpent};

    // Заповнити поля форми
    document.getElementById('new_client_phone').value = phone;
    document.getElementById('new_client_first_name').value = firstName;
    document.getElementById('new_client_last_name').value = lastName || '';
    document.getElementById('new_client_id').value = id;

    // Показати статус клієнта
    const statusDiv = document.getElementById('client_status');
    statusDiv.innerHTML = `
        <p class="text-sm font-medium text-green-700">
            ✅ Існуючий клієнт: ${firstName} ${lastName} | ${ordersCount} замовлень | ₴${totalSpent}
        </p>
    `;
    statusDiv.classList.remove('hidden');
    statusDiv.classList.add('bg-green-50', 'border', 'border-green-200');

    // Сховати підказки
    document.getElementById('phone_suggestions').classList.add('hidden');
}

// =====================================
// ПОШУК ТОВАРІВ
// =====================================

function setupProductSearch() {
    if (productSearchInitialized) {
        console.log('⚠️ Product search already initialized, skipping');
        return;
    }

    const searchInput = document.getElementById('new_product_search');
    const suggestionsContainer = document.getElementById('product_suggestions');

    console.log('🛍️ Setup product search, input:', searchInput, 'container:', suggestionsContainer);

    if (!searchInput || !suggestionsContainer) {
        console.error('❌ Product search elements not found!');
        return;
    }

    console.log('✅ Product search elements found, adding event listener');

    searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        console.log('📝 Product search query:', query);

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            suggestionsContainer.classList.add('hidden');
            suggestionsContainer.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            searchProducts(query);
        }, 300);
    });

    // Закриття підказок
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.classList.add('hidden');
        }
    });

    productSearchInitialized = true;
}

function searchProducts(query) {
    const suggestionsContainer = document.getElementById('product_suggestions');

    suggestionsContainer.innerHTML = `
        <div class="p-3 text-sm text-gray-500 text-center">
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Пошук...
        </div>
    `;
    suggestionsContainer.classList.remove('hidden');

    console.log('🔍 Пошук продуктів:', query);

    fetch(`/api/orders/products/search/?q=${encodeURIComponent(query)}`)
        .then(response => {
            console.log('📡 Відповідь статус:', response.status);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('📦 Отримані продукти:', data);

            if (data.products && data.products.length > 0) {
                displayProductSuggestions(data.products);
            } else {
                suggestionsContainer.innerHTML = `
                    <div class="p-3 text-sm text-gray-500 text-center">
                        Товари не знайдено
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Помилка пошуку продуктів:', error);
            suggestionsContainer.innerHTML = `
                <div class="p-3 text-sm text-red-500 text-center">
                    Помилка: ${error.message}
                </div>
            `;
        });
}

function displayProductSuggestions(products) {
    const suggestionsContainer = document.getElementById('product_suggestions');

    suggestionsContainer.innerHTML = products.map(product => `
        <div class="product-suggestion-item" 
             onclick='addProductToOrder(${JSON.stringify(product)})'>
            <div class="flex items-center space-x-3">
                <span class="text-2xl">${product.emoji}</span>
                <div>
                    <p class="font-semibold text-gray-800">${product.name}</p>
                    <p class="text-xs text-gray-500">${product.category}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="font-semibold text-pink-600">₴${product.price}</p>
                <p class="text-xs text-gray-500">На складі: ${product.stock}</p>
            </div>
        </div>
    `).join('');

    suggestionsContainer.classList.remove('hidden');
}

function addProductToOrder(product) {
    console.log('➕ Додавання товару:', product);

    // Перевірка чи товар вже доданий
    const existingItemIndex = selectedItems.findIndex(item => item.product.id === product.id);

    if (existingItemIndex !== -1) {
        // Збільшити кількість
        selectedItems[existingItemIndex].quantity += 1;
    } else {
        // Додати новий товар
        selectedItems.push({
            product: product,
            quantity: 1
        });
    }

    updateItemsList();
    updateTotalPrice();

    // Очистити пошук
    document.getElementById('new_product_search').value = '';
    document.getElementById('product_suggestions').classList.add('hidden');
}

function removeItemFromOrder(productId) {
    selectedItems = selectedItems.filter(item => item.product.id !== productId);
    updateItemsList();
    updateTotalPrice();
}

function updateItemQuantity(productId, newQuantity) {
    const item = selectedItems.find(item => item.product.id === productId);
    if (item) {
        if (newQuantity > 0 && newQuantity <= item.product.stock) {
            item.quantity = newQuantity;
            updateItemsList();
            updateTotalPrice();
        } else if (newQuantity > item.product.stock) {
            alert(`Недостатньо товару на складі. Доступно: ${item.product.stock} шт`);
        }
    }
}

function updateItemsList() {
    const container = document.getElementById('selected_items_container');
    const noItemsMsg = document.getElementById('no_items_message');
    const itemsCount = document.getElementById('items_count');

    if (selectedItems.length === 0) {
        container.innerHTML = '';
        noItemsMsg.classList.remove('hidden');
        itemsCount.textContent = '0 товарів';
        return;
    }

    noItemsMsg.classList.add('hidden');
    itemsCount.textContent = `${selectedItems.length} ${selectedItems.length === 1 ? 'товар' : 'товарів'}`;

    container.innerHTML = selectedItems.map(item => {
        // ВИПРАВЛЕННЯ: правильно парсимо ціну
        const price = parseFloat(String(item.product.price).replace(',', '.'));
        const subtotal = (price * item.quantity).toFixed(2);
        return `
            <div class="order-item-card item-enter">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3 flex-1">
                        <span class="text-3xl">${item.product.emoji}</span>
                        <div class="flex-1">
                            <p class="font-semibold text-gray-800">${item.product.name}</p>
                            <p class="text-sm text-gray-600">₴${item.product.price} за шт</p>
                        </div>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2">
                            <button type="button"
                                    onclick="updateItemQuantity(${item.product.id}, ${item.quantity - 1})"
                                    class="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded-lg transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
                                </svg>
                            </button>
                            <input type="number"
                                   value="${item.quantity}"
                                   min="1"
                                   max="${item.product.stock}"
                                   onchange="updateItemQuantity(${item.product.id}, parseInt(this.value))"
                                   class="w-16 px-2 py-1 text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500">
                            <button type="button"
                                    onclick="updateItemQuantity(${item.product.id}, ${item.quantity + 1})"
                                    class="w-8 h-8 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded-lg transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                            </button>
                        </div>
                        
                        <div class="text-right min-w-[80px]">
                            <p class="text-xs text-gray-500">Сума</p>
                            <p class="text-lg font-bold text-pink-600">₴${subtotal}</p>
                        </div>
                        
                        <button type="button"
                                onclick="removeItemFromOrder(${item.product.id})"
                                class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updateTotalPrice() {
    let total = 0;
    let totalItems = 0;

    selectedItems.forEach(item => {
        // ВИПРАВЛЕННЯ: правильно парсимо ціну
        // Видаляємо всі нечислові символи крім крапки/коми, замінюємо кому на крапку
        const priceStr = String(item.product.price).replace(',', '.');
        const price = parseFloat(priceStr);

        // Перевіряємо чи ціна валідна
        if (!isNaN(price) && price > 0) {
            total += price * item.quantity;
        } else {
            console.warn('⚠️ Invalid price for product:', item.product.name, item.product.price);
        }

        totalItems += item.quantity;
    });

    console.log('💰 Total calculated:', total, 'items:', totalItems);

    document.getElementById('new_total_price').textContent = `₴${total.toFixed(2)}`;
    document.getElementById('new_items_total').textContent = totalItems;
}

// =====================================
// SUBMIT ФОРМИ
// =====================================

function setupOrderFormSubmit() {
    const form = document.getElementById('newOrderForm');
    if (!form) {
        console.error('❌ Form #newOrderForm not found!');
        return;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        console.log('📤 Submitting order form');
        submitNewOrder();
    });

    console.log('✅ Form submit handler attached');
}

function submitNewOrder() {
    // Валідація
    if (selectedItems.length === 0) {
        alert('Додайте хоча б один товар до замовлення');
        return;
    }

    const clientPhone = document.getElementById('new_client_phone').value.trim();
    const clientFirstName = document.getElementById('new_client_first_name').value.trim();

    if (!clientPhone || !clientFirstName) {
        alert('Заповніть дані клієнта');
        return;
    }

    // Перевірка типу замовлення
    const needsDelivery = document.querySelector('input[name="order_type"]:checked').value === 'delivery';

    // Валідація полів доставки
    if (needsDelivery) {
        const deliveryAddress = document.getElementById('new_delivery_address').value.trim();
        const deliveryDate = document.getElementById('new_delivery_date').value;

        if (!deliveryAddress || !deliveryDate) {
            alert('Заповніть обов\'язкові поля доставки');
            return;
        }
    }

    // Збір даних
    const orderData = {
        client_id: document.getElementById('new_client_id').value || null,
        client_phone: clientPhone,
        client_first_name: clientFirstName,
        client_last_name: document.getElementById('new_client_last_name').value.trim(),
        items: selectedItems.map(item => ({
            product_id: item.product.id,
            quantity: item.quantity
        })),
        needs_delivery: needsDelivery,
        notes: document.getElementById('new_notes').value.trim()
    };

    // Додати дані доставки якщо потрібно
    if (needsDelivery) {
        orderData.delivery_address = document.getElementById('new_delivery_address').value.trim();
        orderData.delivery_date = document.getElementById('new_delivery_date').value;
        orderData.delivery_time = document.getElementById('new_delivery_time').value || null;
    }

    console.log('📦 Order data:', orderData);

    // Відправка
    const submitBtn = document.getElementById('submit_order_btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="flex items-center justify-center">
            <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Створення...
        </span>
    `;

    // Отримання CSRF токену
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/orders/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(orderData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Успішне створення
                alert(data.message);
                closeNewOrderModal();

                // Перезавантажити сторінку або перейти до деталей замовлення
                window.location.href = `/orders/${data.order.id}/`;
            } else {
                // Помилка
                alert('Помилка: ' + (data.error || JSON.stringify(data.errors)));
                submitBtn.disabled = false;
                submitBtn.innerHTML = `
                <span class="flex items-center justify-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                    </svg>
                    Створити замовлення
                </span>
            `;
            }
        })
        .catch(error => {
            console.error('Помилка:', error);
            alert('Виникла помилка при створенні замовлення');
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
            <span class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Створити замовлення
            </span>
        `;
        });
}

// =====================================
// ІНІЦІАЛІЗАЦІЯ
// =====================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Order modals initializing...');

    // Ініціалізуємо тільки submit форми тут
    setupOrderFormSubmit();

    // Пошук буде ініціалізовано при відкритті модалки

    // Закриття модального вікна по ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('newOrderModal');
            if (modal && !modal.classList.contains('hidden')) {
                closeNewOrderModal();
            }
        }
    });

    console.log('✅ Order modals base initialized');
});

// =====================================
// ФУНКЦІЇ ДЛЯ РЕДАГУВАННЯ ЗАМОВЛЕННЯ
// =====================================

function openEditOrderModal(orderId) {
    console.log('✏️ Opening edit modal for order:', orderId);

    const modal = document.getElementById('editOrderModal');
    if (!modal) {
        console.error('❌ Edit modal not found!');
        return;
    }

    // Показати модалку з індикатором завантаження
    modal.classList.remove('hidden');

    // Завантажити дані замовлення
    loadOrderForEdit(orderId);
}

function loadOrderForEdit(orderId) {
    // Показати індикатор завантаження
    const modalContent = document.querySelector('#editOrderModal .p-4.md\\:p-6:last-child');
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="flex items-center justify-center py-12">
                <svg class="animate-spin h-10 w-10 text-pink-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="ml-3 text-gray-600">Завантаження...</span>
            </div>
        `;
    }

    // Завантажити дані через AJAX
    fetch(`/orders/${orderId}/`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to load order');
            return response.text();
        })
        .then(html => {
            // Перенаправити на сторінку редагування:
            window.location.href = `/orders/${orderId}/edit/`;
        })
        .catch(error => {
            console.error('❌ Error loading order:', error);
            closeEditOrderModal();
            alert('Помилка завантаження замовлення');
        });
}

function closeEditOrderModal() {
    const modal = document.getElementById('editOrderModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// =====================================
// ФУНКЦІЇ ДЛЯ ВИДАЛЕННЯ ЗАМОВЛЕННЯ
// =====================================

function openDeleteOrderModal(orderId) {
    console.log('🗑️ Opening delete modal for order:', orderId);

    const modal = document.getElementById('deleteOrderModal');
    if (!modal) {
        console.error('❌ Delete modal not found!');
        return;
    }

    // Завантажити інформацію про замовлення
    loadOrderForDelete(orderId);

    modal.classList.remove('hidden');
}

function loadOrderForDelete(orderId) {
    // Встановити ID замовлення у форму
    const form = document.getElementById('deleteOrderForm');
    if (form) {
        form.action = `/orders/${orderId}/delete/`;
    }

    // Показати індикатор завантаження
    document.getElementById('delete_order_number').textContent = `#${orderId}`;
    document.getElementById('delete_order_client').textContent = 'Завантаження...';
    document.getElementById('delete_order_product').textContent = '';

    // Завантажити деталі замовлення
    fetch(`/api/orders/${orderId}/details/`)
        .then(response => {
            if (!response.ok) {
                // Якщо API не існує, просто показуємо базову інформацію
                document.getElementById('delete_order_client').textContent = 'Інформація недоступна';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                const order = data.order;
                document.getElementById('delete_order_number').textContent = `#${order.id}`;
                document.getElementById('delete_order_client').textContent = `Клієнт: ${order.client.full_name}`;

                if (order.items && order.items.length > 0) {
                    const itemsText = order.items.map(item =>
                        `${item.product.emoji || '🌹'} ${item.product.name} (${item.quantity} шт)`
                    ).join(', ');
                    document.getElementById('delete_order_product').textContent = itemsText;
                }
            }
        })
        .catch(error => {
            console.error('Error loading order details:', error);
            document.getElementById('delete_order_client').textContent = 'Помилка завантаження';
        });
}

function closeDeleteOrderModal() {
    const modal = document.getElementById('deleteOrderModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function confirmDeleteOrder() {
    const form = document.getElementById('deleteOrderForm');
    if (form) {
        form.submit();
    }
}