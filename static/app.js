// MyWalt App State
const state = {
    currentPath: '',
    currentItems: [],
    drives: [],
    favorites: [],
    viewMode: 'grid', // 'grid' or 'list'
    theme: 'light',
    sortBy: 'name',
    categoryFilter: 'all',
    searchMode: 'name', // 'name' or 'fulltext'
    searchActive: false,
    selectedFileForRename: null,
    editingFilePath: null,
    uploadQueue: [],
    galleryImages: [],
    galleryIndex: 0,
    sysStatsInterval: null,
    remotePcLooping: false,
    clipboard: { action: null, sources: [] },
    activeHoverPath: null
};

// Helper token getter
function getToken() {
    return localStorage.getItem('mywalt_token') || '';
}

// DOM Elements
const el = {
    loginModal: document.getElementById('login-modal'),
    loginForm: document.getElementById('login-form'),
    loginPassword: document.getElementById('login-password'),
    loginError: document.getElementById('login-error'),
    
    app: document.getElementById('app'),
    searchInput: document.getElementById('search-input'),
    searchClearBtn: document.getElementById('search-clear-btn'),
    btnSearchModeToggle: document.getElementById('btn-search-mode-toggle'),
    searchModeLabel: document.getElementById('search-mode-label'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    btnLogout: document.getElementById('btn-logout'),
    btnSidebarSettings: document.getElementById('btn-sidebar-settings'),
    btnSysDash: document.getElementById('btn-sys-dash'),
    btnRemotePc: document.getElementById('btn-remote-pc'),
    btnWebTerminal: document.getElementById('btn-web-terminal'),
    btnStorageAnalyzer: document.getElementById('btn-storage-analyzer'),
    btnPinFav: document.getElementById('btn-pin-fav'),
    btnDownloadZip: document.getElementById('btn-download-zip'),
    btnPaste: document.getElementById('btn-paste'),
    pasteCount: document.getElementById('paste-count'),
    
    treeNav: document.getElementById('tree-nav'),
    favoritesNav: document.getElementById('favorites-nav'),
    storagePct: document.getElementById('storage-pct'),
    storageFill: document.getElementById('storage-fill'),
    storageMeta: document.getElementById('storage-meta'),
    
    breadcrumbs: document.getElementById('breadcrumbs'),
    btnUp: document.getElementById('btn-up'),
    btnRefresh: document.getElementById('btn-refresh'),
    sortSelect: document.getElementById('sort-select'),
    btnGridView: document.getElementById('btn-grid-view'),
    btnListView: document.getElementById('btn-list-view'),
    
    searchBanner: document.getElementById('search-banner'),
    searchQueryText: document.getElementById('search-query-text'),
    searchCountText: document.getElementById('search-count-text'),
    btnCloseSearch: document.getElementById('btn-close-search'),
    
    foldersSection: document.getElementById('folders-section'),
    foldersGrid: document.getElementById('folders-grid'),
    foldersCount: document.getElementById('folders-count'),
    foldersHeader: document.getElementById('folders-header'),
    
    filesSection: document.getElementById('files-section'),
    filesGrid: document.getElementById('files-grid'),
    filesCount: document.getElementById('files-count'),
    filesHeader: document.getElementById('files-header'),
    
    statusCount: document.getElementById('status-count'),
    statusPath: document.getElementById('status-path'),
    
    fabMain: document.getElementById('fab-main'),
    fabMenu: document.getElementById('fab-menu'),
    fabUpload: document.getElementById('fab-upload'),
    fabNewFolder: document.getElementById('fab-new-folder'),
    fabNewFile: document.getElementById('fab-new-file'),
    fabCompress: document.getElementById('fab-compress'),
    
    uploadToast: document.getElementById('upload-toast'),
    uploadStatusTitle: document.getElementById('upload-status-title'),
    uploadTotalPct: document.getElementById('upload-total-pct'),
    toastBarFill: document.getElementById('toast-bar-fill'),
    toastFileList: document.getElementById('toast-file-list'),
    toastClose: document.getElementById('toast-close'),
    
    globalDragOverlay: document.getElementById('global-drag-overlay'),
    
    uploadModal: document.getElementById('upload-modal'),
    dropZone: document.getElementById('drop-zone'),
    uploadFileInput: document.getElementById('upload-file-input'),
    uploadFileList: document.getElementById('upload-file-list'),
    btnStartUpload: document.getElementById('btn-start-upload'),
    
    newItemModal: document.getElementById('new-item-modal'),
    newItemTitle: document.getElementById('new-item-title'),
    newItemName: document.getElementById('new-item-name'),
    btnConfirmCreate: document.getElementById('btn-confirm-create'),
    
    renameModal: document.getElementById('rename-modal'),
    renameInput: document.getElementById('rename-input'),
    btnConfirmRename: document.getElementById('btn-confirm-rename'),
    
    compressModal: document.getElementById('compress-modal'),
    compressName: document.getElementById('compress-name'),
    btnConfirmCompress: document.getElementById('btn-confirm-compress'),

    editorModal: document.getElementById('editor-modal'),
    editorTitle: document.getElementById('editor-title'),
    fileEditorText: document.getElementById('file-editor-text'),
    btnSaveFile: document.getElementById('btn-save-file'),
    
    previewModal: document.getElementById('preview-modal'),
    previewTitle: document.getElementById('preview-title'),
    previewContainer: document.getElementById('preview-container'),

    lightboxModal: document.getElementById('lightbox-modal'),
    lightboxImg: document.getElementById('lightbox-img'),
    lightboxCaption: document.getElementById('lightbox-caption'),
    lightboxClose: document.getElementById('lightbox-close'),
    lightboxPrev: document.getElementById('lightbox-prev'),
    lightboxNext: document.getElementById('lightbox-next'),

    sysModal: document.getElementById('sys-modal'),
    sysCpuVal: document.getElementById('sys-cpu-val'),
    sysCpuBar: document.getElementById('sys-cpu-bar'),
    sysMemVal: document.getElementById('sys-mem-val'),
    sysMemBar: document.getElementById('sys-mem-bar'),
    sysUptimeVal: document.getElementById('sys-uptime-val'),
    sysHostVal: document.getElementById('sys-host-val'),

    remotePcModal: document.getElementById('remote-pc-modal'),
    remoteScreenImg: document.getElementById('remote-screen-img'),
    remoteTypeForm: document.getElementById('remote-type-form'),
    remoteTypeInput: document.getElementById('remote-type-input'),
    btnToggleFullscreen: document.getElementById('btn-toggle-fullscreen'),

    terminalModal: document.getElementById('terminal-modal'),
    terminalOutput: document.getElementById('terminal-output'),
    terminalForm: document.getElementById('terminal-form'),
    terminalInput: document.getElementById('terminal-input'),

    storageModal: document.getElementById('storage-modal'),
    storageAnalyzerContent: document.getElementById('storage-analyzer-content'),

    settingsModal: document.getElementById('settings-modal'),
    settingsForm: document.getElementById('settings-form'),
    settingsOldPass: document.getElementById('settings-old-pass'),
    settingsNewPass: document.getElementById('settings-new-pass'),
    settingsMsg: document.getElementById('settings-msg')
};

let newItemIsDirectory = false;

// API Helper
async function api(endpoint, options = {}) {
    options.headers = options.headers || {};
    const token = getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    try {
        const response = await fetch(endpoint, options);
        if (response.status === 401) {
            showLogin();
            throw new Error('Authentication required');
        }
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'API Request Failed');
        }
        return data;
    } catch (err) {
        throw err;
    }
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
});

