function openEditProductModal(id, name, description, categoryId, price, stock, isActive, imageUrl, imageName) {
    const modal = document.getElementById('editProductModal');
    const form = document.getElementById('editProductForm');

    form.action = `/products/${id}/update/`;

    document.getElementById('edit_product_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_description').value = description || '';
    document.getElementById('edit_category').value = categoryId;
    document.getElementById('edit_price').value = parseFloat(price).toFixed(2);
    document.getElementById('edit_stock').value = stock;
    document.getElementById('edit_is_active').checked = isActive;

    updateDisplayValues(name, categoryId, price, stock, isActive);

    handleImageDisplay(imageUrl, imageName);

    modal.classList.remove('hidden');
}

function updateDisplayValues(name, categoryId, price, stock, isActive) {
    const displayName = document.getElementById('display_name');
    const displayCategory = document.getElementById('display_category');
    const displayPrice = document.getElementById('display_price');
    const displayStock = document.getElementById('display_stock');
    const displayIsActive = document.getElementById('display_is_active');

    if (displayName) displayName.textContent = name;
    if (displayPrice) displayPrice.textContent = parseFloat(price).toFixed(2);

    if (displayStock) {
        displayStock.textContent = stock;
        if (stock > 10) {
            displayStock.className = 'font-semibold text-green-600 text-base';
        } else if (stock > 0) {
            displayStock.className = 'font-semibold text-yellow-600 text-base';
        } else {
            displayStock.className = 'font-semibold text-red-600 text-base';
        }
    }

    if (displayIsActive) {
        displayIsActive.textContent = isActive ? '✅ Активний' : '❌ Неактивний';
    }

    if (displayCategory) {
        const categorySelect = document.getElementById('edit_category');
        const selectedOption = categorySelect.options[categorySelect.selectedIndex];
        if (selectedOption && selectedOption.value) {
            displayCategory.textContent = selectedOption.text;
        }
    }
}

function handleImageDisplay(imageUrl, imageName) {
    const currentImageContainer = document.getElementById('current_image_container');
    const currentImagePreview = document.getElementById('current_image_preview');
    const currentImageName = document.getElementById('current_image_name');

    clearEditImage();
    document.getElementById('remove_image').value = 'false';

    if (imageUrl && imageUrl !== 'null' && imageUrl !== null && imageUrl !== 'undefined' && imageUrl !== '') {
        console.log('✅ Показуємо Cloudinary зображення');
        currentImagePreview.src = imageUrl;
        currentImageName.textContent = imageName || 'Cloudinary зображення';
        currentImageContainer.classList.remove('hidden');
    } else {
        console.log('❌ Зображення відсутнє');
        currentImageContainer.classList.add('hidden');
    }
}

function closeEditProductModal() {
    const modal = document.getElementById('editProductModal');
    const form = document.getElementById('editProductForm');

    modal.classList.add('hidden');
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
            alert('Будь ласка, виберіть файл зображення!');
            input.value = '';
            return;
        }

        reader.onload = function (e) {
            previewImg.src = e.target.result;
            imageName.textContent = file.name;
            preview.classList.remove('hidden');

            if (currentImageContainer) {
                currentImageContainer.classList.add('hidden');
            }
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

    if (input) input.value = '';
    if (previewImg) previewImg.src = '';
    if (imageName) imageName.textContent = '';
    if (preview) preview.classList.add('hidden');

    const currentImage = document.getElementById('current_image_preview');
    if (currentImage && currentImage.src && document.getElementById('remove_image').value !== 'true') {
        if (currentImageContainer) currentImageContainer.classList.remove('hidden');
    }
}

function removeCurrentImage() {
    if (confirm('Видалити поточне зображення?')) {
        const currentImageContainer = document.getElementById('current_image_container');
        const removeImageInput = document.getElementById('remove_image');

        currentImageContainer.classList.add('hidden');
        removeImageInput.value = 'true';

    }
}

function openNewProductModal() {
    const modal = document.getElementById('newProductModal');
    modal.classList.remove('hidden');
}

function closeNewProductModal() {
    const modal = document.getElementById('newProductModal');
    const form = modal.querySelector('form');

    modal.classList.add('hidden');
    form.reset();
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
            alert('Будь ласка, виберіть файл зображення!');
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

    if (input) input.value = '';
    if (previewImg) previewImg.src = '';
    if (imageName) imageName.textContent = '';
    if (preview) preview.classList.add('hidden');
}

function confirmDelete(productId, productName) {
    const modal = document.getElementById('deleteProductModal');
    const form = document.getElementById('deleteProductForm');
    const nameSpan = document.getElementById('delete_product_name');

    if (modal && form && nameSpan) {
        form.action = `/products/${productId}/delete/`;
        nameSpan.textContent = productName;
        modal.classList.remove('hidden');
    }
}

function closeDeleteProductModal() {
    const modal = document.getElementById('deleteProductModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}