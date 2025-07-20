class DataLoader {
    constructor(apiBaseUrl, itemType) {
        this.API_BASE_URL = apiBaseUrl;
        this.itemType = itemType;
    }

    async loadItems() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            if (response.status === 204) {
                return [];
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error loading ${this.itemType}s:`, error);
            throw error;
        }
    }

    async deleteItem(itemId) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/${itemId}/`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error deleting ${this.itemType}:`, error);
            throw error;
        }
    }
}