async function checkStatus() {
    try {
        const res = await api('/api/status');
        if (res.is_authenticated) {
            hideLogin();
            loadDrives();
            loadFavorites();
            loadDirectory('');
        } else {
            showLogin();
        }
    } catch (err) {
        showLogin();
    }
}

function showLogin() {
    el.loginModal.classList.remove('hidden');
    el.app.classList.add('hidden');
    el.loginPassword.value = '';
    el.loginError.classList.add('hidden');
}

function hideLogin() {
    el.loginModal.classList.add('hidden');
    el.app.classList.remove('hidden');
}

// Setup Event Handlers
function setupEventListeners() {
    // Login
    el.loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const password = el.loginPassword.value;
        try {
            const res = await api('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            if (res.token) {
                localStorage.setItem('mywalt_token', res.token);
            }
            hideLogin();
            loadDrives();
            loadFavorites();
            loadDirectory('');
        } catch (err) {
            el.loginError.textContent = err.message;
            el.loginError.classList.remove('hidden');
        }
    });

    // Logout
    el.btnLogout.addEventListener('click', async () => {
        try { await api('/api/logout', { method: 'POST' }); } catch (e) {}
        localStorage.removeItem('mywalt_token');
        showLogin();
    });

    // Theme Toggle
    el.btnThemeToggle.addEventListener('click', () => {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.body.className = `${state.theme}-theme`;
        el.btnThemeToggle.innerHTML = state.theme === 'light' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
    });

    // View Mode Toggle
    el.btnGridView.addEventListener('click', () => {
        state.viewMode = 'grid';
        el.btnGridView.classList.add('active');
        el.btnListView.classList.remove('active');
        renderContent(state.currentItems);
    });

    el.btnListView.addEventListener('click', () => {
        state.viewMode = 'list';
        el.btnListView.classList.add('active');
        el.btnGridView.classList.remove('active');
        renderContent(state.currentItems);
    });

    // Category Filter Pills
    document.querySelectorAll('.filter-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.categoryFilter = pill.getAttribute('data-cat');
            sortAndRenderContent();
        });
    });

    // Search Mode Switcher (Name vs Full-Text)
    el.btnSearchModeToggle.addEventListener('click', () => {
        if (state.searchMode === 'name') {
            state.searchMode = 'fulltext';
            el.searchModeLabel.textContent = 'Full-Text Content';
            el.btnSearchModeToggle.classList.add('fulltext');
        } else {
            state.searchMode = 'name';
            el.searchModeLabel.textContent = 'Name Search';
            el.btnSearchModeToggle.classList.remove('fulltext');
        }
        if (el.searchInput.value.trim().length >= 2) {
            executeSearch(el.searchInput.value.trim());
        }
    });

    // Sort Dropdown
    el.sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        sortAndRenderContent();
    });

    // Favorites Pin Toggle Button
    el.btnPinFav.addEventListener('click', () => toggleFavoriteCurrentPath());

    // Download ZIP Current Directory
    el.btnDownloadZip.addEventListener('click', () => {
        if (!state.currentPath) return;
        const zipUrl = `/api/archive/download-zip?path=${encodeURIComponent(state.currentPath)}&token=${encodeURIComponent(getToken())}`;
        window.open(zipUrl, '_blank');
    });

    // Paste Action Button (Ctrl+V)
    el.btnPaste.addEventListener('click', () => pasteClipboard());

    // LIVE REMOTE PC CONTROL MODAL & FULLSCREEN TOGGLE
    el.btnRemotePc.addEventListener('click', () => {
        openModal(el.remotePcModal);
        state.remotePcLooping = true;
        startUltraFastRemoteLoop();
    });

    if (el.btnToggleFullscreen) {
        el.btnToggleFullscreen.addEventListener('click', () => {
            if (!document.fullscreenElement) {
                if (el.remotePcModal.requestFullscreen) el.remotePcModal.requestFullscreen();
                else if (el.remotePcModal.webkitRequestFullscreen) el.remotePcModal.webkitRequestFullscreen();
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
            }
        });
    }

    // Remote PC Mouse Clicks
    el.remoteScreenImg.addEventListener('click', (e) => {
        const rect = el.remoteScreenImg.getBoundingClientRect();
        const relX = (e.clientX - rect.left) / rect.width;
        const relY = (e.clientY - rect.top) / rect.height;
        api('/api/remote/mouse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'click', rel_x: relX, rel_y: relY, button: 'left' })
        });
        setTimeout(refreshRemoteScreenFast, 30);
    });

    el.remoteScreenImg.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const rect = el.remoteScreenImg.getBoundingClientRect();
        const relX = (e.clientX - rect.left) / rect.width;
        const relY = (e.clientY - rect.top) / rect.height;
        api('/api/remote/mouse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'rightclick', rel_x: relX, rel_y: relY, button: 'right' })
        });
        setTimeout(refreshRemoteScreenFast, 30);
    });

    // Remote PC Keyboard Shortcut Buttons
    document.querySelectorAll('.remote-key-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const sc = btn.getAttribute('data-shortcut');
            const k = btn.getAttribute('data-key');
            api('/api/remote/keyboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ shortcut: sc || null, key: k || null })
            });
            setTimeout(refreshRemoteScreenFast, 50);
        });
    });

    // Remote PC Send Text Input
    el.remoteTypeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = el.remoteTypeInput.value;
        if (!text) return;
        api('/api/remote/keyboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        el.remoteTypeInput.value = '';
        setTimeout(refreshRemoteScreenFast, 50);
    });

    // System Dashboard Modal Toggle
    el.btnSysDash.addEventListener('click', () => {
        openModal(el.sysModal);
        refreshSystemStats();
        if (!state.sysStatsInterval) {
            state.sysStatsInterval = setInterval(refreshSystemStats, 3000);
        }
    });

    // Remote Power Controls
    document.querySelectorAll('.power-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const action = btn.getAttribute('data-action');
            if (confirm(`Are you sure you want to ${action.toUpperCase()} the host PC?`)) {
                try {
                    const res = await api('/api/system/power', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action })
                    });
                    alert(res.message);
                } catch (err) {
                    alert('Power action failed: ' + err.message);
                }
            }
        });
    });

    // Web Terminal Console Modal
    el.btnWebTerminal.addEventListener('click', () => {
        openModal(el.terminalModal);
        el.terminalInput.focus();
    });

    el.terminalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const cmd = el.terminalInput.value.trim();
        if (!cmd) return;
        appendTerminalLine(`PS ${state.currentPath}> ${cmd}`, 'cmd');
        el.terminalInput.value = '';

        try {
            const res = await api('/api/system/terminal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd, cwd: state.currentPath })
            });

            if (res.stdout) appendTerminalLine(res.stdout, 'out');
            if (res.stderr) appendTerminalLine(res.stderr, 'err');
        } catch (err) {
            appendTerminalLine('Execution error: ' + err.message, 'err');
        }
    });

    // Storage Analyzer Modal
    el.btnStorageAnalyzer.addEventListener('click', async () => {
        openModal(el.storageModal);
        el.storageAnalyzerContent.innerHTML = '<p class="text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Calculating folder space breakdown...</p>';
        try {
            const res = await api(`/api/storage/analyze?path=${encodeURIComponent(state.currentPath)}`);
            renderStorageAnalysis(res);
        } catch (err) {
            el.storageAnalyzerContent.innerHTML = `<p class="error-banner">Failed to analyze folder space: ${err.message}</p>`;
        }
    });

    // Image Lightbox Gallery Controls
    el.lightboxClose.addEventListener('click', () => closeModal(el.lightboxModal));
    el.lightboxPrev.addEventListener('click', () => navigateLightbox(-1));
    el.lightboxNext.addEventListener('click', () => navigateLightbox(1));

    // Settings Modal
    el.btnSidebarSettings.addEventListener('click', () => openModal(el.settingsModal));
    el.settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await api('/api/set-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    old_password: el.settingsOldPass.value || null,
                    new_password: el.settingsNewPass.value
                })
            });
            el.settingsMsg.textContent = 'Password updated successfully!';
            el.settingsMsg.className = 'message-banner success';
            el.settingsMsg.classList.remove('hidden');
            setTimeout(() => {
                closeModal(el.settingsModal);
                el.settingsForm.reset();
                el.settingsMsg.classList.add('hidden');
            }, 1500);
        } catch (err) {
            el.settingsMsg.textContent = err.message;
            el.settingsMsg.className = 'message-banner';
            el.settingsMsg.classList.remove('hidden');
        }
    });

    // Toolbar buttons
    el.btnRefresh.addEventListener('click', () => loadDirectory(state.currentPath));
    el.btnUp.addEventListener('click', () => navigateUp());

    // Collapsible Sections
    el.foldersHeader.addEventListener('click', () => {
        el.foldersGrid.classList.toggle('hidden');
        el.foldersHeader.querySelector('.section-arrow').style.transform = el.foldersGrid.classList.contains('hidden') ? 'rotate(-90deg)' : 'rotate(0deg)';
    });

    el.filesHeader.addEventListener('click', () => {
        el.filesGrid.classList.toggle('hidden');
        el.filesHeader.querySelector('.section-arrow').style.transform = el.filesGrid.classList.contains('hidden') ? 'rotate(-90deg)' : 'rotate(0deg)';
    });

    // Modal Close Buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal-overlay');
            if (modal) closeModal(modal);
        });
    });

    // FAB Button Toggle
    el.fabMain.addEventListener('click', () => {
        el.fabMain.classList.toggle('active');
        el.fabMenu.classList.toggle('hidden');
    });

    el.fabUpload.addEventListener('click', () => {
        el.fabMenu.classList.add('hidden');
        el.fabMain.classList.remove('active');
        state.uploadQueue = [];
        renderUploadQueue();
        openModal(el.uploadModal);
    });

    el.fabNewFolder.addEventListener('click', () => {
        el.fabMenu.classList.add('hidden');
        el.fabMain.classList.remove('active');
        newItemIsDirectory = true;
        el.newItemTitle.textContent = 'Create New Folder';
        el.newItemName.value = '';
        openModal(el.newItemModal);
    });

    el.fabNewFile.addEventListener('click', () => {
        el.fabMenu.classList.add('hidden');
        el.fabMain.classList.remove('active');
        newItemIsDirectory = false;
        el.newItemTitle.textContent = 'Create New File';
        el.newItemName.value = '';
        openModal(el.newItemModal);
    });

    el.fabCompress.addEventListener('click', () => {
        el.fabMenu.classList.add('hidden');
        el.fabMain.classList.remove('active');
        el.compressName.value = 'archive.zip';
        openModal(el.compressModal);
    });

    // Compress Selection
    el.btnConfirmCompress.addEventListener('click', async () => {
        const zipName = el.compressName.value.trim() || 'archive.zip';
        try {
            await api('/api/archive/compress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sources: [state.currentPath],
                    target_dir: state.currentPath,
                    archive_name: zipName
                })
            });
            closeModal(el.compressModal);
            loadDirectory(state.currentPath);
        } catch (err) {
            alert('Compression failed: ' + err.message);
        }
    });

    // New Item Creation
    el.btnConfirmCreate.addEventListener('click', async () => {
        const name = el.newItemName.value.trim();
        if (!name) return;
        try {
            await api('/api/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_dir: state.currentPath,
                    name: name,
                    is_directory: newItemIsDirectory
                })
            });
            closeModal(el.newItemModal);
            loadDirectory(state.currentPath);
        } catch (err) {
            alert(err.message);
        }
    });

    // Rename Item
    el.btnConfirmRename.addEventListener('click', async () => {
        const newName = el.renameInput.value.trim();
        if (!newName || !state.selectedFileForRename) return;
        try {
            await api('/api/rename', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: state.selectedFileForRename,
                    new_name: newName
                })
            });
            closeModal(el.renameModal);
            loadDirectory(state.currentPath);
        } catch (err) {
            alert(err.message);
        }
    });

    // Save File in Editor
    el.btnSaveFile.addEventListener('click', async () => {
        if (!state.editingFilePath) return;
        try {
            await api('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: state.editingFilePath,
                    content: el.fileEditorText.value
                })
            });
            alert('File saved successfully!');
        } catch (err) {
            alert('Save failed: ' + err.message);
        }
    });

    // Toast Minimize / Close
    el.toastClose.addEventListener('click', () => el.uploadToast.classList.add('hidden'));

    // Upload Modal File Selection & Drag-Drop
    el.dropZone.addEventListener('click', () => el.uploadFileInput.click());
    el.uploadFileInput.addEventListener('change', (e) => {
        addFilesToQueue(Array.from(e.target.files));
    });

    el.dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        el.dropZone.classList.add('drag-over');
    });
    el.dropZone.addEventListener('dragleave', () => el.dropZone.classList.remove('drag-over'));
    el.dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        el.dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files) {
            addFilesToQueue(Array.from(e.dataTransfer.files));
        }
    });

    el.btnStartUpload.addEventListener('click', async () => {
        if (state.uploadQueue.length === 0) return;
        closeModal(el.uploadModal);
        await processUpload(state.uploadQueue);
    });

    // SCREEN-WIDE GLOBAL DRAG & DROP
    window.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (state.currentPath) {
            el.globalDragOverlay.classList.remove('hidden');
        }
    });

    el.globalDragOverlay.addEventListener('dragleave', (e) => {
        e.preventDefault();
        el.globalDragOverlay.classList.add('hidden');
    });

    el.globalDragOverlay.addEventListener('drop', async (e) => {
        e.preventDefault();
        el.globalDragOverlay.classList.add('hidden');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            await processUpload(Array.from(e.dataTransfer.files));
        }
    });

    // Search Execution
    let searchTimeout = null;
    el.searchInput.addEventListener('input', () => {
        const query = el.searchInput.value.trim();
        if (query.length > 0) {
            el.searchClearBtn.classList.remove('hidden');
        } else {
            el.searchClearBtn.classList.add('hidden');
        }

        clearTimeout(searchTimeout);
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => executeSearch(query), 300);
        } else if (query.length === 0 && state.searchActive) {
            exitSearch();
        }
    });

    el.searchClearBtn.addEventListener('click', () => {
        el.searchInput.value = '';
        el.searchClearBtn.classList.add('hidden');
        exitSearch();
    });

    el.btnCloseSearch.addEventListener('click', () => {
        el.searchInput.value = '';
        el.searchClearBtn.classList.add('hidden');
        exitSearch();
    });

    // KEYBOARD SHORTCUTS
    window.addEventListener('keydown', (e) => {
        const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (activeTag === 'input' || activeTag === 'textarea') return;

        const isCtrl = e.ctrlKey || e.metaKey;
        const key = e.key.toLowerCase();

        if (isCtrl && key === 'f') {
            e.preventDefault();
            el.searchInput.focus();
        } else if (isCtrl && key === 'c') {
            if (state.activeHoverPath) {
                e.preventDefault();
                setClipboard('copy', [state.activeHoverPath]);
            }
        } else if (isCtrl && key === 'x') {
            if (state.activeHoverPath) {
                e.preventDefault();
                setClipboard('move', [state.activeHoverPath]);
            }
        } else if (isCtrl && key === 'v') {
            if (state.clipboard.sources.length > 0) {
                e.preventDefault();
                pasteClipboard();
            }
        }
    });
}

