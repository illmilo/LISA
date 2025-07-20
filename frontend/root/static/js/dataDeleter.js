// dataDeleter.js
class DataDeleter {
    constructor(loader, renderer, options = {}) {
        this.loader = loader;      // DataLoader instance
        this.renderer = renderer;  // ItemRenderer instance
        this.options = {
            confirmMessage: `Delete this ${loader.itemType}?`,
            successMessage: `${loader.itemType.charAt(0).toUpperCase() + loader.itemType.slice(1)} deleted successfully`,
            ...options
        };
    }

    async delete(itemId) {
        if (!confirm(this.options.confirmMessage.replace('{id}', itemId))) return;
        
        try {
            const result = await this.loader.deleteItem(itemId);
            alert(this.options.successMessage.replace('{id}', itemId));
            this.renderer.loadAndRenderItems();
            return result;
        } catch (error) {
            console.error(`Error deleting ${this.loader.itemType}:`, error);
            alert(`Error: ${error.message}`);
            throw error;
        }
    }

    setupDeletionListener(containerSelector = '.list-content') {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn(`Container "${containerSelector}" not found`);
            return;
        }

        container.addEventListener('click', async (event) => {
            if (!event.target.classList.contains('delete-btn')) return;
            
            const itemId = event.target.closest('[data-item-id]')?.dataset.itemId;
            if (itemId) await this.delete(itemId);
        });
    }
}