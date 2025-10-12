let menu = [];
let order = [];
let tableNumber = null;
let tableCode = '';

document.addEventListener('DOMContentLoaded', function() {
    // Extract table number from URL path (/table/X) or query (?table=X)
    const pathParts = window.location.pathname.split('/');
    const tableIndex = pathParts.indexOf('table');
    if (tableIndex !== -1 && pathParts[tableIndex + 1]) {
        tableNumber = pathParts[tableIndex + 1];
    } else {
        // Fallback to query parameter
        const urlParams = new URLSearchParams(window.location.search);
        tableNumber = urlParams.get('table');
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const language = urlParams.get('lang');
    
    if (tableNumber) {
        document.getElementById('table-number').textContent = tableNumber;
        document.getElementById('table-number-input').value = tableNumber;
        
        // Only load menu if language is specified
        if (language) {
            loadMenu();
            loadExistingOrder();
        } else {
            // No language specified - user should be on language selection page
            return;
        }
    } else {
        showMessage('Please specify a table number in the URL (?table=X)', 'error');
    }
    
    document.getElementById('order-form').addEventListener('submit', placeOrder);
    
    // Auto-refresh to detect when table is finished or split happens
    setInterval(checkTableStatus, 1000); // Check every 1 second for immediate refresh
});

async function loadMenu() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const language = urlParams.get('lang') || 'en';
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/client', '') : '';
        const response = await fetch(`${baseUrl}/client/menu?table=${tableNumber}&lang=${language}`);
        const data = await response.json();
        
        if (response.ok) {
            menu = data.menu;
            tableCode = data.table_code;
            
            // Update UI based on business type (detect from URL or data)
            updateBusinessTypeUI(data);
            
            // Show language selector only if multiple languages available
            const langSelector = document.querySelector('.language-selector');
            if (data.available_languages && data.available_languages.length > 1) {
                langSelector.style.display = 'block';
                updateLanguageButtons(data.available_languages, data.current_language);
            } else {
                langSelector.style.display = 'none';
            }
            
            displayMenu();
            document.getElementById('menu-section').style.display = 'block';
        } else {
            showMessage(data.detail || 'Error loading menu', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

function displayMenu() {
    const menuContainer = document.getElementById('menu-items');
    menuContainer.innerHTML = '';
    
    // Display menu by categories
    const categoryKeys = Object.keys(menu);
    
    categoryKeys.forEach((category, index) => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'menu-category';
        
        const categoryHeader = document.createElement('h3');
        categoryHeader.className = 'category-title';
        categoryHeader.textContent = category;
        categoryHeader.style.cursor = 'pointer';
        categoryHeader.onclick = function() {
            if (categoryItems.style.display === 'none') {
                categoryItems.style.display = 'grid';
            } else {
                categoryItems.style.display = 'none';
            }
        };
        
        const categoryItems = document.createElement('div');
        categoryItems.className = 'category-items';
        categoryItems.id = `category-items-${index}`; // Unique ID for each category
        categoryItems.style.display = 'none'; // Start collapsed
        
        const categoryItemsList = menu[category] || [];
        
        categoryItemsList.forEach(item => {
            const menuItemDiv = document.createElement('div');
            menuItemDiv.className = 'menu-item';
            menuItemDiv.innerHTML = `
                <h4 class="menu-item-name" data-original-name="${item.name}">${item.name}</h4>
                <p class="ingredients">${item.ingredients || 'No ingredients listed'}</p>
                <p class="price">€${item.price.toFixed(2)}</p>
                <div class="quantity-controls">
                    <button type="button" onclick="updateQuantity(${item.id}, -1)">-</button>
                    <span id="qty-${item.id}">0</span>
                    <button type="button" onclick="updateQuantity(${item.id}, 1)">+</button>
                </div>
                <div id="customize-section-${item.id}" style="display: none; margin-top: 10px;">
                    <button type="button" class="customize-btn-small" onclick="openCustomizeModal(${item.id})">Customize Order</button>
                </div>
            `;
            categoryItems.appendChild(menuItemDiv);
        });
        
        categoryDiv.appendChild(categoryHeader);
        categoryDiv.appendChild(categoryItems);
        menuContainer.appendChild(categoryDiv);
    });
    
    // Update menu language after items are displayed
    if (typeof updateMenuLanguage === 'function') {
        updateMenuLanguage();
    }
}

function openCustomizeModal(itemId) {
    let item = null;
    // Find item in categorized menu
    Object.values(menu).forEach(categoryItems => {
        const found = categoryItems.find(m => m.id === itemId);
        if (found) item = found;
    });
    
    if (!item) {
        alert('Item not found');
        return;
    }
    
    // Parse ingredients from description
    function parseIngredients(description) {
        if (!description || !description.trim()) return [];
        
        // Common ingredient keywords
        const ingredientKeywords = [
            'tomato', 'cheese', 'mozzarella', 'basil', 'pasta', 'chicken', 'beef', 'pork', 'salmon', 'tuna',
            'vegetables', 'onion', 'garlic', 'pepper', 'mushroom', 'olive', 'lettuce', 'spinach',
            'bacon', 'ham', 'egg', 'cream', 'butter', 'oil', 'sauce', 'herbs', 'parsley', 'oregano',
            'lemon', 'lime', 'avocado', 'cucumber', 'carrot', 'potato', 'rice', 'bread', 'flour'
        ];
        
        const found = [];
        const lowerDesc = description.toLowerCase();
        
        ingredientKeywords.forEach(keyword => {
            if (lowerDesc.includes(keyword)) {
                // Capitalize first letter
                found.push(keyword.charAt(0).toUpperCase() + keyword.slice(1));
            }
        });
        
        // If comma-separated, prioritize those over keywords
        if (description.includes(',')) {
            const commaSplit = description.split(',').map(ing => ing.trim()).filter(ing => ing);
            return [...new Set(commaSplit)];
        }
        
        // Remove duplicates and return keywords only if no commas
        return [...new Set(found)];
    }
    
    const ingredients = parseIngredients(item.ingredients);
    
    let ingredientRows = '';
    if (ingredients.length > 0) {
        ingredients.forEach(ing => {
            ingredientRows += 
                '<div class="ingredient-row">' +
                    '<span class="ingredient-name">' + ing + '</span>' +
                    '<div class="ingredient-controls">' +
                        '<button type="button" class="ingredient-btn remove" onclick="changeIngredientQty(' + itemId + ', \'' + ing + '\', -1)">&minus;</button>' +
                        '<span class="ingredient-qty" id="ing-' + itemId + '-' + ing.replace(/\s+/g, '') + '">1</span>' +
                        '<button type="button" class="ingredient-btn add" onclick="changeIngredientQty(' + itemId + ', \'' + ing + '\', 1)">&plus;</button>' +
                    '</div>' +
                '</div>';
        });
    } else {
        ingredientRows = '<p class="no-ingredients">No ingredients detected for customization</p>';
    }
    
    const modal = document.createElement('div');
    modal.className = 'customize-modal';
    modal.innerHTML = 
        '<div class="customize-modal-content">' +
            '<div class="customize-header">' +
                '<h3>Customize ' + item.name + '</h3>' +
                '<button class="close-btn" onclick="closeCustomizeModal()">&times;</button>' +
            '</div>' +
            '<div class="customize-body">' +
                ingredientRows +
                '<div class="extra-ingredients">' +
                    '<input type="text" id="extra-' + itemId + '" placeholder="Add custom ingredients (comma separated)" onchange="updateCustomization(' + itemId + ')" value="' + (itemCustomizations[itemId] && itemCustomizations[itemId].extra ? itemCustomizations[itemId].extra.join(', ') : '') + '">' +
                '</div>' +
            '</div>' +
            '<div class="customize-footer">' +
                '<button class="save-btn" onclick="closeCustomizeModal()">Save</button>' +
            '</div>' +
        '</div>';
    
    document.body.appendChild(modal);
}

function closeCustomizeModal() {
    const modal = document.querySelector('.customize-modal');
    if (modal) {
        modal.remove();
        // Update order display to show customizations
        updateOrderDisplay();
    }
}

let itemCustomizations = {};

function changeIngredientQty(itemId, ingredient, change) {
    const qtyId = 'ing-' + itemId + '-' + ingredient.replace(/\s+/g, '');
    const qtyElement = document.getElementById(qtyId);
    
    if (!qtyElement) return;
    
    let currentQty = parseInt(qtyElement.textContent) || 1;
    let newQty = Math.max(0, currentQty + change);
    
    qtyElement.textContent = newQty;
    
    // Update customizations
    if (!itemCustomizations[itemId]) {
        itemCustomizations[itemId] = { ingredients: {} };
    }
    if (!itemCustomizations[itemId].ingredients) {
        itemCustomizations[itemId].ingredients = {};
    }
    
    itemCustomizations[itemId].ingredients[ingredient] = newQty;
    updateCustomization(itemId);
}

function updateCustomization(itemId) {
    const extraInput = document.getElementById('extra-' + itemId);
    
    if (!itemCustomizations[itemId]) {
        itemCustomizations[itemId] = { ingredients: {}, extra: [] };
    }
    
    // Handle extra ingredients from text input
    if (extraInput && extraInput.value.trim()) {
        itemCustomizations[itemId].extra = extraInput.value.split(',').map(ing => ing.trim()).filter(ing => ing);
    }
    
    // Update order item with customizations
    const existingItem = order.find(item => item.product_id === itemId);
    if (existingItem) {
        existingItem.customizations = JSON.stringify(itemCustomizations[itemId]);
    }
}

function updateQuantity(itemId, change) {
    const qtyElement = document.getElementById(`qty-${itemId}`);
    const customizeSection = document.getElementById(`customize-section-${itemId}`);
    let currentQty = parseInt(qtyElement.textContent);
    let newQty = Math.max(0, currentQty + change);
    
    qtyElement.textContent = newQty;
    
    // Show/hide customize button based on quantity
    if (newQty > 0) {
        customizeSection.style.display = 'block';
    } else {
        customizeSection.style.display = 'none';
    }
    
    // Update order array
    const existingItem = order.find(item => item.product_id === itemId);
    if (existingItem) {
        if (newQty === 0) {
            order = order.filter(item => item.product_id !== itemId);
        } else {
            existingItem.qty = newQty;
        }
    } else if (newQty > 0) {
        const newItem = { product_id: itemId, qty: newQty };
        // Add any existing customizations
        if (itemCustomizations[itemId]) {
            newItem.customizations = JSON.stringify(itemCustomizations[itemId]);
        }
        order.push(newItem);
    }
    
    updateOrderDisplay();
}

function updateOrderDisplay() {
    const orderItemsContainer = document.getElementById('order-items');
    const totalElement = document.getElementById('total');
    const placeOrderBtn = document.getElementById('place-order-btn');
    
    orderItemsContainer.innerHTML = '';
    let total = 0;
    
    order.forEach(orderItem => {
        let menuItem = null;
        // Find item in categorized menu
        Object.values(menu).forEach(categoryItems => {
            const found = categoryItems.find(item => item.id === orderItem.product_id);
            if (found) menuItem = found;
        });
        
        if (menuItem) {
            const itemTotal = menuItem.price * orderItem.qty;
            total += itemTotal;
            
            let customizationText = '';
            if (orderItem.customizations) {
                try {
                    const custom = JSON.parse(orderItem.customizations);
                    if (custom.ingredients || custom.extra) {
                        const parts = [];
                        if (custom.ingredients) {
                            Object.entries(custom.ingredients).forEach(([ing, qty]) => {
                                if (qty === 0) parts.push(`No ${ing}`);
                                else if (qty > 1) parts.push(`${qty}x ${ing}`);
                            });
                        }
                        if (custom.extra && custom.extra.length > 0) {
                            parts.push(`+${custom.extra.join(', ')}`);
                        }
                        if (parts.length > 0) {
                            customizationText = `<br><small style="color: #666; font-style: italic;">${parts.join(', ')}</small>`;
                        }
                    }
                } catch (e) {}
            }
            
            const orderItemDiv = document.createElement('div');
            orderItemDiv.className = 'order-item';
            orderItemDiv.innerHTML = `
                <span>${menuItem.name} x${orderItem.qty}${customizationText}</span>
                <span>€${itemTotal.toFixed(2)}</span>
            `;
            orderItemsContainer.appendChild(orderItemDiv);
        }
    });
    
    totalElement.textContent = `Total: €${total.toFixed(2)}`;
    placeOrderBtn.disabled = order.length === 0;
}

async function placeOrder(event) {
    event.preventDefault();
    
    // Check if checkout was requested
    const statusMsg = document.getElementById('order-status-message');
    if (statusMsg && statusMsg.innerHTML.includes('Checkout requested')) {
        showMessage('Cannot place orders after checkout has been requested', 'error');
        return;
    }
    
    const code = document.getElementById('table-code').value;
    if (code.length !== 3) {
        showMessage('Please enter a valid 3-digit code', 'error');
        return;
    }
    
    if (order.length === 0) {
        showMessage('Please select at least one item', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('table_number', tableNumber);
        formData.append('code', code);
        formData.append('items', JSON.stringify(order));
        
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/client', '') : '';
        const response = await fetch(`${baseUrl}/client/order`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            // Reset form
            order = [];
            document.getElementById('order-form').reset();
            document.querySelectorAll('[id^="qty-"]').forEach(el => el.textContent = '0');
            updateOrderDisplay();
            // Reload existing order to show updated total
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showMessage(data.detail || 'Error placing order', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

async function loadExistingOrder() {
    try {
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/table/' + tableNumber, '') : '';
        const response = await fetch(`${baseUrl}/client/order_details/${tableNumber}`);
        const data = await response.json();
        
        if (data.has_order) {
            displayExistingOrder(data);
        }
    } catch (error) {
        console.error('Error loading existing order:', error);
    }
}

function displayExistingOrder(orderData) {
    orderTotal = orderData.total; // Store for tip calculation
    
    const existingOrderDiv = document.createElement('div');
    existingOrderDiv.id = 'existing-order';
    existingOrderDiv.innerHTML = `
        <h3>Current Order</h3>
        <div class="existing-order-items">
            ${orderData.items.map(item => `
                <div class="existing-order-item">
                    <span>${item.name} x${item.qty}${item.customizations ? ' (Customized)' : ''}</span>
                    <div class="item-actions">
                        <span>€${item.total.toFixed(2)}</span>
                        <button onclick="deleteOrderItem(${item.id})" class="delete-item-btn" title="Remove item">🗑️</button>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="existing-order-total">Total: €${orderData.total.toFixed(2)}</div>
        <p id="order-status-message"><em>You can add more items below or request checkout:</em></p>
    `;
    
    const menuSection = document.getElementById('menu-section');
    menuSection.insertBefore(existingOrderDiv, menuSection.firstChild);
    
    // Check if checkout was already requested
    if (orderData.checkout_requested) {
        // Hide entire menu section and order section when checkout is requested
        const menuItems = document.getElementById('menu-items');
        if (menuItems) {
            menuItems.style.display = 'none';
        }
        
        const orderSection = document.getElementById('order-section');
        if (orderSection) {
            orderSection.style.display = 'none';
        }
        
        document.getElementById('checkout-section').style.display = 'none';
        
        // Update status message and add download button
        const statusMsg = document.getElementById('order-status-message');
        if (statusMsg) {
            statusMsg.innerHTML = '<em style="color: #e67e22; font-weight: bold;">Checkout requested. Please wait for staff assistance.</em><br><br><button onclick="downloadTicket()" style="background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; margin-top: 10px;">📄 Download Receipt</button>';
        }
    } else {
        // Show checkout section normally
        document.getElementById('checkout-section').style.display = 'block';
    }
}

let selectedTipAmount = 0;
let orderTotal = 0;

function selectTip(percentage) {
    const customTipInput = document.getElementById('custom-tip');
    customTipInput.style.display = 'none';
    
    if (percentage === 0) {
        selectedTipAmount = 0;
    } else {
        selectedTipAmount = (orderTotal * percentage) / 100;
    }
    
    updateTipDisplay();
    enableCheckoutButtons();
    
    // Update button states
    document.querySelectorAll('.tip-btn').forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
}

function selectCustomTip() {
    const customTipInput = document.getElementById('custom-tip');
    customTipInput.style.display = 'block';
    customTipInput.focus();
    
    customTipInput.onchange = function() {
        selectedTipAmount = parseFloat(this.value) || 0;
        updateTipDisplay();
        enableCheckoutButtons();
    };
    
    // Update button states
    document.querySelectorAll('.tip-btn').forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
}

function updateTipDisplay() {
    document.getElementById('tip-display').textContent = `Selected Tip: €${selectedTipAmount.toFixed(2)}`;
}

function enableCheckoutButtons() {
    document.getElementById('cash-btn').disabled = false;
    document.getElementById('card-btn').disabled = false;
}

async function requestCheckout(method) {
    try {
        const formData = new FormData();
        formData.append('table_number', tableNumber);
        formData.append('checkout_method', method);
        formData.append('tip_amount', selectedTipAmount);
        
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/table/' + tableNumber, '') : '';
        const response = await fetch(`${baseUrl}/client/checkout`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            // Hide checkout buttons and disable ordering after request
            document.getElementById('checkout-section').style.display = 'none';
            
            // Hide entire menu section and order section when checkout is requested
            const menuItems = document.getElementById('menu-items');
            if (menuItems) {
                menuItems.style.display = 'none';
            }
            
            const orderSection = document.getElementById('order-section');
            if (orderSection) {
                orderSection.style.display = 'none';
            }
            
            // Update status message and add download button
            const statusMsg = document.getElementById('order-status-message');
            if (statusMsg) {
                statusMsg.innerHTML = '<em style="color: #e67e22; font-weight: bold;">Checkout requested. Please wait for staff assistance.</em><br><br><button onclick="downloadTicket()" style="background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; margin-top: 10px;">📄 Download Receipt</button>';
            }
        } else {
            showMessage(data.detail || 'Error requesting checkout', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

let lastOrderHash = '';

async function checkTableStatus() {
    try {
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/table/' + tableNumber, '') : '';
        const response = await fetch(`${baseUrl}/client/order_details/${tableNumber}`);
        const data = await response.json();
        
        if (!data.has_order && document.getElementById('existing-order')) {
            // Table was finished, refresh the page
            showMessage('Your table has been processed. Thank you!', 'success');
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else if (data.has_order) {
            // Simple refresh check - compare order total
            if (window.lastTotal !== undefined && data.total !== window.lastTotal) {
                console.log(`Order changed: €${window.lastTotal} -> €${data.total}, refreshing...`);
                location.reload();
            }
            window.lastTotal = data.total;
        }
    } catch (error) {
        // Ignore errors in background check
    }
}

async function deleteOrderItem(orderItemId) {
    if (!confirm('Are you sure you want to remove this item from your order?')) {
        return;
    }
    
    try {
        const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/table/' + tableNumber, '') : '';
        const response = await fetch(`${baseUrl}/client/order_item/${orderItemId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            // Reload the page to refresh the order
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showMessage(data.detail || 'Error removing item', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

function downloadTicket() {
    const baseUrl = window.location.pathname.includes('/r/') ? window.location.pathname.replace('/table/' + tableNumber, '') : '';
    window.open(`${baseUrl}/client/simple-receipt/${tableNumber}`, '_blank');
}

function updateLanguageButtons(availableLanguages, currentLanguage) {
    const langSelector = document.querySelector('.language-selector');
    langSelector.innerHTML = '';
    
    const langNames = {
        'en': '🇺🇸 English',
        'es': '🇪🇸 Español', 
        'fr': '🇫🇷 Français',
        'de': '🇩🇪 Deutsch',
        'it': '🇮🇹 Italiano'
    };
    
    availableLanguages.forEach(lang => {
        const btn = document.createElement('button');
        btn.className = 'lang-btn';
        btn.textContent = langNames[lang] || lang.toUpperCase();
        btn.onclick = () => changeLanguage(lang);
        if (lang === currentLanguage) {
            btn.style.background = '#0056b3';
        }
        langSelector.appendChild(btn);
    });
}

function changeLanguage(lang) {
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}

function updateBusinessTypeUI(data) {
    // Detect if this is a hotel based on business_type field
    const isHotel = data.business_type === 'hotel';
    
    const locationHeader = document.getElementById('location-header');
    const welcomeMessage = document.getElementById('welcome-message');
    const codeLabel = document.getElementById('code-label');
    const pageTitle = document.getElementById('page-title');
    
    if (isHotel) {
        // Update labels for hotel context
        if (locationHeader) {
            const roomPrefix = data.room_prefix ? data.room_prefix + ' ' : '';
            locationHeader.innerHTML = `🏨 ${roomPrefix}Room <span id="table-number">${tableNumber}</span>`;
        }
        if (welcomeMessage) {
            welcomeMessage.textContent = 'Welcome! Browse our room service menu and place your order';
        }
        if (codeLabel) {
            codeLabel.textContent = 'Enter 3-digit room code:';
        }
        if (pageTitle) {
            const roomPrefix = data.room_prefix ? data.room_prefix + ' ' : '';
            pageTitle.textContent = `Hotel Room Service - ${roomPrefix}Room ${tableNumber}`;
        }
    } else {
        // Update labels for restaurant context
        if (locationHeader) {
            locationHeader.innerHTML = `📍 Table <span id="table-number">${tableNumber}</span>`;
        }
        if (welcomeMessage) {
            welcomeMessage.textContent = 'Welcome! Browse our menu and place your order';
        }
        if (codeLabel) {
            codeLabel.textContent = 'Enter 3-digit table code:';
        }
        if (pageTitle) {
            pageTitle.textContent = `Restaurant Menu - Table ${tableNumber}`;
        }
    }
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}