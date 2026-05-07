const API_URL = 'http://localhost:8000';
let currentUser = null;
let token = localStorage.getItem('foodhub_token');
let cart = {}; // { menuId: { item: {}, quantity: 1 } }
let defaultCategoryId = 1; // Disimpan untuk kemudahan tambah menu

// Format Rupiah
const formatRp = (angka) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka);
};

// UI Toggling
function switchAuthTab(tab) {
    document.getElementById('tab-login').classList.remove('active');
    document.getElementById('tab-register').classList.remove('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    if (tab === 'login') {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
    } else {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
    }
}

function showAuth() {
    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('hidden');
}

function hideAuth() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
}

function updateAuthUI() {
    if (currentUser) {
        document.getElementById('header-login-btn').classList.add('hidden');
        document.getElementById('header-logout-btn').classList.remove('hidden');
        document.getElementById('user-greeting').classList.remove('hidden');
        document.getElementById('user-greeting').textContent = `Halo, ${currentUser.username}`;
        document.getElementById('admin-menu-section').classList.remove('hidden');
        document.getElementById('order-history-section').classList.remove('hidden');
        hideAuth();
        loadOrders();
    } else {
        document.getElementById('header-login-btn').classList.remove('hidden');
        document.getElementById('header-logout-btn').classList.add('hidden');
        document.getElementById('user-greeting').classList.add('hidden');
        document.getElementById('admin-menu-section').classList.add('hidden');
        document.getElementById('order-history-section').classList.add('hidden');
    }
}

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    if (isError) toast.classList.add('error');
    else toast.classList.remove('error');
    
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// Initial Load Check
window.onload = async () => {
    ensureDefaultCategory();
    loadMenus(); // Load menus immediately for guests
    if (token) {
        await checkAuth();
    } else {
        updateAuthUI();
    }
};

async function checkAuth() {
    try {
        const res = await fetch(`${API_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            currentUser = await res.json();
            updateAuthUI();
        } else {
            logout();
        }
    } catch (e) {
        console.error("Gagal verifikasi token", e);
        updateAuthUI();
    }
}

function logout() {
    localStorage.removeItem('foodhub_token');
    token = null;
    currentUser = null;
    cart = {};
    renderCart();
    updateAuthUI();
    showToast("Berhasil logout");
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            body: formData // OAuth2 Password form requires FormData
        });
        const data = await res.json();
        
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem('foodhub_token', token);
            showToast('Login berhasil!');
            await checkAuth();
        } else {
            showToast(data.detail || 'Login gagal', true);
        }
    } catch (e) {
        showToast('Kesalahan jaringan', true);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const payload = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        full_name: document.getElementById('reg-fullname').value,
        password: document.getElementById('reg-password').value
    };

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast('Registrasi berhasil! Silakan login.');
            switchAuthTab('login');
            document.getElementById('login-username').value = payload.username;
        } else {
            showToast(data.detail || 'Registrasi gagal', true);
        }
    } catch (e) {
        showToast('Kesalahan jaringan', true);
    }
}

// Menus & Categories
async function ensureDefaultCategory() {
    try {
        const res = await fetch(`${API_URL}/categories`);
        const cats = await res.json();
        if (cats.length === 0) {
            const createRes = await fetch(`${API_URL}/categories`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: "Menu Utama", description: "Default Kategori" })
            });
            const newCat = await createRes.json();
            defaultCategoryId = newCat.id;
        } else {
            defaultCategoryId = cats[0].id;
        }
    } catch (e) {
        console.error("Gagal cek kategori", e);
    }
}

async function loadMenus() {
    try {
        const res = await fetch(`${API_URL}/menus`);
        const menus = await res.json();
        const container = document.getElementById('menu-container');
        container.innerHTML = '';
        
        if (menus.length === 0) {
            container.innerHTML = '<div style="color:var(--text-muted)">Belum ada menu tersedia.</div>';
            return;
        }

        menus.forEach(item => {
            const div = document.createElement('div');
            div.className = 'menu-item';
            div.innerHTML = `
                <h3 style="margin-bottom:0">${item.name}</h3>
                <div class="price">${formatRp(item.price)}</div>
                <button class="btn" onclick="addToCart(${item.id}, '${item.name}', ${item.price})">+ Tambah ke Keranjang</button>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        showToast('Gagal memuat menu', true);
    }
}

async function handleAddMenu(e) {
    e.preventDefault();
    const name = document.getElementById('new-menu-name').value;
    const price = parseFloat(document.getElementById('new-menu-price').value);

    try {
        const res = await fetch(`${API_URL}/menus`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                price: price,
                category_id: defaultCategoryId
            })
        });
        
        if (res.ok) {
            showToast('Menu berhasil ditambahkan!');
            document.getElementById('add-menu-form').reset();
            loadMenus();
        } else {
            const err = await res.json();
            showToast(err.detail || 'Gagal tambah menu', true);
        }
    } catch (e) {
        showToast('Kesalahan jaringan', true);
    }
}