// ULTRA-FAST STREAM DESKTOP REFRESHER (~20-25 FPS LOOP)
let isDesktopFetching = false;
function startUltraFastRemoteLoop() {
    if (!state.remotePcLooping || el.remotePcModal.classList.contains('hidden')) return;

    if (isDesktopFetching) {
        setTimeout(startUltraFastRemoteLoop, 30);
        return;
    }

    isDesktopFetching = true;
    const frameUrl = `/api/remote/desktop/frame?quality=35&width=1024&token=${encodeURIComponent(getToken())}&t=${Date.now()}`;
    const img = new Image();
    img.onload = () => {
        el.remoteScreenImg.src = frameUrl;
        isDesktopFetching = false;
        if (state.remotePcLooping && !el.remotePcModal.classList.contains('hidden')) {
            setTimeout(startUltraFastRemoteLoop, 30);
        }
    };
    img.onerror = () => {
        isDesktopFetching = false;
        if (state.remotePcLooping && !el.remotePcModal.classList.contains('hidden')) {
            setTimeout(startUltraFastRemoteLoop, 100);
        }
    };
    img.src = frameUrl;
}

function refreshRemoteScreenFast() {
    isDesktopFetching = false;
    startUltraFastRemoteLoop();
}

function setClipboard(action, sources) {
    state.clipboard = { action, sources };
    const fileName = sources[0].split(/[\/\\]/).pop();
    const actionLabel = action === 'copy' ? 'Copied' : 'Cut';
    
    el.pasteCount.textContent = sources.length;
    el.btnPaste.classList.remove('hidden');
    
    el.statusCount.textContent = `${actionLabel} "${fileName}" to clipboard (Press Ctrl+V or click Paste)`;
}

