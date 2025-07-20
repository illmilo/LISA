// itemRenderer.js
class ItemRenderer {
    constructor(itemType, loader, target) {
        this.itemType = itemType;
        this.loader = loader;
        this.listContainer = document.querySelector(target);
        this.searchInput = document.querySelector('.search-box input');
        this.initialize();
    }

    initialize() {
        if (this.listContainer) {
            this.loadAndRenderItems();
            
            // Event delegation for action buttons
            this.listContainer.addEventListener('click', async (event) => {
                const id = event.target.closest('[data-item-id]')?.dataset.itemId;
                if (!id) return;
                
                if (event.target.classList.contains('delete-btn')) {
                    await this.handleDeleteItem(id);
                }
            });
        }

        if (this.searchInput && this.listContainer) {
            this.searchInput.addEventListener('input', (event) => {
                this.filterList(event.target.value);
            });
        }
    }

    async loadAndRenderItems() {
        try {
            const items = await this.loader.loadItems();
            this.renderList(items);
        } catch (error) {
            alert(`Error loading ${this.itemType}s: ${error.message}`);
        }
    }

    async handleDeleteItem(itemId) {
        if (!confirm(`Delete this ${this.itemType}?`)) return;
        
        try {
            await this.loader.deleteItem(itemId);
            alert(`${this.itemType.charAt(0).toUpperCase() + this.itemType.slice(1)} deleted successfully`);
            this.loadAndRenderItems();
        } catch (error) {
            alert(`Error deleting ${this.itemType}: ${error.message}`);
        }
    }

    filterList(query) {
        const items = this.listContainer.querySelectorAll('.list-item');
        const lowerQuery = query.trim().toLowerCase();
        
        items.forEach(item => {
            const nameElem = item.querySelector('.item-info h3');
            const name = nameElem ? nameElem.textContent.toLowerCase() : '';
            item.style.display = name.includes(lowerQuery) ? '' : 'none';
        });
    }

    renderList(items) {
        if (!this.listContainer) {
            console.warn("Cannot render list: container not found");
            return;
        }
        
        this.listContainer.innerHTML = '';
        
        if (!items || items.length === 0) {
            this.listContainer.innerHTML = `<div class="no-items">No ${this.itemType}s found</div>`;
            return;
        }
        
        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'list-item';
            itemElement.dataset.itemId = item.id;
            
            const infoContainer = document.createElement('div');
            infoContainer.className = 'item-info';
            
            const nameHeader = document.createElement('h3');
            nameHeader.textContent = item.name || `Unnamed ${this.itemType}`;
            infoContainer.appendChild(nameHeader);
            
            for (const [key, value] of Object.entries(item)) {
                if (key === 'id' || key === 'name') continue;
                
                const propElement = document.createElement('p');
                propElement.innerHTML = `<strong>${key.replace(/_/g, ' ')}:</strong> ${value || 'N/A'}`;
                infoContainer.appendChild(propElement);
            }
            
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'item-actions';
            actionsContainer.innerHTML = '<button class="btn delete-btn">Delete</button>';
            
            itemElement.appendChild(infoContainer);
            itemElement.appendChild(actionsContainer);
            this.listContainer.appendChild(itemElement);
        });
    }
}