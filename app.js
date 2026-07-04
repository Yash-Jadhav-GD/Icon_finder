document.addEventListener('DOMContentLoaded', async () => {
    const iconGrid = document.getElementById('iconGrid');
    const searchInput = document.getElementById('searchInput');
    const categoryFilters = document.getElementById('categoryFilters');
    const resultCount = document.getElementById('resultCount');
    const loading = document.getElementById('loading');
    const toast = document.getElementById('toast');
    
    // Modal elements
    const modalOverlay = document.getElementById('iconModal');
    const closeModalBtn = document.getElementById('closeModal');
    const modalIconImg = document.getElementById('modalIconImg');
    const modalIconName = document.getElementById('modalIconName');
    const modalIconLabel = document.getElementById('modalIconLabel');
    const modalCopySvgBtn = document.getElementById('modalCopySvg');
    const modalCopyNameBtn = document.getElementById('modalCopyName');
    const relatedGrid = document.getElementById('relatedGrid');

    let allIcons = [];
    let currentFilter = 'all';
    let currentSource = 'both';
    let currentModalIcon = null;

    // Top categories based on common keywords
    const TOP_CATEGORIES = [
        { id: 'all', label: 'All' },
        { id: 'ai', label: 'AI / Artificial Intelligence' },
        { id: 'interface', label: 'Interface' },
        { id: 'system', label: 'System' },
        { id: 'media', label: 'Media' },
        { id: 'network', label: 'Network' },
        { id: 'business', label: 'Business' },
        { id: 'data', label: 'Data' },
        { id: 'security', label: 'Security' }
    ];

    // Load data
    try {
        loading.style.display = 'block';
        // Add cache busting so browser doesn't use old JSON
        const response = await fetch('icons.json?v=' + Date.now());
        if (!response.ok) throw new Error('Failed to load icons.json');
        allIcons = await response.json();
        
        init();
        filterIcons(); // render all initially
    } catch (error) {
        console.error("Error loading icons:", error);
        iconGrid.innerHTML = `<p style="color: red;">Failed to load icons. Make sure you are serving via HTTP server.</p>`;
    } finally {
        loading.style.display = 'none';
    }

    // Initialize sidebar and events
    function init() {
        // Build category filters dynamically
        categoryFilters.innerHTML = '';
        TOP_CATEGORIES.forEach(cat => {
            const btn = document.createElement('button');
            btn.className = `filter-btn ${cat.id === 'all' ? 'active' : ''}`;
            btn.dataset.filter = cat.id;
            btn.textContent = cat.label;
            
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = cat.id;
                filterIcons();
            });
            categoryFilters.appendChild(btn);
        });

        // Initialize Library Toggles
        document.querySelectorAll('.library-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.library-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                currentSource = e.target.dataset.source;
                filterIcons();
            });
        });

        // Setup search input
        searchInput.addEventListener('input', (e) => {
            filterIcons();
        });
    }

    function filterIcons() {
        let query = searchInput.value.toLowerCase().trim();
        query = query.replace('artificial intelligence', 'ai');
        const searchTerms = query.split(/\s+/).filter(t => t.length > 0);
        
        // Apply library source filter first
        let filtered = allIcons.filter(icon => {
            if (currentSource === 'gep') return !icon.source || icon.source !== 'external';
            if (currentSource === 'external') return icon.source === 'external';
            return true;
        });

        // Category filter
        if (currentFilter !== 'all') {
            filtered = filtered.filter(icon => {
                if (currentFilter === 'ai') {
                    // Use word boundaries so "ai" doesn't match "retail" and "bot" doesn't match "bottle"
                    const searchBase = ((icon.label || '') + ' ' + (icon.tags || []).join(' ')).toLowerCase();
                    return /\b(ai|robot|bot|chatbot|chip|microchip|artificial|intelligence|5g|brain)\b/i.test(searchBase);
                }
                return icon.tags && icon.tags.some(tag => tag === currentFilter || tag.includes(currentFilter));
            });
        }

        // Apply search query - MUST match ALL search terms (AND logic)
        if (searchTerms.length > 0) {
            filtered = filtered.map(icon => {
                const labelStr = (icon.label || '').toLowerCase();
                const tagsStr = (icon.tags || []).join(' ').toLowerCase();
                const searchBase = labelStr + " " + tagsStr;
                
                let isMatch = true;
                let score = 0;

                for (const term of searchTerms) {
                    let termMatch = false;
                    
                    if (term === 'ai') {
                        if (/\b(ai|robot|bot|chatbot|chip|microchip|artificial|intelligence|5g|brain)\b/i.test(searchBase)) {
                            termMatch = true;
                            score += 10;
                        }
                    } else {
                        // Word boundary match gives higher score
                        if (new RegExp('\\b' + term + '\\b', 'i').test(searchBase)) {
                            termMatch = true;
                            score += 5;
                        } else if (searchBase.includes(term)) {
                            termMatch = true;
                            score += 1;
                        }
                    }

                    if (!termMatch) {
                        isMatch = false;
                        break;
                    }
                }
                
                // Boost score if the term is in tags exactly
                if (isMatch && icon.tags) {
                    searchTerms.forEach(term => {
                        if (icon.tags.includes(term)) score += 10;
                    });
                }

                return isMatch ? { icon, score } : null;
            }).filter(item => item !== null);

            // Sort by relevance score descending
            filtered.sort((a, b) => b.score - a.score);
            
            // Map back to just the icon objects
            filtered = filtered.map(item => item.icon);
        }

        renderIcons(filtered, iconGrid, true);
    }

    // Get display name
    function getDisplayName(icon) {
        return icon.tags && icon.tags.length > 0 
                ? icon.tags.slice(0,2).join(' ') 
                : icon.file.replace('.svg', '').replace(/-[0-9]+$/, '');
    }

    // Create a DOM node for a single icon card
    function createIconCard(icon, isMainGrid) {
        const card = document.createElement('div');
        card.className = 'icon-card';
        if (icon.source === 'external') {
            card.classList.add('external-card');
        }
        
        const displayName = getDisplayName(icon);

        if (isMainGrid) {
            card.innerHTML = `
                <div class="card-actions-top">
                    <button class="info-btn" title="View Details">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    </button>
                </div>
                <div class="icon-img-wrapper">
                    <img src="icons/${icon.file}?v=4" alt="${displayName}" loading="lazy">
                </div>
                <div class="icon-name" title="${icon.label}">${displayName}</div>
                <div class="copy-overlay">
                    <button class="icon-only-btn copy-svg" data-file="icons/${icon.file}" title="Copy SVG">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    </button>
                </div>
            `;
        } else {
            card.innerHTML = `
                <div class="icon-img-wrapper" style="margin-bottom: 0;">
                    <img src="icons/${icon.file}?v=4" alt="${displayName}" loading="lazy">
                </div>
                <div class="icon-name" style="margin-top: 0.5rem;" title="${icon.label}">${displayName}</div>
            `;
        }
        
        // Click info button to open drawer
        const infoBtn = card.querySelector('.info-btn');
        if (infoBtn) {
            infoBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openModal(icon);
            });
        }

        // Click entire card to instantly copy SVG
        card.addEventListener('click', async () => {
            const success = await copySvg(icon.file);
            if (success) {
                const copyBtn = card.querySelector('.copy-svg');
                if (copyBtn) {
                    const originalHtml = copyBtn.innerHTML;
                    copyBtn.classList.add('copied');
                    copyBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                    
                    setTimeout(() => {
                        copyBtn.classList.remove('copied');
                        copyBtn.innerHTML = originalHtml;
                    }, 1500);
                }
            }
        });
        return card;
    }

    // Render icons to a specific container
    function renderIcons(iconsToRender, container, isMainGrid = false) {
        container.innerHTML = '';
        if (isMainGrid) {
            resultCount.textContent = iconsToRender.length;
        }

        const fragment = document.createDocumentFragment();
        const displayLimit = isMainGrid ? 300 : 12;
        const subset = iconsToRender.slice(0, displayLimit);

        if (!isMainGrid || currentSource !== 'both') {
            // Simple render for single library or related icons
            subset.forEach(icon => {
                if (!icon.file) return;
                fragment.appendChild(createIconCard(icon, isMainGrid));
            });
        } else {
            // Segmented render for 'both' libraries on main grid
            const gepIcons = subset.filter(i => !i.source || i.source !== 'external');
            const extIcons = subset.filter(i => i.source === 'external');

            gepIcons.forEach(icon => {
                if (!icon.file) return;
                fragment.appendChild(createIconCard(icon, true));
            });

            if (extIcons.length > 0 && gepIcons.length > 0) {
                const divider = document.createElement('div');
                divider.className = 'grid-divider';
                divider.innerHTML = '<span>External / 3rd-Party Icons</span>';
                fragment.appendChild(divider);
            }

            extIcons.forEach(icon => {
                if (!icon.file) return;
                fragment.appendChild(createIconCard(icon, true));
            });
        }

        container.appendChild(fragment);
        
        if (isMainGrid && iconsToRender.length > displayLimit) {
            const moreMsg = document.createElement('div');
            moreMsg.style.gridColumn = '1 / -1';
            moreMsg.style.textAlign = 'center';
            moreMsg.style.color = 'var(--text-secondary)';
            moreMsg.style.padding = '2rem';
            moreMsg.textContent = `Showing first ${displayLimit} of ${iconsToRender.length} icons. Keep typing to filter more.`;
            container.appendChild(moreMsg);
        }
    }

    // Modal Logic
    function openModal(icon) {
        currentModalIcon = icon;
        const displayName = getDisplayName(icon);
        
        modalIconImg.src = `icons/${icon.file}?v=4`;
        modalIconName.textContent = displayName;
        modalIconLabel.textContent = icon.label || 'No description available.';
        
        // Find related icons (shared tags)
        let related = [];
        if (icon.tags && icon.tags.length > 0) {
            related = allIcons.filter(i => {
                if (i.id === icon.id) return false;
                // Count shared tags
                const shared = (i.tags || []).filter(t => icon.tags.includes(t));
                i._score = shared.length;
                return shared.length > 0;
            });
            // Sort by most shared tags
            related.sort((a, b) => b._score - a._score);
        } else {
            // fallback: just grab some random or nearby icons
            related = allIcons.slice(0, 10).filter(i => i.id !== icon.id);
        }
        
        renderIcons(related, relatedGrid, false);
        
        modalOverlay.classList.add('open');
    }

    closeModalBtn.addEventListener('click', () => {
        modalOverlay.classList.remove('open');
    });

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.classList.remove('open');
        }
    });

    modalCopySvgBtn.addEventListener('click', () => {
        if (currentModalIcon) copySvg(currentModalIcon.file);
    });

    modalCopyNameBtn.addEventListener('click', async () => {
        if (currentModalIcon) {
            const name = getDisplayName(currentModalIcon);
            try {
                await navigator.clipboard.writeText(name);
                showToast('Copied name to clipboard!');
            } catch (err) {
                showToast('Failed to copy name', true);
            }
        }
    });

    async function copySvg(filename) {
        try {
            const res = await fetch(`icons/${filename}`);
            if (!res.ok) throw new Error("Could not fetch SVG");
            let svgText = await res.text();
            
            // Format SVG before copying (1.59cm size, 2.5pt stroke, #66737C color)
            try {
                const parser = new DOMParser();
                const doc = parser.parseFromString(svgText, "image/svg+xml");
                const svg = doc.querySelector("svg");
                
                if (svg) {
                    // Set physical dimensions
                    svg.setAttribute("width", "1.59cm");
                    svg.setAttribute("height", "1.59cm");
                    
                    // Calculate internal stroke width based on viewBox to ensure 2.5pt physical output
                    let vbWidth = 60; // default assuming 60x60
                    const viewBoxStr = svg.getAttribute("viewBox");
                    if (viewBoxStr) {
                        const parts = viewBoxStr.split(/[\s,]+/);
                        if (parts.length >= 4) {
                            vbWidth = parseFloat(parts[2]);
                        }
                    }
                    
                    // Target is 2.5pt = 3.333px
                    // 1.59cm = ~60px
                    // So if viewbox width is W, scaling factor is 60 / W
                    // We need internal_stroke * (60 / W) = 3.333
                    // internal_stroke = 3.333 * (W / 60)
                    const targetStrokePx = 3.33333;
                    const calculatedStroke = (targetStrokePx * (vbWidth / 60)).toFixed(3);
                    
                    // Modify stroke/fill and stroke-width on all descendants
                    const elements = doc.querySelectorAll("*");
                    elements.forEach(el => {
                        const currentStroke = el.getAttribute("stroke");
                        if (currentStroke && currentStroke.toLowerCase() !== "none") {
                            el.setAttribute("stroke", "#66737C");
                            el.setAttribute("stroke-width", calculatedStroke);
                        }
                        
                        const currentFill = el.getAttribute("fill");
                        if (currentFill && currentFill.toLowerCase() !== "none") {
                            el.setAttribute("fill", "#66737C");
                        }
                        
                        // Handle inline styles just in case
                        if (el.style) {
                            if (el.style.stroke && el.style.stroke.toLowerCase() !== "none") {
                                el.style.stroke = "#66737C";
                                el.style.strokeWidth = calculatedStroke + "px";
                            }
                            if (el.style.fill && el.style.fill.toLowerCase() !== "none") {
                                el.style.fill = "#66737C";
                            }
                        }
                    });
                    
                    const serializer = new XMLSerializer();
                    svgText = serializer.serializeToString(svg);
                }
            } catch(e) {
                console.error("Error formatting SVG for copy:", e);
            }
            
            try {
                // Try to write the actual file formats to the clipboard
                // This allows pasting the graphic directly into PowerPoint, Word, etc.
                const clipboardItem = new ClipboardItem({
                    'text/plain': new Blob([svgText], { type: 'text/plain' }),
                    'text/html': new Blob([svgText], { type: 'text/html' })
                });
                
                // image/svg+xml is supported in newer browsers and is the true way to copy vector files
                try {
                    const svgItem = new ClipboardItem({
                        'text/plain': new Blob([svgText], { type: 'text/plain' }),
                        'text/html': new Blob([svgText], { type: 'text/html' }),
                        'image/svg+xml': new Blob([svgText], { type: 'image/svg+xml' })
                    });
                    await navigator.clipboard.write([svgItem]);
                } catch (svgErr) {
                    // Fallback to HTML/text if image/svg+xml is rejected by the browser
                    await navigator.clipboard.write([clipboardItem]);
                }
            } catch (err) {
                // Absolute fallback (just copies code)
                await navigator.clipboard.writeText(svgText);
            }

            showToast('Copied SVG graphic to clipboard!');
            return true;
        } catch (err) {
            console.error(err);
            showToast('Failed to copy SVG', true);
            return false;
        }
    }

    let toastTimeout;
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.style.backgroundColor = isError ? '#ef4444' : 'var(--text-primary)';
        toast.style.color = isError ? 'white' : 'var(--surface-color)';
        toast.classList.add('show');
        
        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
