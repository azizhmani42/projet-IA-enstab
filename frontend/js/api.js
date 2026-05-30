/* ============================================================
   LogoForge AI — API Client
   Handles all communication with the Flask backend.
   ============================================================ */

const API = {
    BASE_URL: '',  // Same origin — Flask serves the frontend

    /**
     * Generate logos from a text prompt.
     * @param {string} prompt      - Description of the desired logo
     * @param {string} style       - One of the available style presets
     * @param {string} colors      - Comma-separated color values or description
     * @param {number} numImages   - Number of variations (1-4)
     * @param {string} brandName   - Exact brand name to overlay on the image
     * @returns {Promise<Object>} { success, message, images: [...] }
     */
    async generateLogos(prompt, style, colors, numImages, brandName) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt,
                    style,
                    colors,
                    num_images: numImages,
                    brand_name: brandName || null,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                const errorMsg = errorData?.detail || errorData?.message || `Erreur serveur (${response.status})`;
                const error = new Error(errorMsg);
                error.detail = errorData?.detail || errorMsg;
                error.message = errorData?.message || errorMsg;
                throw error;
            }

            const data = await response.json();

            if (!data.success) {
                const error = new Error(data.message || 'La génération a échoué');
                error.detail = data.detail || data.message;
                throw error;
            }

            return data;
        } catch (error) {
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('Impossible de contacter le serveur. Vérifiez votre connexion.');
            }
            throw error;
        }
    },

    /**
     * Fetch the full gallery of previously generated images.
     * @returns {Promise<Object>} { success, total, images: [...] }
     */
    async getGallery() {
        try {
            const response = await fetch(`${this.BASE_URL}/api/gallery`);

            if (!response.ok) {
                throw new Error(`Erreur lors du chargement de la galerie (${response.status})`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('Impossible de contacter le serveur.');
            }
            throw error;
        }
    },

    /**
     * Delete an image by its ID.
     * @param {string|number} imageId
     * @returns {Promise<Object>}
     */
    async deleteImage(imageId) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/images/${imageId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(
                    errorData?.message || `Erreur lors de la suppression (${response.status})`
                );
            }

            const data = await response.json();
            return data;
        } catch (error) {
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('Impossible de contacter le serveur.');
            }
            throw error;
        }
    },

    /**
     * Fetch the list of available styles.
     * @returns {Promise<Object>}
     */
    async getStyles() {
        try {
            const response = await fetch(`${this.BASE_URL}/api/styles`);

            if (!response.ok) {
                throw new Error(`Erreur lors du chargement des styles (${response.status})`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('Impossible de contacter le serveur.');
            }
            throw error;
        }
    },

    /**
     * Build the full URL to serve a generated image.
     * @param {string} filename
     * @returns {string}
     */
    getImageUrl(filename) {
        return `${this.BASE_URL}/api/images/${filename}`;
    },
};
