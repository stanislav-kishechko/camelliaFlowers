function openNewProductModal() {
    document.getElementById('newProductModal').classList.remove('hidden');
}

function closeNewProductModal() {
    document.getElementById('newProductModal').classList.add('hidden');
    document.querySelector('#newProductModal form').reset();
    clearNewProductImage();
}

function previewNewProductImage(input) {
    const preview = document.getElementById('new_product_image_preview');
    const previewImg = document.getElementById('new_product_preview_img');
    const imageName = document.getElementById('new_product_image_name');

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const file = input.files[0];

        if (file.size > 5 * 1024 * 1024) {
            alert('Файл занадто великий! Максимальний розмір: 5MB');
            input.value = '';
            return;
        }

        if (!file.type.match('image.*')) {
            alert('Будь ласка, оберіть файл зображення');
            input.value = '';
            return;
        }

        reader.onload = function (e) {
            previewImg.src = e.target.result;
            imageName.textContent = file.name;
            preview.classList.remove('hidden');
        };

        reader.readAsDataURL(file);
    }
}

function clearNewProductImage() {
    const input = document.getElementById('new_product_image_input');
    const preview = document.getElementById('new_product_image_preview');
    const previewImg = document.getElementById('new_product_preview_img');
    const imageName = document.getElementById('new_product_image_name');

    input.value = '';
    previewImg.src = '';
    imageName.textContent = '';
    preview.classList.add('hidden');
}

function openEditProductModal(id, name, description, categoryId, price, stock, isActive, imageUrl, imageName) {
    const modal = document.getElementById('editProductModal');
    const form = document.getElementById('editProductForm');

    form.action = `/products/${id}/update/`;

    document.getElementById('edit_product_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_description').value = description || '';
    document.getElementById('edit_category').value = categoryId;
    document.getElementById('edit_price').value = price;
    document.getElementById('edit_stock').value = stock;
    document.getElementById('edit_is_active').checked = isActive;

    clearEditImage();
    document.getElementById('remove_image').value = 'false';

    const currentImageContainer = document.getElementById('current_image_container');
    const currentImagePreview = document.getElementById('current_image_preview');
    const currentImageName = document.getElementById('current_image_name');

    if (imageUrl && imageUrl !== 'null') {
        currentImagePreview.src = imageUrl;
        currentImageName.textContent = imageName || 'Поточне зображення';
        currentImageContainer.classList.remove('hidden');
    } else {
        currentImageContainer.classList.add('hidden');
    }

    modal.classList.remove('hidden');
}

function closeEditProductModal() {
    const modal = document.getElementById('editProductModal');
    modal.classList.add('hidden');

    const form = document.getElementById('editProductForm');
    form.reset();
    clearEditImage();
    document.getElementById('remove_image').value = 'false';
    document.getElementById('current_image_container').classList.add('hidden');
}

function previewEditImage(input) {
    const preview = document.getElementById('edit_image_preview');
    const previewImg = document.getElementById('edit_preview_img');
    const imageName = document.getElementById('edit_image_name');
    const currentImageContainer = document.getElementById('current_image_container');

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const file = input.files[0];

        if (file.size > 5 * 1024 * 1024) {
            alert('Файл занадто великий! Максимальний розмір: 5MB');
            input.value = '';
            return;
        }

        if (!file.type.match('image.*')) {
            alert('Будь ласка, оберіть файл зображення');
            input.value = '';
            return;
        }

        reader.onload = function (e) {
            previewImg.src = e.target.result;
            imageName.textContent = file.name;
            preview.classList.remove('hidden');
            currentImageContainer.classList.add('hidden');
        };

        reader.readAsDataURL(file);
    }
}

function clearEditImage() {
    const input = document.getElementById('edit_image_input');
    const preview = document.getElementById('edit_image_preview');
    const previewImg = document.getElementById('edit_preview_img');
    const imageName = document.getElementById('edit_image_name');
    const currentImageContainer = document.getElementById('current_image_container');

    input.value = '';
    previewImg.src = '';
    imageName.textContent = '';
    preview.classList.add('hidden');

    const currentImage = document.getElementById('current_image_preview');
    if (currentImage.src && document.getElementById('remove_image').value !== 'true') {
        currentImageContainer.classList.remove('hidden');
    }
}

function removeCurrentImage() {
    const currentImageContainer = document.getElementById('current_image_container');
    const removeImageInput = document.getElementById('remove_image');

    currentImageContainer.classList.add('hidden');

    removeImageInput.value = 'true';

    const input = document.getElementById('edit_image_input');
    input.value = '';
    clearEditImage();
}

function confirmDelete(productId, productName) {
    const modal = document.getElementById('deleteProductModal');
    const form = document.getElementById('deleteProductForm');
    const productNameSpan = document.getElementById('delete_product_name');

    form.action = `/products/${productId}/delete/`;

    productNameSpan.textContent = productName;

    modal.classList.remove('hidden');
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteProductModal');
    modal.classList.add('hidden');
}

window.onclick = function (event) {
    const newModal = document.getElementById('newProductModal');
    const editModal = document.getElementById('editProductModal');
    const deleteModal = document.getElementById('deleteProductModal');

    if (event.target === newModal) {
        closeNewProductModal();
    }
    if (event.target === editModal) {
        closeEditProductModal();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
};

document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeNewProductModal();
        closeEditProductModal();
        closeDeleteModal();
    }
});