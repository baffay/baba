// تحديث الوقت
function updateTime() {
    const now = new Date();
    const timeFormatter = new Intl.DateTimeFormat('ar-SA', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    document.getElementById('currentTime').textContent = timeFormatter.format(now);
}

setInterval(updateTime, 1000);
updateTime();

// تنسيق المبالغ
function formatMoney(amount) {
    return new Intl.NumberFormat('ar-SA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// تأثيرات حركية للبطاقات
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('mouseover', () => {
        card.style.transform = 'translateY(-5px)';
    });
    card.addEventListener('mouseout', () => {
        card.style.transform = 'translateY(0)';
    });
});

// التحقق من صحة المدخلات
function validateForm() {
    const amount = document.querySelector('input[name="amount"]').value;
    if (parseFloat(amount) <= 0) {
        alert('المبلغ يجب أن يكون أكبر من صفر');
        return false;
    }
    return true;
}

// إخفاء رسائل التنبيه تلقائياً
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.style.display = 'none';
    });
}, 5000);

// تحديث نمط النموذج حسب نوع العملية
function updateFormStyle(type) {
    const form = document.querySelector('.form-section');
    form.className = 'form-section ' + type;
}

// إدارة النوافذ المنبثقة
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// إغلاق النوافذ المنبثقة عند النقر خارجها
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// تأكيد الحذف
function confirmDelete(message = 'هل أنت متأكد من الحذف؟') {
    return confirm(message);
}

// تصدير البيانات إلى Excel
function exportToExcel(tableId, filename) {
    let table = document.getElementById(tableId);
    let html = table.outerHTML;
    let url = 'data:application/vnd.ms-excel,' + encodeURIComponent(html);
    let downloadLink = document.createElement("a");
    document.body.appendChild(downloadLink);
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// طباعة التقرير
function printReport() {
    window.print();
}