async function pasteClipboard() {
    if (state.clipboard.sources.length === 0 || !state.currentPath) return;

    const endpoint = state.clipboard.action === 'copy' ? '/api/copy' : '/api/move';
    try {
        await api(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sources: state.clipboard.sources,
                dest_dir: state.currentPath
            })
        });

        const actionText = state.clipboard.action === 'copy' ? 'Copied' : 'Moved';
        alert(`${actionText} items successfully to ${state.currentPath}`);

        if (state.clipboard.action === 'move') {
            state.clipboard = { action: null, sources: [] };
            el.btnPaste.classList.add('hidden');
        }

        loadDirectory(state.currentPath);
    } catch (err) {
        alert('Paste failed: ' + err.message);
    }
}

function openModal(modal) {
    modal.classList.remove('hidden');
}

function closeModal(modal) {
    modal.classList.add('hidden');
    if (modal === el.previewModal) {
        el.previewContainer.innerHTML = '';
    }
    if (modal === el.sysModal && state.sysStatsInterval) {
        clearInterval(state.sysStatsInterval);
        state.sysStatsInterval = null;
    }
    if (modal === el.remotePcModal) {
        state.remotePcLooping = false;
        if (document.fullscreenElement && document.exitFullscreen) {
            document.exitFullscreen().catch(e => {});
        }
    }
}

