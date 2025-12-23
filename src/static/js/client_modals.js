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
    isActive
) {
    console.log('Opening edit modal for client:', clientId);

    document.getElementById('edit_client_id').value = clientId;
    document.getElementById('edit_first_name').value = firstName;
    document.getElementById('edit_last_name').value = lastName;
    document.getElementById('edit_phone').value = phone;
    document.getElementById('edit_email').value = email || '';
    document.getElementById('edit_address').value = address || '';
    document.getElementById('edit_city').value = city || '';
    document.getElementById('edit_notes').value = notes || '';

    document.getElementById('edit_client_type').value = isVip ? 'vip' : 'regular';

    document.getElementById('edit_is_active').checked = isActive;

    document.getElementById('editClientModal').classList.remove('hidden');

    document.body.style.overflow = 'hidden';
}

function closeEditClientModal() {
    document.getElementById('editClientModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

document.getElementById('editClientForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const clientId = document.getElementById('edit_client_id').value;
    const formData = new FormData(this);

    console.log('Submitting edit form for client:', clientId);

    const clientType = formData.get('client_type');
    formData.set('is_vip', clientType === 'vip' ? 'on' : '');
    formData.delete('client_type');

    fetch(`/clients/${clientId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            console.log('Response status:', response.status);
            if (response.ok) {
                // Success - reload the page to show updated data
                window.location.reload();
            } else {
                // Try to parse error message
                return response.text().then(text => {
                    console.error('Error response:', text);
                    alert('Помилка: Не вдалося оновити клієнта');
                });
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Сталася помилка при збереженні');
        });
});

function confirmDeleteClient(clientId, clientName, clientPhone) {
    console.log('Opening delete modal for client:', clientId);

    const deleteModal = document.getElementById('deleteClientModal');
    if (!deleteModal) {
        console.error('Delete modal not found in DOM');
        alert('Модальне вікно видалення не знайдено');
        return;
    }

    const deleteIdInput = document.getElementById('delete_client_id');
    const deleteNameSpan = document.getElementById('delete_client_name');
    const deletePhoneSpan = document.getElementById('delete_client_phone');

    if (!deleteIdInput || !deleteNameSpan || !deletePhoneSpan) {
        console.error('Delete modal elements not found');
        alert('Елементи модального вікна не знайдені');
        return;
    }

    deleteIdInput.value = clientId;
    deleteNameSpan.textContent = clientName;
    deletePhoneSpan.textContent = clientPhone;

    deleteModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeDeleteClientModal() {
    const deleteModal = document.getElementById('deleteClientModal');
    if (deleteModal) {
        deleteModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

document.getElementById('deleteClientForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const clientId = document.getElementById('delete_client_id').value;
    const formData = new FormData(this);

    console.log('Submitting delete form for client:', clientId);

    fetch(`/clients/${clientId}/delete/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            console.log('Delete response status:', response.status);
            if (response.ok || response.redirected) {
                // Success - redirect to clients list
                window.location.href = '/clients/';
            } else {
                return response.text().then(text => {
                    console.error('Delete error response:', text);
                    alert('Помилка: Не вдалося видалити клієнта');
                });
            }
        })
        .catch(error => {
            console.error('Delete fetch error:', error);
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
