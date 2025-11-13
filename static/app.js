// Configuration Firebase - À REMPLACER avec tes vraies valeurs
const firebaseConfig = {
  apiKey: "AIzaSyDwcFMTbMUWaxD8bauWsjWbORyXMu3SSpM",
  authDomain: "chicken-hot-dreux.firebaseapp.com",
  databaseURL: "https://chicken-hot-dreux-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "chicken-hot-dreux",
  storageBucket: "chicken-hot-dreux.firebasestorage.app",
  messagingSenderId: "681275425785",
  appId: "1:681275425785:web:564d2f96ba3dcce0913328",
  measurementId: "G-ETLFE74H4G"
};

// Initialiser Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

let currentOrders = {};
let lastOrderTime = 0;

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatPrice(price) {
    return typeof price === 'number' ? price.toFixed(2) : '0.00';
}

function createOrderCard(orderId, order) {
    const isNew = new Date(order.timestamp).getTime() > lastOrderTime;
    
    const deliveryFeeDisplay = order.delivery_fee_waived 
        ? `<span class="free-badge">GRATUIT</span>` 
        : `${formatPrice(order.delivery_fee)}€`;

    const addressClass = order.address_verified ? 'address-verified' : 'address-unverified';
    const addressIcon = order.address_verified ? '✓' : '⚠';
    
    return `
        <div class="order-card ${isNew ? 'new' : ''}" id="order-${orderId}">
            <div class="order-header">
                <div class="order-time">${formatDate(order.timestamp)}</div>
                <div class="order-status">Nouvelle</div>
            </div>

            <div class="customer-info">
                <div class="info-row">
                    <span class="info-label">📞 Téléphone:</span>
                    <span class="info-value phone-number">${order.phone_number || 'Non fourni'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">${addressIcon} Adresse:</span>
                    <span class="info-value ${addressClass}">${order.formatted_address || order.delivery_address || 'Non fournie'}</span>
                </div>
                ${order.distance_km > 0 ? `
                <div class="info-row">
                    <span class="info-label">📍 Distance:</span>
                    <span class="info-value distance">${order.distance_km} km</span>
                </div>
                ` : ''}
            </div>

            <div class="items-list">
                ${order.items.map(item => `
                    <div class="item">
                        <span>
                            <span class="item-quantity">${item.quantity}x</span>
                            <span class="item-name">${item.name}</span>
                        </span>
                        <span class="item-price">${formatPrice(item.total_price)}€</span>
                    </div>
                `).join('')}
            </div>

            <div class="order-total">
                <div class="total-row subtotal">
                    <span>Sous-total:</span>
                    <span>${formatPrice(order.subtotal)}€</span>
                </div>
                <div class="total-row delivery ${order.delivery_fee_waived ? 'free' : ''}">
                    <span>Frais de livraison:</span>
                    <span>${deliveryFeeDisplay}</span>
                </div>
                <div class="total-row final">
                    <span>TOTAL:</span>
                    <span>${formatPrice(order.total)}€</span>
                </div>
            </div>

            ${order.notes ? `
                <div class="notes">
                    <strong>📝 Notes:</strong> ${order.notes}
                </div>
            ` : ''}
        </div>
    `;
}

function renderOrders() {
    const ordersContainer = document.getElementById('orders');
    const noOrdersDiv = document.getElementById('no-orders');
    const loadingDiv = document.getElementById('loading');
    
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    const orderEntries = Object.entries(currentOrders);
    
    if (orderEntries.length === 0) {
        ordersContainer.innerHTML = '';
        if (noOrdersDiv) noOrdersDiv.style.display = 'block';
        return;
    }
    
    if (noOrdersDiv) noOrdersDiv.style.display = 'none';
    
    // Trier par timestamp décroissant
    orderEntries.sort((a, b) => {
        return new Date(b[1].timestamp) - new Date(a[1].timestamp);
    });
    
    ordersContainer.innerHTML = orderEntries
        .map(([id, order]) => createOrderCard(id, order))
        .join('');
    
    // Mettre à jour le dernier timestamp
    lastOrderTime = Math.max(lastOrderTime, 
        ...orderEntries.map(([_, order]) => new Date(order.timestamp).getTime())
    );
}

// Écouter les changements en temps réel
const ordersRef = database.ref('orders');

ordersRef.on('value', (snapshot) => {
    if (snapshot.exists()) {
        currentOrders = snapshot.val();
        renderOrders();
    } else {
        currentOrders = {};
        renderOrders();
    }
}, (error) => {
    console.error('Erreur Firebase:', error);
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.textContent = 'Erreur de connexion: ' + error.message;
        errorDiv.style.display = 'block';
    }
});

// Notification sonore pour nouvelles commandes
const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSiJ0fPTgjMGHm7A7+OZRQ0PVqzn77BdGAo+ltryxnUrBSp+zPPaizsIGGS57OihUBELTKXh8bllHAU2jdXzzn0pBSh4yPDejkILEVu16+yiVBMKRp/g8r9uIQUrhM/z24U3Bhxqvu7mnEgODlSq5++wYBkKPJPY8sl3KgUqfsrz2Ys5CBdlu+zpoVIRDEqj4PK8aR0FNIzU8859KQUpeMnw3oxDCxFZs+rsoVQTCkSe3/G/bSIFKYLN8txBNQYbab3t56FGDg1Sq+Xwr18aCjuR1/LJdioFKn7J8tmLOwgXZLns6aFSEQxKo+DyvGkdBTSM1PLPfCkFKXjJ8N6MQwsRWbPq7KFUEwpEnt/xwW0iBCmCzfPcQTUGG2m87OahRw4NUqvl8K9fGgo7kdbyynYqBSp+yPLaizsIF2S57OmhUhEMSqPg8rxpHQU0jNTyz3wpBSl4yfDejEMLEVmz6uyhVBMKRJ7f8cFtIgQpgs3z3EE1Bhtpve7noUcODVKr5fCvXxoKO5HW8sp2KgUqfsny2os7CBdkuexxZWxlcXNjbHNkZmdoamtsbmxsZ2VlZGRhYV9dXl1bWllZWFdXVlVUU1JSUVBPTk1MSUhHRkRDQkE/Pj07Ojg3NTQyMTAvLi0sKyopKCYlJCMiISAfHR0dHBwaGhkXFhUVExIREBAPDg0NDAsLCgoICQgHBgUFBAMDAgEBAQA=');

let firstLoad = true;
let previousOrderCount = 0;

function playNotificationSound() {
    if (!firstLoad) {
        audio.play().catch(e => console.log('Erreur son:', e));
    }
    firstLoad = false;
}

// Jouer un son lors d'une nouvelle commande
ordersRef.on('value', (snapshot) => {
    if (snapshot.exists()) {
        const orderCount = Object.keys(snapshot.val()).length;
        if (orderCount > previousOrderCount && previousOrderCount > 0) {
            playNotificationSound();
        }
        previousOrderCount = orderCount;
    }
});

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    console.log('🍗 Chicken Hot Dreux - Interface chargée');
});
