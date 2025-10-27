document.addEventListener('DOMContentLoaded', () => {

  // Populate Edit modal
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = document.getElementById('edit-popup');
      modal.querySelector('#edit-id').value = btn.dataset.id;
      modal.querySelector('#edit-sku').value = btn.dataset.sku;
      modal.querySelector('#edit-name').value = btn.dataset.name;
      modal.querySelector('#edit-price').value = btn.dataset.price;
      modal.querySelector('#edit-stock').value = btn.dataset.stock;
      modal.querySelector('#edit-category').value = btn.dataset.category;
      modal.querySelector('#edit-description').value = btn.dataset.description;
    });
  });

  // Submit Edit
  document.getElementById('edit-product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const data = {
      sku: document.getElementById('edit-sku').value,
      name: document.getElementById('edit-name').value,
      price: parseFloat(document.getElementById('edit-price').value),
      stock: parseInt(document.getElementById('edit-stock').value),
      category_id: parseInt(document.getElementById('edit-category').value),
      description: document.getElementById('edit-description').value
    };
    const res = await fetch(`/api/admin/products/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) showToast('Thành công', 'Cập nhật sản phẩm thành công', 'success');
    else alert('Cập nhật thất bại');
  });

  // Populate Delete modal
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = document.getElementById('delete-popup');
      modal.querySelector('#delete-id').value = btn.dataset.id;
      modal.querySelector('#delete-name').textContent = btn.dataset.name;
    });
  });

  // Submit Delete
  document.getElementById('delete-product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('delete-id').value;
    const res = await fetch(`/api/admin/products/${id}`, {
      method: 'DELETE'
    });
    if (res.ok) showToast('Thành công', 'Xóa sản phẩm thành công', 'success');
    else alert('Xóa thất bại');
  });


  // Submit Add Product
document.getElementById('add-product-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const data = {
    sku: document.getElementById('add-sku').value,
    name: document.getElementById('add-name').value,
    price: parseFloat(document.getElementById('add-price').value),
    stock: parseInt(document.getElementById('add-stock').value),
    category_id: parseInt(document.getElementById('add-category').value),
    description: document.getElementById('add-description').value
  };

  try {
    const res = await fetch('/api/admin/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      showToast('Thành công', 'Thêm sản phẩm mới thành công', 'success');
    } else {
      const err = await res.json();
      showToast('Lỗi', err.message || 'Thêm sản phẩm thất bại', 'error');
    }
  } catch (err) {
    showToast('Lỗi', 'Không thể kết nối tới server', 'error');
  }
});

});
