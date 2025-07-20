// dataPoster.js
class DataPoster {
    constructor(loader, renderer, options = {}) {
        this.loader = loader;          // DataLoader instance
        this.renderer = renderer;      // ItemRenderer instance
        this.options = {
            formId: 'create-form',
            fieldMappings: {},        // Custom field mappings
            transformData: null,      // Optional data transformer
            beforeSubmit: null,       // Pre-submit hook
            afterSuccess: null,       // Post-success hook
            ...options
        };
    }

    async submit() {
        try {
            // 1. Prepare the form data
            const formData = this.collectFormData();
            console.log('Form data collected:', formData);

            // 2. Apply transformations if needed
            const finalData = this.options.transformData 
                ? await this.options.transformData(formData)
                : formData;
        console.log('Data being sent:', finalData);
            // 3. Optional pre-submit validation/hook
            if (this.options.beforeSubmit) {
                const shouldProceed = await this.options.beforeSubmit(finalData);
                if (shouldProceed === false) return;
            }

            // 4. Send the request
            const response = await fetch(this.loader.API_BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(finalData)
            });

            if (!response.ok) {
                const error = await this.parseError(response);
                throw error;
            }

            // 5. Handle success
            const result = await response.json();
            this.handleSuccess(result);

            // 6. Optional post-success hook
            if (this.options.afterSuccess) {
                this.options.afterSuccess(result);
            }

            return result;

        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    collectFormData() {
        const formData = {};
        const form = document.getElementById(this.options.formId);

        if (!form) {
            throw new Error(`Form with ID "${this.options.formId}" not found`);
        }

        // Get all form elements
        const elements = form.elements;

        // Process each form element
        for (let element of elements) {
            if (element.name && element.type !== 'submit') {
                const fieldName = this.options.fieldMappings[element.name] || element.name;
                formData[fieldName] = this.getElementValue(element);
            }
        }

        return formData;
    }

    getElementValue(element) {
        switch (element.type) {
            case 'number':
            return element.value ? element.valueAsNumber : null;
        case 'checkbox':
            return element.checked;
        case 'time':
            return element.value ? element.value.substring(0, 5) : null;
        default:
            return element.value;
        }
    }

    async parseError(response) {
        try {
            const errorData = await response.json();
            
            // Handle array of errors (common in FastAPI validation)
            if (Array.isArray(errorData)) {
                const messages = errorData.map(e => 
                    e.msg || e.detail || JSON.stringify(e)
                ).join(', ');
                return new Error(messages);
            }
            
            // Handle single error object
            return new Error(
                errorData.detail || 
                errorData.message || 
                errorData.error || 
                JSON.stringify(errorData)
            );
        } catch {
            return new Error(await response.text());
        }
    }

    handleSuccess(result) {
        const form = document.getElementById(this.options.formId);
        if (form) form.reset();
        
        this.renderer.loadAndRenderItems();
        
        alert(`${this.loader.itemType.charAt(0).toUpperCase() + this.loader.itemType.slice(1)} created successfully! ID: ${result.id}`);
    }

    handleError(error) {
        console.error(`Error creating ${this.loader.itemType}:`, error);
        console.error('Error details:', error.message);
        
        // More user-friendly error display
        alert(`Error creating ${this.loader.itemType}:\n${error.message}`);
    }
    initialize() {
        const form = document.getElementById(this.options.formId);
        if (form) {
            form.addEventListener('submit', async (event) => {
                event.preventDefault();
                await this.submit();
            });
        }
        return this;
    }
}