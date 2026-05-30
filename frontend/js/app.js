/* ============================================================
   Brandora AI — Main Application Controller
   ============================================================ */

const App = {
    selectedStyle: 'minimalist',
    selectedNumImages: 1,
    isGenerating: false,

    /* ------ Style metadata ------ */
    STYLE_MAP: {
        minimalist:  { icon: '◯',  label: 'Minimaliste' },
        vintage:     { icon: '🏛️', label: 'Vintage' },
        three_d:     { icon: '🧊', label: '3D' },
        geometric:   { icon: '◆',  label: 'Géométrique' },
        gradient:    { icon: '🌈', label: 'Dégradé' },
        mascot:      { icon: '🐾', label: 'Mascotte' },
        typographic: { icon: 'Aa', label: 'Typographique' },
        abstract:    { icon: '🎨', label: 'Abstrait' },
        flat:        { icon: '▢',  label: 'Flat Design' },
        hand_drawn:  { icon: '✏️', label: 'Dessiné' },
    },

    getStyleLabel(styleValue) {
        return this.STYLE_MAP[styleValue]?.label || styleValue;
    },

    /* ------ Color presets ------ */
    COLOR_PRESETS: [
        { name: 'Violet & Cyan',  value: '#8b5cf6, #06b6d4',  colors: ['#8b5cf6', '#06b6d4'] },
        { name: 'Rose & Or',      value: '#ec4899, #f59e0b',  colors: ['#ec4899', '#f59e0b'] },
        { name: 'Vert & Bleu',    value: '#10b981, #3b82f6',  colors: ['#10b981', '#3b82f6'] },
        { name: 'Rouge & Noir',   value: '#ef4444, #1e1e1e',  colors: ['#ef4444', '#1e1e1e'] },
        { name: 'Bleu & Blanc',   value: '#3b82f6, #f8fafc',  colors: ['#3b82f6', '#f8fafc'] },
        { name: 'Or & Marine',    value: '#eab308, #1e3a5f',  colors: ['#eab308', '#1e3a5f'] },
    ],

    /* ==========================================================
       Initialization
       ========================================================== */
    init() {
        this.setupNavbar();
        this.setupStyleSelector();
        this.setupColorPresets();
        this.setupGenerateButton();
        this.setupFilterBar();
        this.setupScrollReveal();
        this.setupCharCount();
        Gallery.load();
    },

    /* ==========================================================
       Navbar — scroll effect + active link
       ========================================================== */
    setupNavbar() {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;

        // Scroll shadow
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 20);
        }, { passive: true });

        // Active nav link on scroll
        const sections = ['generator', 'gallery'];
        const links = document.querySelectorAll('.nav-link');

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        links.forEach((l) => l.classList.remove('active'));
                        const active = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
                        if (active) active.classList.add('active');
                    }
                });
            },
            { threshold: 0.4 }
        );

        sections.forEach((id) => {
            const el = document.getElementById(id);
            if (el) observer.observe(el);
        });
    },

    /* ==========================================================
       Char Counter for prompt
       ========================================================== */
    setupCharCount() {
        const textarea = document.getElementById('prompt-input');
        const counter  = document.getElementById('prompt-char-count');
        if (!textarea || !counter) return;

        const MAX = 500;
        textarea.setAttribute('maxlength', MAX);

        const updateCount = () => {
            const len = textarea.value.length;
            counter.textContent = `${len} / ${MAX}`;
            counter.style.color = len > MAX * 0.9 ? 'var(--accent)' : 'var(--text-muted)';
        };

        textarea.addEventListener('input', updateCount);
        updateCount(); // Run once initially
    },

    /* ==========================================================
       Style Selector
       ========================================================== */
    setupStyleSelector() {
        const container = document.getElementById('style-selector');
        if (!container) return;

        container.innerHTML = '';

        Object.entries(this.STYLE_MAP).forEach(([key, { icon, label }]) => {
            const card = document.createElement('div');
            card.className = `style-card${key === this.selectedStyle ? ' active' : ''}`;
            card.dataset.style = key;
            card.setAttribute('role', 'radio');
            card.setAttribute('aria-checked', key === this.selectedStyle ? 'true' : 'false');
            card.setAttribute('tabindex', key === this.selectedStyle ? '0' : '-1');
            card.innerHTML = `
                <span class="style-card-icon">${icon}</span>
                <span class="style-card-label">${label}</span>
            `;
            card.addEventListener('click', () => this.selectStyle(key));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.selectStyle(key); }
            });
            container.appendChild(card);
        });
    },

    selectStyle(style) {
        this.selectedStyle = style;
        document.querySelectorAll('.style-card').forEach((c) => {
            const isActive = c.dataset.style === style;
            c.classList.toggle('active', isActive);
            c.setAttribute('aria-checked', isActive ? 'true' : 'false');
            c.setAttribute('tabindex', isActive ? '0' : '-1');
        });
    },

    /* ==========================================================
       Color Presets
       ========================================================== */
    setupColorPresets() {
        const container  = document.getElementById('color-presets');
        const colorInput = document.getElementById('color-input');
        if (!container) return;

        container.innerHTML = '';

        this.COLOR_PRESETS.forEach((preset, idx) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            // No preset active by default — user picks manually
            btn.className = 'color-preset-btn';
            btn.title = preset.name;
            btn.dataset.value = preset.value;
            btn.innerHTML = `
                <span class="color-swatch" style="background:linear-gradient(135deg,${preset.colors[0]},${preset.colors[1]})"></span>
                <span class="color-preset-label">${preset.name}</span>
            `;
            btn.addEventListener('click', () => {
                if (colorInput) colorInput.value = preset.value;
                document.querySelectorAll('.color-preset-btn').forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
            });
            container.appendChild(btn);
        });
        // Color input starts empty — user fills it manually or picks a preset
    },

    /* ==========================================================
       Generate Button
       ========================================================== */
    setupGenerateButton() {
        const btn = document.getElementById('generate-btn');
        if (btn) btn.addEventListener('click', () => this.generate());

        const textarea = document.getElementById('prompt-input');
        if (textarea) {
            textarea.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    this.generate();
                }
            });
        }
    },

    /* ==========================================================
       Filter Bar (Gallery)
       ========================================================== */
    setupFilterBar() {
        const bar = document.getElementById('filter-bar');
        if (!bar) return;

        const allBtn = document.createElement('button');
        allBtn.type = 'button';
        allBtn.className = 'filter-btn active';
        allBtn.textContent = 'Tous';
        allBtn.dataset.style = 'all';
        allBtn.addEventListener('click', () => Gallery.filter('all'));
        bar.appendChild(allBtn);

        Object.entries(this.STYLE_MAP).forEach(([key, { icon, label }]) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'filter-btn';
            btn.textContent = `${icon} ${label}`;
            btn.dataset.style = key;
            btn.addEventListener('click', () => Gallery.filter(key));
            bar.appendChild(btn);
        });
    },

    /* ==========================================================
       Scroll Reveal
       ========================================================== */
    setupScrollReveal() {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) entry.target.classList.add('revealed');
                });
            },
            { threshold: 0.08 }
        );
        document.querySelectorAll('.section-reveal').forEach((el) => observer.observe(el));
    },

    /* ==========================================================
       Progress Bar animation (remplace l'overlay bloquant)
       ========================================================== */
    _progressTimer: null,
    _progressValue: 0,

    startLoadingSteps() {
        const bar = document.getElementById('progress-bar-inner');
        const textEl = document.getElementById('progress-bar-text');
        this._progressValue = 0;
        if (bar) bar.style.width = '0%';

        const messages = [
            '⚡ Interprétation du prompt...',
            '🎨 Création du logo...',
            '✨ Raffinement en cours...',
        ];
        let msgIdx = 0;
        if (textEl) textEl.textContent = messages[0];

        // Animate progress bar from 0 → 85% smoothly
        this._progressTimer = setInterval(() => {
            if (this._progressValue < 85) {
                this._progressValue += (85 - this._progressValue) * 0.04;
                if (bar) bar.style.width = this._progressValue + '%';
            }
            // Cycle messages
            msgIdx = (msgIdx + 1) % messages.length;
            if (textEl) textEl.textContent = messages[msgIdx];
        }, 1500);
    },

    stopLoadingSteps() {
        if (this._progressTimer) {
            clearInterval(this._progressTimer);
            this._progressTimer = null;
        }
        // Complete the bar
        const bar = document.getElementById('progress-bar-inner');
        const textEl = document.getElementById('progress-bar-text');
        if (bar) bar.style.width = '100%';
        if (textEl) textEl.textContent = '✅ Logo généré !';
    },

    /* ==========================================================
       Generate Logos
       ========================================================== */
    _elapsedTimer: null,

    async generate() {
        if (this.isGenerating) return;

        const promptEl    = document.getElementById('prompt-input');
        const colorEl     = document.getElementById('color-input');
        const brandNameEl = document.getElementById('brand-name-input');
        const genBtn      = document.getElementById('generate-btn');

        const prompt    = promptEl?.value.trim()    || '';
        const colors    = colorEl?.value.trim()     || '';
        const brandName = brandNameEl?.value.trim() || '';

        if (prompt.length < 3) {
            this.showToast('Veuillez entrer une description d\'au moins 3 caractères.', 'error');
            if (promptEl) {
                promptEl.focus();
                promptEl.classList.add('input-error');
                setTimeout(() => promptEl.classList.remove('input-error'), 1500);
            }
            return;
        }

        this.isGenerating = true;

        // Désactiver le bouton et afficher le timer
        if (genBtn) {
            genBtn.disabled = true;
            genBtn.querySelector('.generate-btn-label').textContent = 'Génération... 0s';
        }

        // Timer qui compte les secondes écoulées
        let elapsed = 0;
        this._elapsedTimer = setInterval(() => {
            elapsed++;
            const textEl = document.getElementById('progress-bar-text');
            const btnLabel = genBtn?.querySelector('.generate-btn-label');
            if (textEl) textEl.textContent = `⚡ Génération en cours... ${elapsed}s`;
            if (btnLabel) btnLabel.textContent = `Génération... ${elapsed}s`;
        }, 1000);

        this.showLoading();
        this.startLoadingSteps();

        try {
            const data = await API.generateLogos(
                prompt,
                this.selectedStyle,
                colors,
                this.selectedNumImages,
                brandName,
            );

            if (data.success && data.images && data.images.length > 0) {
                this.renderResults(data.images);
                this.showToast(
                    `✅ Logo généré en ${elapsed}s !`,
                    'success'
                );
                await Gallery.load();
            } else {
                const errorMsg = data.detail || data.message || 'La génération a échoué.';
                this.showToast(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Erreur génération:', error);
            let errorMsg = 'Une erreur est survenue.';
            
            // Try to extract API error message
            if (error.detail) {
                errorMsg = error.detail;
            } else if (error.message) {
                errorMsg = error.message;
            }
            
            this.showToast(errorMsg, 'error');
        } finally {
            this.isGenerating = false;
            if (this._elapsedTimer) {
                clearInterval(this._elapsedTimer);
                this._elapsedTimer = null;
            }
            // Réactiver le bouton
            if (genBtn) {
                genBtn.disabled = false;
                genBtn.querySelector('.generate-btn-label').textContent = 'Générer mon Logo';
            }
            this.stopLoadingSteps();
            this.hideLoading();
        }
    },

    /* ==========================================================
       Render Results
       ========================================================== */
    renderResults(images) {
        const section = document.getElementById('results');
        const grid    = document.getElementById('results-grid');
        if (!section || !grid) return;

        section.style.display = 'block';

        // Retrieve brand name entered by user
        const brandNameEl = document.getElementById('brand-name-input');
        const brandName   = brandNameEl?.value.trim() || '';

        // Update results count
        const countEl = document.getElementById('results-count');
        if (countEl) {
            countEl.textContent = `${images.length} logo${images.length > 1 ? 's' : ''} généré${images.length > 1 ? 's' : ''}`;
        }

        // Store images for download-all
        this._lastGeneratedImages = images;

        // Setup download-all button
        const downloadAllBtn = document.getElementById('download-all-btn');
        if (downloadAllBtn) {
            downloadAllBtn.onclick = () => {
                images.forEach(img => {
                    this.downloadImage(API.getImageUrl(img.filename), img.filename);
                });
                this.showToast('Téléchargement de tous les logos lancé !', 'success');
            };
        }

        grid.innerHTML = images
            .map((image, index) => {
                const imageUrl   = API.getImageUrl(image.filename);
                const styleLabel = this.getStyleLabel(image.style || this.selectedStyle);
                const displayName = brandName || 'Logo';
                const escapedPrompt = Gallery._escapeHtml(image.prompt || '');
                const escapedName   = Gallery._escapeHtml(displayName);
                const escapedStyle  = Gallery._escapeHtml(styleLabel);
                return `
                <div class="result-card fade-in-up" style="animation-delay:${index * 0.12}s">

                    <!-- Logo Preview Area -->
                    <div class="result-card-image-wrapper" onclick="Gallery.showLightbox('${imageUrl}','${escapedPrompt}')">
                        <img
                            src="${imageUrl}"
                            alt="${escapedName}"
                            class="result-card-image"
                            loading="lazy"
                        />
                        <!-- Zoom overlay on hover -->
                        <div class="result-card-zoom-overlay">
                            <button class="zoom-icon-btn" type="button" title="Agrandir">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Card Info Strip -->
                    <div class="result-card-info">
                        <!-- Brand name + style badge row -->
                        <div class="result-card-brand-row">
                            <p class="result-card-brand-name">${escapedName}</p>
                            <span class="result-card-style">${escapedStyle}</span>
                        </div>

                        <!-- Action buttons -->
                        <div class="result-card-actions">
                            <button
                                class="result-action-btn btn-download"
                                onclick="App.downloadImage('${imageUrl}','${image.filename}')"
                                title="Télécharger"
                                type="button"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                                </svg>
                                Télécharger
                            </button>
                            <button
                                class="result-action-btn btn-expand"
                                onclick="Gallery.showLightbox('${imageUrl}','${escapedPrompt}')"
                                title="Agrandir"
                                type="button"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                                </svg>
                                Aperçu
                            </button>
                            <button
                                class="result-action-btn btn-remix"
                                onclick="App.remixLogo('${escapedPrompt}')"
                                title="Créer une variante"
                                type="button"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M17 1l4 4-4 4"/>
                                    <path d="M3 11V9a4 4 0 014-4h14"/>
                                    <path d="M7 23l-4-4 4-4"/>
                                    <path d="M21 13v2a4 4 0 01-4 4H3"/>
                                </svg>
                                Variante
                            </button>
                        </div>
                    </div>

                    <!-- Mockup Preview Strip -->
                    <div class="result-card-mockups">
                        <div class="mockup-thumb" title="Carte de visite">
                            <div class="mockup-thumb-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M8 11h8M8 14h4"/></svg>
                                <span class="mockup-thumb-label">Carte</span>
                            </div>
                        </div>
                        <div class="mockup-thumb" title="Icône d'app">
                            <div class="mockup-thumb-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="4"/><circle cx="12" cy="12" r="3"/></svg>
                                <span class="mockup-thumb-label">App</span>
                            </div>
                        </div>
                        <div class="mockup-thumb" title="Réseaux sociaux">
                            <div class="mockup-thumb-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>
                                <span class="mockup-thumb-label">Social</span>
                            </div>
                        </div>
                    </div>

                </div>`;
            })
            .join('');

        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    /* ==========================================================
       Quick Regenerate — relance immédiate avec les mêmes réglages
       ========================================================== */
    quickRegenerate() {
        if (this.isGenerating) return;
        this.showToast('⚡ Régénération rapide en cours...', 'success');
        this.generate();
    },

    /* ==========================================================
       Remix Logo — refill prompt and regenerate
       ========================================================== */
    remixLogo(prompt) {
        const promptEl = document.getElementById('prompt-input');
        if (promptEl && prompt) {
            promptEl.value = decodeURIComponent(prompt);
            promptEl.dispatchEvent(new Event('input'));
        }
        document.getElementById('generator')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        this.showToast('Prompt pré-rempli — modifiez et relancez !', 'success');
    },

    /* ==========================================================
       Download
       ========================================================== */
    downloadImage(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'logo.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    },

    /* ==========================================================
       Toast Notifications
       ========================================================== */
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconSvg = type === 'success'
            ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
            : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';

        toast.innerHTML = `
            <span class="toast-icon">${iconSvg}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" type="button" onclick="this.parentElement.remove()" aria-label="Fermer">&times;</button>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 350);
        }, 4000);
    },

    /* ==========================================================
       Barre de progression compacte (non-bloquante)
       ========================================================== */
    showLoading() {
        const wrap = document.getElementById('loading-overlay');
        const bar  = document.getElementById('progress-bar-inner');
        if (wrap) {
            wrap.classList.add('active');
            wrap.setAttribute('aria-hidden', 'false');
        }
        if (bar) bar.style.width = '0%';
        // La page reste scrollable — pas de overflow:hidden
    },

    hideLoading() {
        const wrap = document.getElementById('loading-overlay');
        if (wrap) {
            // Court délai pour montrer 100% avant de masquer
            setTimeout(() => {
                wrap.classList.remove('active');
                wrap.setAttribute('aria-hidden', 'true');
                const bar = document.getElementById('progress-bar-inner');
                if (bar) bar.style.width = '0%';
            }, 600);
        }
    },
};

/* ==========================================================
   Boot
   ========================================================== */
document.addEventListener('DOMContentLoaded', () => App.init());