// Process File Upload
async function processUpload(files) {
    el.uploadToast.classList.remove('hidden');
    el.uploadStatusTitle.textContent = 'Uploading files...';
    el.uploadTotalPct.textContent = '0%';
    el.toastBarFill.style.width = '0%';
    el.toastFileList.innerHTML = '';

    files.forEach(f => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'toast-file-item';
        itemDiv.setAttribute('data-file', f.name);
        itemDiv.innerHTML = `
            <span class="toast-file-name">${f.name}</span>
            <span class="toast-file-status"><i class="fa-solid fa-spinner fa-spin"></i></span>
        `;
        el.toastFileList.appendChild(itemDiv);
    });

    const formData = new FormData();
    formData.append('target_dir', state.currentPath);
    files.forEach(file => formData.append('files', file));

    try {
        let pct = 10;
        const interval = setInterval(() => {
            if (pct < 90) {
                pct += 15;
                el.uploadTotalPct.textContent = `${pct}%`;
                el.toastBarFill.style.width = `${pct}%`;
            }
        }, 150);

        await api('/api/upload', { method: 'POST', body: formData });
        clearInterval(interval);

        el.uploadTotalPct.textContent = '100%';
        el.toastBarFill.style.width = '100%';
        el.uploadStatusTitle.textContent = 'Upload complete';

        files.forEach(f => {
            const itemDiv = el.toastFileList.querySelector(`[data-file="${CSS.escape(f.name)}"]`);
            if (itemDiv) {
                itemDiv.querySelector('.toast-file-status').innerHTML = '<i class="fa-solid fa-circle-check toast-file-icon"></i>';
            }
        });

        setTimeout(() => loadDirectory(state.currentPath), 500);
        setTimeout(() => el.uploadToast.classList.add('hidden'), 4000);

    } catch (err) {
        alert('Upload failed: ' + err.message);
        el.uploadStatusTitle.textContent = 'Upload failed';
    }
}

// Load Drives & Storage
async function loadDrives() {
    try {
        const drives = await api('/api/drives');
        state.drives = drives;
        el.treeNav.innerHTML = '';

        if (drives.length > 0) {
            const primary = drives[0];
            const pct = primary.total ? Math.round((primary.used / primary.total) * 100) : 0;
            const freeGB = primary.free ? (primary.free / (1024 ** 3)).toFixed(1) : 0;
            const totalGB = primary.total ? (primary.total / (1024 ** 3)).toFixed(1) : 0;
            
            el.storagePct.textContent = `${pct}%`;
            el.storageFill.style.width = `${pct}%`;
            el.storageMeta.textContent = `${freeGB} GB free of ${totalGB} GB`;
        }

        drives.forEach(d => {
            const item = document.createElement('div');
            item.className = `tree-item drive-item ${state.currentPath.startsWith(d.path) ? 'active' : ''}`;
            item.innerHTML = `<i class="fa-solid fa-hard-drive"></i> <span>${d.name}</span>`;
            item.addEventListener('click', () => loadDirectory(d.path));
            el.treeNav.appendChild(item);
        });

        try {
            const userShortcuts = await api('/api/shortcuts');
            userShortcuts.forEach(s => {
                const item = document.createElement('div');
                item.className = 'tree-item';
                item.innerHTML = `<i class="fa-solid fa-folder"></i> <span>${s.name}</span>`;
                item.addEventListener('click', () => loadDirectory(s.path));
                el.treeNav.appendChild(item);
            });
        } catch (scErr) {}
    } catch (err) {
        console.error('Failed to load drives:', err);
    }
}

// Load Favorites
async function loadFavorites() {
    try {
        const favs = await api('/api/favorites');
        state.favorites = favs || [];
        renderFavoritesNav();
    } catch (err) {
        console.warn('Could not load favorites:', err);
    }
}

