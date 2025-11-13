// Configuration Firebase
const FIREBASE_URL = 'https://chicken-hot-dreux-default-rtdb.europe-west1.firebasedatabase.app';

let orders = {};

// Fonction pour formater la date/heure
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Fonction pour déterminer la classe CSS du type de service
function getTypeClass(typeService) {
    if (typeService === 'Livraison') return 'type-livraison';
    if (typeService === 'À emporter') return 'type-emporter';
    if (typeService === 'Sur place') return 'type-surplace';
    return 'type-default';
}

// Fonction pour créer le HTML d'une commande
function createOrderHTML(orderId, order) {
    const typeService = order.type_service || 'Non spécifié';
    const isDelivery = typeService === 'Livraison';
    
    // Affichage conditionnel du téléphone et de l'adresse
    let contactHTML = '';
    if (isDelivery) {
        contactHTML = `
            <div class="contact-info">
                ${order.phone_number && order.phone_number !== 'Non fourni' ? `
                    <p><strong>📞 Téléphone:</strong> <span class="phone-number">${order.phone_number}</span></p>
                ` : ''}
                ${order.formatted_address || order.delivery_address ? `
                    <p><strong>📍 Adresse:</strong> <span class="delivery-address">${order.formatted_address || order.delivery_address}</span></p>
                ` : ''}
                ${order.distance_km > 0 ? `
                    <p class="distance">Distance: ${order.distance_km} km</p>
                ` : ''}
            </div>
        `;
    }
    
    // Items
    const itemsHTML = order.items.map(item => `
        <div class="item">
            <span class="item-name">
                <span class="item-quantity">${item.quantity}×</span>
                ${item.name}
            </span>
            <span class="item-price">${item.total_price.toFixed(2)}€</span>
        </div>
    `).join('');
    
    // Frais de livraison (seulement si livraison)
    let deliveryFeeHTML = '';
    if (isDelivery) {
        if (order.delivery_fee_waived) {
            deliveryFeeHTML = `
                <div class="price-row delivery-free">
                    <span>Frais de livraison (offerts)</span>
                    <span>0.00€</span>
                </div>
            `;
        } else if (order.delivery_fee > 0) {
            deliveryFeeHTML = `
                <div class="price-row delivery-fee">
                    <span>Frais de livraison</span>
                    <span>+${order.delivery_fee.toFixed(2)}€</span>
                </div>
            `;
        }
    }
    
    // Notes
    const notesHTML = order.notes && order.notes !== '' ? `
        <div class="order-notes">
            <p><strong>📝 Notes:</strong> ${order.notes}</p>
        </div>
    ` : '';
    
    return `
        <div class="order-card" data-type="${typeService}" data-id="${orderId}">
            <div class="order-header">
                <span class="order-time">${formatDateTime(order.timestamp)}</span>
                <span class="status-badge status-${order.status || 'pending'}">
                    ${order.status === 'completed' ? 'Terminée' : 'Nouvelle'}
                </span>
            </div>
            
            <div class="order-type ${getTypeClass(typeService)}">
                ${typeService}
            </div>
            
            ${contactHTML}
            
            <div class="order-items">
                ${itemsHTML}
            </div>
            
            <div class="order-pricing">
                <div class="price-row subtotal">
                    <span>Sous-total</span>
                    <span>${order.subtotal.toFixed(2)}€</span>
                </div>
                ${deliveryFeeHTML}
                <div class="price-row total">
                    <span>TOTAL</span>
                    <span>${order.total.toFixed(2)}€</span>
                </div>
            </div>
            
            ${notesHTML}
        </div>
    `;
}

// Fonction pour mettre à jour une commande existante ou l'ajouter
function updateOrderElement(orderId, order) {
    const container = document.getElementById('orders-container');
    const existingCard = container.querySelector(`[data-id="${orderId}"]`);
    
    const newHTML = createOrderHTML(orderId, order);
    
    if (existingCard) {
        // Mettre à jour la carte existante sans la faire disparaître
        existingCard.outerHTML = newHTML;
    } else {
        // Nouvelle commande - l'ajouter au début
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newHTML;
        container.insertBefore(tempDiv.firstElementChild, container.firstChild);
        
        // Son de notification pour nouvelle commande
        playNotificationSound();
    }
}

// Fonction pour supprimer les commandes qui n'existent plus
function removeDeletedOrders(currentOrderIds) {
    const container = document.getElementById('orders-container');
    const existingCards = container.querySelectorAll('.order-card');
    
    existingCards.forEach(card => {
        const orderId = card.getAttribute('data-id');
        if (!currentOrderIds.includes(orderId)) {
            card.remove();
        }
    });
}

// Fonction pour afficher toutes les commandes (initialisation)
function displayAllOrders() {
    const container = document.getElementById('orders-container');
    
    if (Object.keys(orders).length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>🍗 En attente de commandes...</h2>
                <p>Les nouvelles commandes apparaîtront automatiquement ici</p>
            </div>
        `;
        return;
    }
    
    // Supprimer le message "empty state" s'il existe
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Trier les commandes par date (plus récentes en premier)
    const sortedOrders = Object.entries(orders)
        .sort((a, b) => new Date(b[1].timestamp) - new Date(a[1].timestamp));
    
    // Mettre à jour ou ajouter chaque commande
    sortedOrders.forEach(([id, order]) => {
        updateOrderElement(id, order);
    });
    
    // Supprimer les commandes qui n'existent plus
    const currentOrderIds = sortedOrders.map(([id]) => id);
    removeDeletedOrders(currentOrderIds);
}

// Fonction pour écouter les nouvelles commandes en temps réel
function listenToOrders() {
    const ordersRef = `${FIREBASE_URL}/orders.json`;
    
    // Première récupération
    fetch(ordersRef)
        .then(response => response.json())
        .then(data => {
            if (data) {
                orders = data;
                displayAllOrders();
            }
        })
        .catch(error => {
            console.error('Erreur de chargement:', error);
        });
    
    // Polling toutes les 3 secondes pour les mises à jour
    setInterval(() => {
        fetch(ordersRef)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    orders = data;
                    displayAllOrders();
                }
            })
            .catch(error => {
                console.error('Erreur de mise à jour:', error);
            });
    }, 3000);
}

// Fonction pour jouer un son de notification (optionnel)
function playNotificationSound() {
    // Vibration si supportée
    if ('vibrate' in navigator) {
        navigator.vibrate(200);
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    console.log('🍗 Chicken Hot Dreux - Interface chargée');
    listenToOrders();
});
