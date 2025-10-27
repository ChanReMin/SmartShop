  function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    toastEl.querySelector('#toast-title').textContent = title;
    toastEl.querySelector('#toast-body').textContent = message;

    // Thay đổi màu theo type
    toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'text-white', 'text-dark');
    if (type === 'success') toastEl.classList.add('bg-success', 'text-white');
    else if (type === 'error') toastEl.classList.add('bg-danger', 'text-white');
    else if (type === 'warning') toastEl.classList.add('bg-warning', 'text-dark');
    else toastEl.classList.add('bg-info', 'text-white');

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  }