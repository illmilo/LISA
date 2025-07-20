// dropdownLoader.js
class DropdownLoader {
    constructor(loader, selectElementId, itemNameKey = 'name') {
        this.loader = loader;          // Accepts a DataLoader instance
        this.selectElementId = selectElementId;
        this.itemNameKey = itemNameKey; // Key to use for display text
    }

    async populate() {
        try {
            const select = document.getElementById(this.selectElementId);
            if (!select) {
                console.warn(`Dropdown element with ID '${this.selectElementId}' not found`);
                return;
            }

            // Use the provided loader to get items
            const items = await this.loader.loadItems();
            
            // Clear existing options
            select.innerHTML = '';
            
            // Add default option
            this.addOption(select, '', `Select ${this.loader.itemType}`, true, true);
            
            // Add item options
            items.forEach(item => {
                const displayText = item[this.itemNameKey] || `${this.loader.itemType} ${item.id}`;
                this.addOption(select, item.id, displayText);
            });
            
        } catch (error) {
            console.error('Error populating dropdown:', error);
            throw error;
        }
    }

    addOption(selectElement, value, text, disabled = false, selected = false) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        option.disabled = disabled;
        option.selected = selected;
        selectElement.appendChild(option);
    }

    getSelectedValue() {
        const select = document.getElementById(this.selectElementId);
        return select ? select.value : null;
    }

    clear() {
        const select = document.getElementById(this.selectElementId);
        if (select) select.innerHTML = '';
    }
}