function renderFavoritesNav() {
    el.favoritesNav.innerHTML = '';
    if (state.favorites.length === 0) {
        el.favoritesNav.innerHTML = '<div class="text-muted" style="padding: 6px 12px; font-size: 0.75rem;">No pinned folders</div>';
        return;
    }
    state.favorites.forEach(f => {
        const item = document.createElement('div');
        item.className = `tree-item ${state.currentPath === f.path ? 'active' : ''}`;
        item.innerHTML = `<i class="fa-solid fa-star text-warning"></i> <span>${f.name}</span>`;
        item.addEventListener('click', () => loadDirectory(f.path));
        el.favoritesNav.appendChild(item);
    });

    updateFavPinIcon();
}

async function toggleFavoriteCurrentPath() {
    if (!state.currentPath) return;
    const folderName = state.currentPath.split(/[\/\\]/).filter(Boolean).pop() || state.currentPath;
    const idx = state.favorites.findIndex(f => f.path === state.currentPath);

    if (idx >= 0) {
        state.favorites.splice(idx, 1);
    } else {
        state.favorites.push({ name: folderName, path: state.currentPath });
    }

    renderFavoritesNav();
    try {
        await api('/api/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ favorites: state.favorites })
        });
    } catch (err) {
        console.error('Failed to save favorites:', err);
    }
}

function updateFavPinIcon() {
    const isFav = state.favorites.some(f => f.path === state.currentPath);
    if (isFav) {
        el.btnPinFav.innerHTML = '<i class="fa-solid fa-star"></i>';
        el.btnPinFav.title = 'Unpin Favorite Folder';
    } else {
        el.btnPinFav.innerHTML = '<i class="fa-regular fa-star"></i>';
        el.btnPinFav.title = 'Pin Favorite Folder';
    }
}

// Directory Loading
async function loadDirectory(path) {
    state.searchActive = false;
    el.searchBanner.classList.add('hidden');
    try {
        const data = await api(`/api/files?path=${encodeURIComponent(path)}`);
        state.currentPath = data.current_path;
        state.currentItems = data.items;
        
        updateFavPinIcon();
        renderBreadcrumbs(data.breadcrumbs);
        sortAndRenderContent();
        
        el.statusCount.textContent = `${data.count} items`;
        el.statusPath.textContent = data.current_path;
    } catch (err) {
        alert('Could not load directory: ' + err.message);
    }
}

function navigateUp() {
    if (!state.currentPath) return;
    const parts = state.currentPath.split(/[\/\\]/).filter(Boolean);
    if (parts.length <= 1) {
        if (state.drives.length > 0) loadDirectory(state.drives[0].path);
        return;
    }
    parts.pop();
    const parentPath = parts.join('\\') + (state.currentPath.includes(':') && parts.length === 1 ? '\\' : '');
    loadDirectory(parentPath);
}

// Render Breadcrumbs
function renderBreadcrumbs(crumbs) {
    el.breadcrumbs.innerHTML = '';
    crumbs.forEach((c, idx) => {
        const span = document.createElement('span');
        span.className = `crumb-link ${idx === crumbs.length - 1 ? 'active' : ''}`;
        span.textContent = c.name;
        span.addEventListener('click', () => loadDirectory(c.path));
        el.breadcrumbs.appendChild(span);

        if (idx < crumbs.length - 1) {
            const sep = document.createElement('span');
            sep.textContent = '/';
            sep.style.margin = '0 4px';
            sep.style.color = 'var(--text-light)';
            el.breadcrumbs.appendChild(sep);
        }
    });
}

// Sort & Filter Render
function sortAndRenderContent() {
    let items = [...state.currentItems];

    // Category filter
    if (state.categoryFilter !== 'all') {
        items = items.filter(i => i.is_dir || i.category === state.categoryFilter);
    }

    // Sort
    if (state.sortBy === 'name') {
        items.sort((a, b) => a.name.localeCompare(b.name));
    } else if (state.sortBy === 'size') {
        items.sort((a, b) => b.size - a.size);
    } else if (state.sortBy === 'date') {
        items.sort((a, b) => b.modified - a.modified);
    } else if (state.sortBy === 'type') {
        items.sort((a, b) => (a.category || '').localeCompare(b.category || ''));
    }

    renderContent(items);
}

