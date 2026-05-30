/* ============================================================
   LogoForge AI — Gallery Manager
   Handles gallery loading, filtering, rendering, lightbox.
   ============================================================ */

const Gallery = {
    images: [],
    currentFilter: 'all',

    /**
     * Load gallery images from the API and render them.
     */
    async load() {
        try {
            const data = await API.getGallery();
            if (data.success) {
                this.images = data.images || [];
                this.render();
            }
        } catch (error) {
            console.error('Erreur lors du chargement de la galerie:', error);
            App.showToast('Impossible de charger la galerie', 'error');
        }
    },

    /**
     * Render gallery cards into the grid, applying the current filter.
     */
    render() {
        const grid = document.getElementById('gallery-grid');
        const emptyState = document.getElementById('gallery-empty');
        if (!grid) return;

        const filtered =
            this.currentFilter === 'all'
                ? this.images
                : this.images.filter((img) => img.style === this.currentFilter);

        if (filtered.length === 0) {
            grid.innerHTML = '';
            if (emptyState) emptyState.style.display = 'flex';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        grid.innerHTML = filtered
            .map((image, index) => this.createGalleryCard(image, index))
            .join('');

        // Staggered fade-in
        const cards = grid.querySelectorAll('.gallery-card');
        cards.forEach((card, i) => {
            card.style.animationDelay = `${i * 0.07}s`;
        });
    },

    /**
     * Filter gallery by style.
     * @param {string} style - Style name or 'all'
     */
    filter(style) {
        this.currentFilter = style;

        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.style === style);
        });

        this.render();
    },

    /**
     * Delete an image with confirmation.
     * @param {string|number} imageId
     */
    async deleteImage(imageId) {
        const confirmed = confirm('Supprimer cette image ? Cette action est irréversible.');
        if (!confirmed) return;

        try {
            const data = await API.deleteImage(imageId);
            if (data.success !== false) {
                App.showToast('Image supprimée avec succès', 'success');
                await this.load();
            } else {
                App.showToast(data.message || 'Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('Erreur suppression:', error);
            App.showToast(error.message || 'Erreur lors de la suppression', 'error');
        }
    },

    /**
     * Show a full-screen lightbox preview.
     * @param {string} imageUrl
     * @param {string} prompt
     */
    showLightbox(imageUrl, prompt) {
        const lightbox = document.getElementById('lightbox');
        const lbImage = document.getElementById('lightbox-image');
        const lbCaption = document.getElementById('lightbox-caption');
        if (!lightbox || !lbImage) return;

        lbImage.src = imageUrl;
        if (lbCaption) lbCaption.textContent = prompt || '';
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Close on background click
        lightbox.onclick = (e) => {
            if (e.target === lightbox || e.target.classList.contains('lightbox-close')) {
                this.closeLightbox();
            }
        };

        // Close on Escape
        this._escHandler = (e) => {
            if (e.key === 'Escape') this.closeLightbox();
        };
        document.addEventListener('keydown', this._escHandler);
    },

    /**
     * Close the lightbox.
     */
    closeLightbox() {
        const lightbox = document.getElementById('lightbox');
        if (lightbox) {
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }
        if (this._escHandler) {
            document.removeEventListener('keydown', this._escHandler);
            this._escHandler = null;
        }
    },

    /**
     * Build HTML string for a gallery card.
     * @param {Object} image
     * @param {number} index
     * @returns {string}
     */
    createGalleryCard(image, index) {
        const imageUrl = API.getImageUrl(image.filename);
        const date = image.created_at
            ? new Date(image.created_at).toLocaleDateString('fr-FR', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
              })
            : '';

        return `
        <div class="gallery-card fade-in-up" style="animation-delay: ${index * 0.07}s">
            <div class="gallery-card-image-wrapper">
                <img
                    src="${imageUrl}"
                    alt="${this._escapeHtml(image.prompt || 'Logo généré')}"
                    class="gallery-card-image"
                    loading="lazy"
                    onclick="Gallery.showLightbox('${imageUrl}', '${this._escapeHtml(image.prompt || '')}')"
                />
                <div class="gallery-card-overlay">
                    <button
                        class="gallery-overlay-btn"
                        onclick="Gallery.showLightbox('${imageUrl}', '${this._escapeHtml(image.prompt || '')}')"
                        title="Agrandir"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                        </svg>
                    </button>
                    <button
                        class="gallery-overlay-btn"
                        onclick="App.downloadImage('${imageUrl}', '${image.filename}')"
                        title="Télécharger"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                        </svg>
                    </button>
                    <button
                        class="gallery-overlay-btn delete-btn"
                        onclick="Gallery.deleteImage('${image.id}')"
                        title="Supprimer"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="gallery-card-meta">
                <p class="gallery-card-prompt" title="${this._escapeHtml(image.prompt || '')}">
                    ${this._escapeHtml(image.prompt || 'Sans description')}
                </p>
                <div class="gallery-card-details">
                    <span class="gallery-card-style">${this._escapeHtml(this._getStyleLabel(image.style) || '')}</span>
                    <span class="gallery-card-date">${date}</span>
                </div>
            </div>
        </div>`;
    },

    /**
     * Escape HTML special characters.
     */
    _escapeHtml(str) {
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return String(str).replace(/[&<>"']/g, (c) => map[c]);
    },

    /**
     * Get French label for a style value
     * @param {string} styleValue
     * @returns {string}
     */
    _getStyleLabel(styleValue) {
        const styleMap = {
            minimalist:  'Minimaliste',
            vintage:     'Vintage',
            three_d:     '3D',
            geometric:   'Géométrique',
            gradient:    'Dégradé',
            mascot:      'Mascotte',
            typographic: 'Typographique',
            abstract:    'Abstrait',
            flat:        'Flat Design',
            hand_drawn:  'Dessiné',
        };
        return styleMap[styleValue] || styleValue;
    },
};
