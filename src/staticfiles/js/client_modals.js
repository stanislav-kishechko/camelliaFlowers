// Client Modals JavaScript for Camellia Flowers CRM

/**
 * Open edit client modal with updated statistics
 */
function openEditClientModal(
    clientId,
    firstName,
    lastName,
    phone,
    email,
    address,
    city,
    notes,
    isVip,
    isActive,
    ordersCount,
    totalSpent,
    averageOrder,
    createdAt
) {
    // Fill form fields
    document.getElementById('edit_client_id').value = clientId;
    document.getElementById('edit_first_name').value = firstName;
    document.getElementById('edit_last_name').value = lastName;
    document.getElementById('edit_phone').value = phone;
    document.getElementById('edit_email').value = email || '';
    document.getElementById('edit_address').value = address || '';
    document.getElementById('edit_city').value = city || '';
    document.getElementById('edit_notes').value = notes || '';

    // Set client type (VIP or regular)
    document.getElementById('edit_client_type').value = isVip ? 'vip' : 'regular';

    // Set active status
    document.getElementById('edit_is_active').checked = isActive;

    // Fill statistics with real data
    // Parse strings to numbers for proper formatting
    const parsedOrdersCount = parseInt(ordersCount) || 0;
    const parsedTotalSpent = parseFloat(totalSpent) || 0;
    const parsedAverageOrder = parseFloat(averageOrder) || 0;

    console.log('Statistics received:', {
        ordersCount,
        totalSpent,
        averageOrder
    });

    console.log('Statistics parsed:', {
        parsedOrdersCount,
        parsedTotalSpent,
        parsedAverageOrder
    });

    document.getElementById('edit_orders_count').textContent = parsedOrdersCount;
    document.getElementById('edit_total_spent').textContent = `₴${parsedTotalSpent.toFixed(2)}`;
    document.getElementById('edit_average_order').textContent = `₴${parsedAverageOrder.toFixed(2)}`;
    document.getElementById('edit_created_at').textContent = createdAt || '-';

    // Show modal
    document.getElementById('editClientModal').classList.remove('hidden');

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

/**
 * Close edit client modal
 */
function closeEditClientModal() {
    document.getElementById('editClientModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

/**
 * Handle edit client form submission
 */
document.getElementById('editClientForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const clientId = document.getElementById('edit_client_id').value;

    // Convert client type to is_vip boolean
    const clientType = formData.get('client_type');
    formData.set('is_vip', clientType === 'vip' ? 'on' : '');
    formData.delete('client_type');

    fetch(`/clients/${clientId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                return response.json().then(data => {
                    alert('Помилка: ' + (data.error || 'Не вдалося оновити клієнта'));
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Сталася помилка при збереженні');
        });
});

/**
 * Open delete client confirmation modal
 */
function confirmDeleteClient(clientId, clientName, clientPhone) {
    document.getElementById('delete_client_id').value = clientId;
    document.getElementById('delete_client_name').textContent = clientName;
    document.getElementById('delete_client_phone').textContent = clientPhone;

    document.getElementById('deleteClientModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

/**
 * Close delete client modal
 */
function closeDeleteClientModal() {
    document.getElementById('deleteClientModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

/**
 * Handle delete client form submission
 */
document.getElementById('deleteClientForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const clientId = document.getElementById('delete_client_id').value;

    fetch(`/clients/${clientId}/delete/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
        .then(response => {
            if (response.ok) {
                window.location.href = '/clients/';
            } else {
                return response.json().then(data => {
                    alert('Помилка: ' + (data.error || 'Не вдалося видалити клієнта'));
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Сталася помилка при видаленні');
        });
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeEditClientModal();
        closeDeleteClientModal();
    }
});

document.getElementById('editClientModal')?.addEventListener('click', function (e) {
    if (e.target === this) {
        closeEditClientModal();
    }
});

document.getElementById('deleteClientModal')?.addEventListener('click', function (e) {
    if (e.target === this) {
        closeDeleteClientModal();
    }
});