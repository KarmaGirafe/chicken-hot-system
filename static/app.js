let database;
let commandesRef;
let commandesActives = new Map();
let isFirstLoad = true;

// Initialise Firebase
async function initFirebase() {
    try {
        // Récupère la config depuis le backend
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // Initialise Firebase
        firebase.initializeApp(config);
        database = firebase.database();
        commandesRef = database.ref('commandes');
        
        // Écoute les changements en temps réel
        commandesRef.on('child_added', (snapshot) => {
            const commande = snapshot.val();
            commande.id = snapshot.key;
            
            if (commande.statut === 'En attente') {
                // Joue un son seulement après le premier chargement
                if (!isFirstLoad) {
                    playNotificationSound();
                }
                afficherCommande(commande, !isFirstLoad);
            }
        });
        
        commandesRef.on('child_changed', (snapshot) => {
            const commande = snapshot.val();
            commande.id = snapshot.key;
            
            if (commande.statut !== 'En attente') {
                retirerCommande(commande.id);
            }
        });
        
        commandesRef.on('child_removed', (snapshot) => {
            retirerCommande(snapshot.key);
        });
        
        // Après 2 secondes, on considère que le chargement initial est terminé
        setTimeout(() => {
            isFirstLoad = false;
        }, 2000);
        
        updateStatus(true);
    } catch (error) {
        console.error('Erreur Firebase:', error);
        updateStatus(false);
    }
}

function updateStatus(connected) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connecté';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Déconnecté';
    }
}

function afficherCommande(commande, isNew = false) {
    commandesActives.set(commande.id, commande);
    updateCommandesCount();
    
    const grid = document.getElementById('commandesGrid');
    
    // Retire l'état vide
    const emptyState = grid.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Crée la carte
    const card = document.createElement('div');
    card.className = 'commande-card' + (isNew ? ' nouvelle' : '');
    card.id = `commande-${commande.id}`;
    
    const serviceClass = commande.type_service.toLowerCase().replace(' ', '-');
    
    card.innerHTML = `
        ${isNew ? '<span class="badge-nouvelle">🔔 NOUVELLE</span>' : ''}
        <div class="commande-header">
            <span class="commande-numero">🔔 ${commande.numero}</span>
            <span class="commande-heure">🕐 ${commande.heure}</span>
        </div>
        <div class="commande-service ${serviceClass}">📍 ${commande.type_service}</div>
        <div class="commande-articles">🍽️ ${commande.articles}</div>
        <div class="commande-prix">💰 ${commande.total.toFixed(2)} €</div>
        <button class="btn-prete" onclick="marquerPrete('${commande.id}')">
            ✅ Commande Prête
        </button>
    `;
    
    grid.appendChild(card);
    
    // Retire le badge "nouvelle" après 5 secondes
    if (isNew) {
        setTimeout(() => {
            card.classList.remove('nouvelle');
            const badge = card.querySelector('.badge-nouvelle');
            if (badge) badge.remove();
        }, 5000);
    }
}

function retirerCommande(commandeId) {
    commandesActives.delete(commandeId);
    updateCommandesCount();
    
    const card = document.getElementById(`commande-${commandeId}`);
    if (card) {
        card.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => card.remove(), 300);
    }
    
    // Si plus de commandes, affiche l'état vide
    if (commandesActives.size === 0) {
        const grid = document.getElementById('commandesGrid');
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">✨</div>
                <p>Aucune commande en attente</p>
                <small>Les nouvelles commandes apparaîtront ici automatiquement</small>
            </div>
        `;
    }
}

function updateCommandesCount() {
    document.getElementById('commandesCount').textContent = commandesActives.size;
}

async function marquerPrete(commandeId) {
    try {
        const response = await fetch(`/api/commande/${commandeId}/statut`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ statut: 'Prête' })
        });
        
        if (response.ok) {
            // La carte sera retirée automatiquement via Firebase
            playSuccessSound();
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la mise à jour');
    }
}

function playNotificationSound() {
    const audio = document.getElementById('notificationSound');
    audio.play().catch(e => console.log('Impossible de jouer le son'));
}

function playSuccessSound() {
    // Son de succès simple
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// Démarre l'app
initFirebase();
