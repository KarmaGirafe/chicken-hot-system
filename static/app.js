// Configuration Firebase
const FIREBASE_URL = 'https://chicken-hot-dreux-default-rtdb.europe-west1.firebasedatabase.app';

let orders = {};
let isFirstLoad = true;

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

// Fonction pour comparer si deux commandes sont identiques
function ordersAreEqual(order1, order2) {
    return JSON.stringify(order1) === JSON.stringify(order2);
}

// Fonction pour mettre à jour uniquement les commandes modifiées
function updateOrders(newOrders) {
    const container = document.getElementById('orders-container');
    
    // Vérifier s'il y a des commandes
    if (!newOrders || Object.keys(newOrders).length === 0) {
        const emptyState = container.querySelector('.empty-state');
        if (!emptyState) {
            container.innerHTML = `
                <div class="empty-state">
                    <h2>🍗 En attente de commandes...</h2>
                    <p>Les nouvelles commandes apparaîtront automatiquement ici</p>
                </div>
            `;
        }
        return;
    }
    
    // Supprimer le message "empty state" s'il existe
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Trier les commandes par date (plus récentes en premier)
    const sortedOrders = Object.entries(newOrders)
        .sort((a, b) => new Date(b[1].timestamp) - new Date(a[1].timestamp));
    
    const newOrderIds = sortedOrders.map(([id]) => id);
    const existingCards = container.querySelectorAll('.order-card');
    
    // Supprimer les commandes qui n'existent plus
    existingCards.forEach(card => {
        const orderId = card.getAttribute('data-id');
        if (!newOrderIds.includes(orderId)) {
            card.remove();
        }
    });
    
    // Ajouter ou mettre à jour les commandes
    sortedOrders.forEach(([orderId, order], index) => {
        const existingCard = container.querySelector(`[data-id="${orderId}"]`);
        
        if (!existingCard) {
            // Nouvelle commande - l'ajouter
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = createOrderHTML(orderId, order);
            const newCard = tempDiv.firstElementChild;
            
            // Insérer à la bonne position selon le tri
            if (index === 0) {
                container.insertBefore(newCard, container.firstChild);
            } else {
                const previousOrderId = sortedOrders[index - 1][0];
                const previousCard = container.querySelector(`[data-id="${previousOrderId}"]`);
                if (previousCard && previousCard.nextSibling) {
                    container.insertBefore(newCard, previousCard.nextSibling);
                } else {
                    container.appendChild(newCard);
                }
            }
            
            // Notification pour nouvelle commande (sauf au premier chargement)
            if (!isFirstLoad) {
                playNotificationSound();
            }
        } else {
            // Vérifier si la commande a changé
            const oldOrder = orders[orderId];
            if (oldOrder && !ordersAreEqual(oldOrder, order)) {
                // La commande a été modifiée - la mettre à jour
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = createOrderHTML(orderId, order);
                existingCard.replaceWith(tempDiv.firstElementChild);
            }
            // Sinon, ne rien faire pour éviter le clignotement
        }
    });
    
    isFirstLoad = false;
}

// Fonction pour écouter les nouvelles commandes en temps réel
function listenToOrders() {
    const ordersRef = `${FIREBASE_URL}/orders.json`;
    
    // Fonction de récupération
    function fetchOrders() {
        fetch(ordersRef)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    updateOrders(data);
                    orders = data;
                } else {
                    updateOrders({});
                    orders = {};
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
            });
    }
    
    // Première récupération
    fetchOrders();
    
    // Polling toutes les 5 secondes
    setInterval(fetchOrders, 5000);
}

// Fonction pour jouer un son de notification
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