// Cart Logic
function addToCart(id, name, price) {
    if (cart[id]) {
        cart[id].quantity += 1;
    } else {
        cart[id] = { id, name, price, quantity: 1 };
    }
    renderCart();
    showToast(`${name} masuk keranjang!`);
}

function removeFromCart(id) {
    if (cart[id]) {
        cart[id].quantity -= 1;
        if (cart[id].quantity <= 0) {
            delete cart[id];
        }
        renderCart();
    }
}

function renderCart() {
    const container = document.getElementById('cart-container');
    const totalSection = document.getElementById('cart-total-section');
    const checkoutBtn = document.getElementById('checkout-btn');
    const totalPriceEl = document.getElementById('cart-total-price');
    
    container.innerHTML = '';
    let total = 0;
    let hasItems = false;

    Object.values(cart).forEach(item => {
        hasItems = true;
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div>
                <div style="font-weight: 600">${item.name}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted)">${formatRp(item.price)} x ${item.quantity}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-weight: 700">${formatRp(itemTotal)}</span>
                <button onclick="removeFromCart(${item.id})" style="background:var(--accent); color:white; border:none; border-radius:50%; width:24px; height:24px; cursor:pointer;">-</button>
            </div>
        `;
        container.appendChild(div);
    });

    if (hasItems) {
        totalSection.classList.remove('hidden');
        checkoutBtn.classList.remove('hidden');
        totalPriceEl.textContent = formatRp(total);
    } else {
        container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">Keranjang kosong.</div>';
        totalSection.classList.add('hidden');
        checkoutBtn.classList.add('hidden');
    }
}

// Ordering
async function handleCheckout() {
    if (!currentUser || !currentUser.id) {
        showToast('Silakan login terlebih dahulu untuk membuat pesanan!', true);
        showAuth();
        return;
    }

    const items = Object.values(cart).map(i => ({
        menu_item_id: i.id,
        quantity: i.quantity
    }));

    try {
        const res = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser.id,
                items: items
            })
        });

        if (res.ok) {
            showToast('Pesanan berhasil dibuat! Sedang diproses...');
            cart = {};
            renderCart();
            loadOrders();
        } else {
            const data = await res.json();
            showToast(data.detail || 'Gagal membuat pesanan', true);
        }
    } catch (e) {
        showToast('Kesalahan jaringan saat checkout', true);
    }
}

async function loadOrders() {
    if (!currentUser) return;
    try {
        const res = await fetch(`${API_URL}/orders?user_id=${currentUser.id}`);
        const orders = await res.json();
        const container = document.getElementById('order-history');
        container.innerHTML = '';
        
        if (orders.length === 0) {
            container.innerHTML = '<div style="color:var(--text-muted); font-size: 0.9rem;">Belum ada pesanan.</div>';
            return;
        }

        orders.reverse().forEach(order => {
            const date = new Date(order.created_at).toLocaleString('id-ID');
            const div = document.createElement('div');
            div.style.padding = '1rem 0';
            div.style.borderBottom = '1px solid var(--border)';
            
            let statusColor = 'var(--text-muted)';
            if (order.status === 'completed') statusColor = '#10b981';
            
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <strong style="color: var(--primary)">Order #${order.id}</strong>
                    <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; color: ${statusColor}">${order.status.toUpperCase()}</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">${date}</div>
                <div style="display: flex; justify-content: space-between; font-weight: 700;">
                    <span>Total Bayar:</span>
                    <span>${formatRp(order.total_amount)}</span>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Gagal load order history");
    }
}