// Render Folders & Files
function renderContent(items) {
    const folders = items.filter(i => i.is_dir);
    const files = items.filter(i => !i.is_dir);

    el.foldersCount.textContent = folders.length;
    el.filesCount.textContent = files.length;

    // Render Folders Section
    el.foldersGrid.innerHTML = '';
    if (folders.length === 0) {
        el.foldersSection.classList.add('hidden');
    } else {
        el.foldersSection.classList.remove('hidden');
        folders.forEach(folder => {
            const card = document.createElement('div');
            card.className = 'folder-card';
            card.innerHTML = `
                <div class="folder-icon-box"><i class="fa-solid fa-folder"></i></div>
                <div class="folder-details">
                    <span class="folder-name" title="${folder.name}">${folder.name}</span>
                    <span class="folder-meta">Folder</span>
                </div>
                <div class="card-hover-actions">
                    <button class="card-action-btn copy-btn" title="Copy (Ctrl+C)"><i class="fa-solid fa-copy"></i></button>
                    <button class="card-action-btn cut-btn" title="Cut (Ctrl+X)"><i class="fa-solid fa-scissors"></i></button>
                    <button class="card-action-btn rename-btn" title="Rename"><i class="fa-solid fa-pen"></i></button>
                    <button class="card-action-btn btn-del del-btn" title="Delete"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;

            card.addEventListener('mouseenter', () => { state.activeHoverPath = folder.path; });
            card.addEventListener('mouseleave', () => { if (state.activeHoverPath === folder.path) state.activeHoverPath = null; });

            card.addEventListener('click', (e) => {
                if (e.target.closest('.card-action-btn')) return;
                loadDirectory(folder.path);
            });

            card.querySelector('.copy-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                setClipboard('copy', [folder.path]);
            });

            card.querySelector('.cut-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                setClipboard('move', [folder.path]);
            });

            card.querySelector('.rename-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                state.selectedFileForRename = folder.path;
                el.renameInput.value = folder.name;
                openModal(el.renameModal);
            });

            card.querySelector('.del-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Move folder "${folder.name}" to Recycle Bin?`)) {
                    await api('/api/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paths: [folder.path], soft_delete: true }) });
                    loadDirectory(state.currentPath);
                }
            });

            el.foldersGrid.appendChild(card);
        });
    }

    // Render Files Section
    el.filesGrid.innerHTML = '';
    if (files.length === 0) {
        el.filesSection.classList.add('hidden');
    } else {
        el.filesSection.classList.remove('hidden');
        files.forEach(file => {
            const card = document.createElement('div');
            card.className = 'file-card';
            card.setAttribute('data-cat', file.category);

            const downloadUrl = `/api/download?path=${encodeURIComponent(file.path)}&token=${encodeURIComponent(getToken())}`;
            let previewHtml = '';

            if (file.category === 'image') {
                previewHtml = `<img src="${downloadUrl}" alt="${file.name}" loading="lazy">`;
            } else {
                const badgeText = getBadgeTextForCategory(file.category, file.name);
                previewHtml = `<div class="badge-card-icon">${badgeText}</div>`;
            }

            card.innerHTML = `
                <div class="file-preview-wrapper">${previewHtml}</div>
                <div class="file-info">
                    <span class="file-title" title="${file.name}">${file.name}</span>
                    <span class="file-size">${formatBytes(file.size)}</span>
                </div>
                <div class="card-hover-actions">
                    <button class="card-action-btn copy-btn" title="Copy (Ctrl+C)"><i class="fa-solid fa-copy"></i></button>
                    <button class="card-action-btn cut-btn" title="Cut (Ctrl+X)"><i class="fa-solid fa-scissors"></i></button>
                    <button class="card-action-btn download-btn" title="Download"><i class="fa-solid fa-download"></i></button>
                    <button class="card-action-btn rename-btn" title="Rename"><i class="fa-solid fa-pen"></i></button>
                    <button class="card-action-btn btn-del del-btn" title="Delete"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;

            card.addEventListener('mouseenter', () => { state.activeHoverPath = file.path; });
            card.addEventListener('mouseleave', () => { if (state.activeHoverPath === file.path) state.activeHoverPath = null; });

            card.addEventListener('click', (e) => {
                if (e.target.closest('.card-action-btn')) return;
                openFile(file);
            });

            card.querySelector('.copy-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                setClipboard('copy', [file.path]);
            });

            card.querySelector('.cut-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                setClipboard('move', [file.path]);
            });

            card.querySelector('.download-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                window.open(downloadUrl, '_blank');
            });

            card.querySelector('.rename-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                state.selectedFileForRename = file.path;
                el.renameInput.value = file.name;
                openModal(el.renameModal);
            });

            card.querySelector('.del-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Move file "${file.name}" to Recycle Bin?`)) {
                    await api('/api/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paths: [file.path], soft_delete: true }) });
                    loadDirectory(state.currentPath);
                }
            });

            el.filesGrid.appendChild(card);
        });
    }
}

function getBadgeTextForCategory(cat, filename) {
    const ext = filename.split('.').pop().toUpperCase();
    if (cat === 'audio') return 'MP3';
    if (cat === 'document') return ext.length <= 4 ? ext : 'DOC';
    if (cat === 'code') return ext.length <= 4 ? ext : 'CODE';
    if (cat === 'archive') return 'ZIP';
    return ext.length <= 4 ? ext : 'FILE';
}

// Open / Edit / Preview File
async function openFile(item) {
    const downloadUrl = `/api/download?path=${encodeURIComponent(item.path)}&token=${encodeURIComponent(getToken())}`;
    const streamUrl = `/api/stream?path=${encodeURIComponent(item.path)}&token=${encodeURIComponent(getToken())}`;
    const pdfUrl = `/api/pdf/render?path=${encodeURIComponent(item.path)}&token=${encodeURIComponent(getToken())}`;

    if (item.category === 'image') {
        state.galleryImages = state.currentItems.filter(i => !i.is_dir && i.category === 'image');
        state.galleryIndex = state.galleryImages.findIndex(i => i.path === item.path);
        showLightboxImage();
        openModal(el.lightboxModal);

    } else if (item.category === 'video') {
        el.previewTitle.textContent = item.name;
        el.previewContainer.innerHTML = `<video controls autoplay style="width:100%; max-height:70vh;" src="${streamUrl}"></video>`;
        openModal(el.previewModal);

    } else if (item.category === 'audio') {
        el.previewTitle.textContent = item.name;
        el.previewContainer.innerHTML = `<div style="padding:20px; width:100%; text-align:center;"><i class="fa-solid fa-music fa-3x text-primary" style="margin-bottom:15px;"></i><h4>${item.name}</h4><audio controls autoplay style="width:100%; margin-top:15px;" src="${streamUrl}"></audio></div>`;
        openModal(el.previewModal);

    } else if (item.name.toLowerCase().endsWith('.pdf')) {
        el.previewTitle.textContent = item.name;
        el.previewContainer.innerHTML = `<iframe src="${pdfUrl}" style="width:100%; height:75vh; border:none;"></iframe>`;
        openModal(el.previewModal);

    } else if (item.category === 'code' || item.name.endsWith('.txt') || item.name.endsWith('.log')) {
        try {
            const data = await api(`/api/read?path=${encodeURIComponent(item.path)}`);
            state.editingFilePath = item.path;
            el.editorTitle.innerHTML = `<i class="fa-solid fa-code"></i> ${item.name}`;
            el.fileEditorText.value = data.content;
            openModal(el.editorModal);
        } catch (err) {
            alert('Cannot read text file: ' + err.message);
        }

    } else if (item.category === 'archive') {
        if (confirm(`Extract archive "${item.name}" into current directory?`)) {
            try {
                await api('/api/archive/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        archive_path: item.path,
                        dest_dir: state.currentPath
                    })
                });
                alert('Archive extracted successfully!');
                loadDirectory(state.currentPath);
            } catch (err) {
                alert('Extraction failed: ' + err.message);
            }
        }
    } else {
        window.open(downloadUrl, '_blank');
    }
}

