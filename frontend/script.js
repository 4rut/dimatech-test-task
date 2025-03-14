function showSection(sectionId) {
  const sections = document.querySelectorAll('main section');
  sections.forEach(sec => sec.classList.add('hidden'));
  document.getElementById(sectionId).classList.remove('hidden');
}

let currentUserId = null;
let currentAdminId = null;

async function userLogin(event) {
  event.preventDefault();
  const email = document.getElementById('user-email').value;
  const password = document.getElementById('user-password').value;
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  const data = await res.json();
  if (res.ok) {
    currentUserId = data.id;
    document.getElementById('user-info').innerText = `Вы вошли как ${data.full_name} (${data.email})`;
    document.querySelector('#user .card').classList.add('hidden'); // скрыть форму логина
    document.getElementById('user-data').classList.remove('hidden');
  } else {
    alert(data.detail || 'Ошибка авторизации');
  }
}

async function fetchUserAccounts() {
  const res = await fetch('/user/accounts', {
    headers: {'X-User-ID': currentUserId}
  });
  const accounts = await res.json();
  const list = document.getElementById('accounts-list');
  list.innerHTML = '';
  accounts.forEach(acc => {
    const li = document.createElement('li');
    li.innerText = `Счет ID: ${acc.id}, Баланс: ${acc.balance}`;
    list.appendChild(li);
  });
}

async function fetchUserPayments() {
  const res = await fetch('/user/payments', {
    headers: {'X-User-ID': currentUserId}
  });
  const payments = await res.json();
  const list = document.getElementById('payments-list');
  list.innerHTML = '';
  payments.forEach(p => {
    const li = document.createElement('li');
    li.innerText = `Transaction: ${p.transaction_id}, Amount: ${p.amount}, Date: ${p.created_at}`;
    list.appendChild(li);
  });
}

async function adminLogin(event) {
  event.preventDefault();
  const email = document.getElementById('admin-email').value;
  const password = document.getElementById('admin-password').value;
  const res = await fetch('/admin/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  const data = await res.json();
  if (res.ok) {
    currentAdminId = data.id;
    document.getElementById('admin-info').innerText = `Вы вошли как ${data.full_name} (${data.email})`;
    document.querySelector('#admin .card').classList.add('hidden'); // скрыть форму логина
    document.getElementById('admin-data').classList.remove('hidden');
  } else {
    alert(data.detail || 'Ошибка авторизации');
  }
}

async function fetchUsers() {
  const res = await fetch('/admin/users');
  const users = await res.json();
  const list = document.getElementById('users-list');
  list.innerHTML = '';
  users.forEach(u => {
    const li = document.createElement('li');
    li.innerText = `ID: ${u.id}, Name: ${u.full_name}, Email: ${u.email}, Role: ${u.role}`;
    list.appendChild(li);
  });
}

async function sendWebhook(event) {
  event.preventDefault();
  const transaction_id = document.getElementById('wh-transaction-id').value;
  const user_id = Number(document.getElementById('wh-user-id').value);
  const account_id = Number(document.getElementById('wh-account-id').value);
  const amount = Number(document.getElementById('wh-amount').value);

  if (user_id < 0 || account_id < 0 || amount < 0) {
    alert("User ID, Account ID и Amount не могут быть меньше нуля");
    return;
  }

  const secret_key = 'gfdmhghif38yrf9ew0jkf32';
  const stringToHash = `${account_id}${amount}${transaction_id}${user_id}${secret_key}`;
  const signature = await sha256(stringToHash);

  const res = await fetch('/webhook/payment', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({transaction_id, user_id, account_id, amount, signature})
  });
  const data = await res.json();
  document.getElementById('webhook-result').innerText = JSON.stringify(data);
}

async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