// Lightbox Gallery Navigation
function showLightboxImage() {
    if (state.galleryImages.length === 0) return;
    const imgItem = state.galleryImages[state.galleryIndex];
    el.lightboxImg.src = `/api/download?path=${encodeURIComponent(imgItem.path)}&token=${encodeURIComponent(getToken())}`;
    el.lightboxCaption.textContent = `${imgItem.name} (${state.galleryIndex + 1} / ${state.galleryImages.length})`;
}

function navigateLightbox(direction) {
    if (state.galleryImages.length === 0) return;
    state.galleryIndex = (state.galleryIndex + direction + state.galleryImages.length) % state.galleryImages.length;
    showLightboxImage();
}

// System Stats Refresher
async function refreshSystemStats() {
    try {
        const stats = await api('/api/system/stats');
        el.sysCpuVal.textContent = `${stats.cpu_percent.toFixed(1)}%`;
        el.sysCpuBar.style.width = `${stats.cpu_percent}%`;

        const memUsed = (stats.memory_used / (1024 ** 3)).toFixed(1);
        const memTotal = (stats.memory_total / (1024 ** 3)).toFixed(1);
        el.sysMemVal.textContent = `${memUsed} / ${memTotal} GB`;
        el.sysMemBar.style.width = `${stats.memory_percent}%`;

        const hours = Math.floor(stats.uptime_seconds / 3600);
        const mins = Math.floor((stats.uptime_seconds % 3600) / 60);
        el.sysUptimeVal.textContent = `${hours}h ${mins}m`;
        el.sysHostVal.textContent = `Host: ${stats.hostname} (${stats.platform})`;
    } catch (err) {
        console.error('Failed to update system stats:', err);
    }
}

// Web Terminal Helper
function appendTerminalLine(text, type = 'out') {
    const div = document.createElement('div');
    div.className = `term-line ${type}`;
    div.textContent = text;
    el.terminalOutput.appendChild(div);
    el.terminalOutput.scrollTop = el.terminalOutput.scrollHeight;
}

// Storage Analyzer Render
function renderStorageAnalysis(data) {
    let html = `<h4 style="margin-bottom:10px;"><i class="fa-solid fa-folder"></i> Total Directory Size: ${formatBytes(data.total_size)}</h4>`;

    if (data.subfolders && data.subfolders.length > 0) {
        html += '<h5 style="margin-top:15px; margin-bottom:8px;">Largest Subfolders:</h5>';
        data.subfolders.forEach(sub => {
            const pct = data.total_size ? Math.round((sub.size / data.total_size) * 100) : 0;
            html += `
                <div class="storage-item-row">
                    <div class="storage-item-meta"><span>📁 ${sub.name}</span><span>${formatBytes(sub.size)} (${pct}%)</span></div>
                    <div class="storage-item-bar"><div class="storage-item-fill" style="width:${pct}%"></div></div>
                </div>
            `;
        });
    }

    if (data.top_files && data.top_files.length > 0) {
        html += '<h5 style="margin-top:15px; margin-bottom:8px;">Largest Files:</h5>';
        data.top_files.forEach(f => {
            html += `<div class="storage-item-meta" style="padding:4px 0;"><span>📄 ${f.name}</span><span>${formatBytes(f.size)}</span></div>`;
        });
    }

    el.storageAnalyzerContent.innerHTML = html;
}

// Search Execution
async function executeSearch(query) {
    try {
        const endpoint = state.searchMode === 'fulltext'
            ? `/api/search/fulltext?root=${encodeURIComponent(state.currentPath)}&q=${encodeURIComponent(query)}`
            : `/api/search?root=${encodeURIComponent(state.currentPath)}&q=${encodeURIComponent(query)}`;

        const res = await api(endpoint);
        state.searchActive = true;
        el.searchQueryText.textContent = query;
        el.searchCountText.textContent = (res.results || []).length;
        el.searchBanner.classList.remove('hidden');

        if (state.searchMode === 'fulltext') {
            const fulltextItems = (res.results || []).map(r => ({
                name: `${r.file_name} (Line ${r.line_number}: "${r.snippet}")`,
                path: r.file_path,
                is_dir: false,
                size: 0,
                category: 'code'
            }));
            renderContent(fulltextItems);
        } else {
            const searchItems = (res.results || []).map(r => ({
                name: r.name,
                path: r.path,
                is_dir: r.is_dir,
                size: r.size,
                category: r.is_dir ? 'folder' : 'file'
            }));
            renderContent(searchItems);
        }
    } catch (err) {
        console.error('Search failed:', err);
    }
}

function exitSearch() {
    state.searchActive = false;
    el.searchBanner.classList.add('hidden');
    loadDirectory(state.currentPath);
}

// Upload Queue Handling
function addFilesToQueue(files) {
    files.forEach(f => state.uploadQueue.push(f));
    renderUploadQueue();
}

function renderUploadQueue() {
    el.uploadFileList.innerHTML = '';
    state.uploadQueue.forEach((f, idx) => {
        const div = document.createElement('div');
        div.className = 'queue-item';
        div.innerHTML = `<span>${f.name} (${formatBytes(f.size)})</span><i class="fa-solid fa-xmark remove-queue" style="cursor:pointer;" data-idx="${idx}"></i>`;
        div.querySelector('.remove-queue').addEventListener('click', () => {
            state.uploadQueue.splice(idx, 1);
            renderUploadQueue();
        });
        el.uploadFileList.appendChild(div);
    });
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
