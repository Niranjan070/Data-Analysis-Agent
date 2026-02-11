/**
 * Data Analysis Agent — Frontend Application
 * Handles file uploads, API interactions, and dynamic UI updates
 */

// ========== State ==========
const state = {
    datasetLoaded: false,
    datasetName: '',
    isAnalyzing: false,
    resultsCount: 0,
};

// ========== DOM Elements ==========
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ========== Initialization ==========
document.addEventListener('DOMContentLoaded', () => {
    loadSampleDatasets();
    setupUpload();
    setupToolCards();
    setupButtons();
});

// ========== Sample Datasets ==========
async function loadSampleDatasets() {
    try {
        const res = await fetch('/api/sample-datasets');
        const data = await res.json();
        const list = $('#sample-list');
        list.innerHTML = '';

        data.datasets.forEach(ds => {
            const item = document.createElement('div');
            item.className = 'sample-item';
            item.innerHTML = `
                <div class="sample-info">
                    <h4>${ds.name}</h4>
                    <p>${ds.rows} rows × ${ds.columns} columns</p>
                </div>
                <span class="sample-arrow">→</span>
            `;
            item.addEventListener('click', () => loadSample(ds.filename));
            list.appendChild(item);
        });
    } catch (err) {
        console.error('Failed to load samples:', err);
        $('#sample-list').innerHTML = '<p class="sample-loading">Could not load samples</p>';
    }
}

async function loadSample(filename) {
    showUploadLoading();
    try {
        const formData = new FormData();
        formData.append('filename', filename);
        const res = await fetch('/api/load-sample', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.success) {
            onDatasetLoaded(data);
        } else {
            alert('Failed to load sample dataset');
        }
    } catch (err) {
        console.error('Sample load error:', err);
        alert('Error loading sample: ' + err.message);
    } finally {
        hideUploadLoading();
    }
}

// ========== File Upload ==========
function setupUpload() {
    const dropZone = $('#drop-zone');
    const fileInput = $('#file-input');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileUpload(files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
    });
}

async function handleFileUpload(file) {
    showUploadLoading();
    try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/upload', { method: 'POST', body: formData });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        if (data.success) {
            onDatasetLoaded(data);
        }
    } catch (err) {
        console.error('Upload error:', err);
        alert('Upload failed: ' + err.message);
    } finally {
        hideUploadLoading();
    }
}

// ========== Dataset Loaded ==========
function onDatasetLoaded(data) {
    state.datasetLoaded = true;
    state.datasetName = data.dataset_name;

    // Update title
    $('#dataset-title').textContent = `📊 ${data.dataset_name}`;

    // Update badges
    const badges = $('#dataset-badges');
    badges.innerHTML = `
        <span class="badge badge-purple">${data.shape.rows} rows</span>
        <span class="badge badge-cyan">${data.shape.cols} columns</span>
        <span class="badge badge-yellow">${Object.values(data.dtypes).filter(t => t.includes('int') || t.includes('float')).length} numeric</span>
        <span class="badge">${Object.values(data.dtypes).filter(t => t === 'object').length} categorical</span>
    `;

    // Update compression card
    if (data.compression) {
        const comp = data.compression;
        const ratio = comp.compression_ratio || 1;
        $('#compression-ratio').textContent = `${ratio}x`;

        const maxTokens = Math.max(comp.full_tokens || 1, comp.compressed_tokens || 1);
        const origPct = ((comp.full_tokens || 0) / maxTokens * 100);
        const compPct = ((comp.compressed_tokens || 0) / maxTokens * 100);

        $('#comp-bar-original').style.width = origPct + '%';
        $('#comp-bar-compressed').style.width = compPct + '%';
        $('#comp-tokens-original').textContent = `${comp.full_tokens || 0} tokens`;
        $('#comp-tokens-compressed').textContent = `${comp.compressed_tokens || 0} tokens`;
        $('#compression-savings').textContent =
            `💡 Schema compression saves ${comp.savings_pct || 0}% of tokens — ${comp.full_tokens - comp.compressed_tokens} tokens saved per LLM call!`;

        updateHeaderStats(comp.full_tokens - comp.compressed_tokens, comp.savings_pct);
    }

    // Update schema preview
    if (data.schema_compact) {
        $('#schema-code').textContent = data.schema_compact;
    }

    // Update data preview table
    if (data.preview && data.preview.length > 0) {
        const columns = Object.keys(data.preview[0]);
        const thead = $('#preview-thead');
        const tbody = $('#preview-tbody');

        thead.innerHTML = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';
        tbody.innerHTML = data.preview.map(row =>
            '<tr>' + columns.map(c => `<td>${row[c] ?? '—'}</td>`).join('') + '</tr>'
        ).join('');
    }

    // Show sections
    $('#upload-section').style.display = 'none';
    $('#dataset-section').style.display = 'block';
    $('#analysis-section').style.display = 'block';
    $('#results-section').style.display = 'block';

    // Scroll to dataset info
    $('#dataset-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ========== Analysis Tools ==========
function setupToolCards() {
    $$('.tool-card').forEach(card => {
        card.addEventListener('click', () => {
            const tool = card.dataset.tool;
            if (tool) runAnalysis(tool);
        });
    });
}

function setupButtons() {
    // Auto EDA
    $('#btn-auto-eda').addEventListener('click', runAutoEDA);

    // Custom query
    $('#btn-custom-query').addEventListener('click', () => {
        const query = $('#custom-query').value.trim();
        if (query) runAnalysis('custom', query);
    });

    $('#custom-query').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) runAnalysis('custom', query);
        }
    });

    // Change dataset
    $('#btn-change-dataset').addEventListener('click', () => {
        $('#upload-section').style.display = 'block';
        $('#dataset-section').style.display = 'none';
        $('#analysis-section').style.display = 'none';
        $('#results-section').style.display = 'none';
    });

    // Schema toggle
    $('#btn-toggle-schema').addEventListener('click', () => {
        const code = $('#schema-code');
        code.classList.toggle('expanded');
        const btn = $('#btn-toggle-schema');
        btn.textContent = code.classList.contains('expanded') ? 'Collapse' : 'Expand';
    });

    // Clear results
    $('#btn-clear-results').addEventListener('click', () => {
        $('#results-list').innerHTML = '';
        state.resultsCount = 0;
    });

    // Show context modal
    $('#btn-show-context').addEventListener('click', showContextModal);

    // Close modal
    $('#btn-close-modal').addEventListener('click', () => {
        $('#context-modal').style.display = 'none';
    });
    $('#modal-overlay').addEventListener('click', () => {
        $('#context-modal').style.display = 'none';
    });
}

// ========== Run Analysis ==========
async function runAnalysis(tool, query = '') {
    if (state.isAnalyzing) return;
    state.isAnalyzing = true;

    showAnalysisLoading(`Running ${tool} analysis...`);

    try {
        const formData = new FormData();
        formData.append('tool', tool);
        if (query) formData.append('query', query);

        const res = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.result) {
            addResultCard(data.result);
        }
        if (data.token_stats) {
            updateTokenDashboard(data.token_stats);
        }
    } catch (err) {
        console.error('Analysis error:', err);
        addResultCard({
            tool: tool,
            success: false,
            error: err.message,
            stdout: '',
            chart_path: null,
            code: '',
            tokens_used: 0,
        });
    } finally {
        state.isAnalyzing = false;
        hideAnalysisLoading();
    }
}

async function runAutoEDA() {
    if (state.isAnalyzing) return;
    state.isAnalyzing = true;

    showAnalysisLoading('Running full automated EDA pipeline...');
    $('#btn-auto-eda').disabled = true;

    try {
        const res = await fetch('/api/auto-eda', { method: 'POST' });
        const data = await res.json();

        if (data.results) {
            // Clear previous results
            $('#results-list').innerHTML = '';
            state.resultsCount = 0;

            // Add each result with staggered animation
            data.results.forEach((result, i) => {
                setTimeout(() => addResultCard(result), i * 200);
            });
        }

        if (data.token_stats) {
            updateTokenDashboard(data.token_stats);
        }

        // Scroll to results
        setTimeout(() => {
            $('#results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    } catch (err) {
        console.error('Auto EDA error:', err);
        alert('Auto EDA failed: ' + err.message);
    } finally {
        state.isAnalyzing = false;
        hideAnalysisLoading();
        $('#btn-auto-eda').disabled = false;
    }
}

// ========== Result Cards ==========
function addResultCard(result) {
    state.resultsCount++;
    const toolNames = {
        overview: '📊 Dataset Overview',
        describe: '📈 Statistical Summary',
        correlations: '🔗 Correlation Analysis',
        distributions: '📉 Distribution Analysis',
        value_counts: '🏷️ Categorical Analysis',
        missing_analysis: '🕳️ Missing Value Analysis',
        outliers: '⚡ Outlier Detection',
        pairplot: '🔄 Pair Plot',
        time_analysis: '⏰ Time Analysis',
        custom: '🔍 Custom Analysis',
    };

    const card = document.createElement('div');
    card.className = 'result-card expanded';

    const statusClass = result.success ? 'success' : 'error';
    const statusText = result.success ? '✓ Success' : '✗ Error';

    card.innerHTML = `
        <div class="result-card-header" onclick="this.parentElement.classList.toggle('expanded')">
            <div class="result-card-title">
                <h4>${toolNames[result.tool] || result.tool}</h4>
                <span class="result-status ${statusClass}">${statusText}</span>
            </div>
            <div class="result-meta">
                <span class="result-tokens">${result.tokens_used || 0} tokens</span>
                <span class="result-collapse-icon">▼</span>
            </div>
        </div>
        <div class="result-card-body">
            ${result.stdout ? `<pre class="result-output">${escapeHtml(result.stdout)}</pre>` : ''}
            ${result.result_value ? `<pre class="result-output">${escapeHtml(result.result_value)}</pre>` : ''}
            ${result.error ? `<pre class="result-output" style="color: var(--accent-red);">${escapeHtml(result.error)}</pre>` : ''}
            ${result.chart_path ? `
                <div class="result-chart">
                    <img src="${result.chart_path}" alt="Chart" loading="lazy">
                </div>
            ` : ''}
            ${result.code ? `
                <div class="result-code-toggle">
                    <button class="btn btn-ghost btn-sm" onclick="toggleCode(this)">Show Code</button>
                    <pre class="result-code">${escapeHtml(result.code)}</pre>
                </div>
            ` : ''}
        </div>
    `;

    $('#results-list').prepend(card);
}

function toggleCode(btn) {
    const code = btn.nextElementSibling;
    code.classList.toggle('visible');
    btn.textContent = code.classList.contains('visible') ? 'Hide Code' : 'Show Code';
}

// ========== Token Dashboard ==========
function updateTokenDashboard(stats) {
    if (stats.schema_compression) {
        $('#td-schema-savings').textContent = `${stats.schema_compression.savings_pct || 0}%`;
    }
    if (stats.history_compression) {
        $('#td-history-savings').textContent = `${stats.history_compression.savings_pct || 0}%`;
    }
    if (stats.scaledown_api) {
        $('#td-total-saved').textContent = formatNumber(stats.scaledown_api.total_tokens_saved || 0);
    }
    $('#td-steps').textContent = stats.total_analysis_steps || 0;

    // Update header stats
    const totalSaved = (stats.scaledown_api?.total_tokens_saved || 0) +
        (stats.schema_compression?.full_tokens - stats.schema_compression?.compressed_tokens || 0);
    const avgCompression = stats.schema_compression?.savings_pct || 0;
    updateHeaderStats(totalSaved, avgCompression);
}

function updateHeaderStats(tokensSaved, compressionPct) {
    $('#header-tokens-saved').textContent = formatNumber(tokensSaved);
    $('#header-compression').textContent = `${Math.round(compressionPct)}%`;
}

// ========== Context Modal ==========
async function showContextModal() {
    try {
        const res = await fetch('/api/compressed-context');
        const data = await res.json();

        $('#modal-context-code').textContent = data.context || 'No context available';
        $('#modal-stats').innerHTML = `
            <div class="modal-stat">📝 ${data.token_estimate || 0} estimated tokens</div>
            <div class="modal-stat">📦 Compressed context ready for LLM</div>
        `;

        $('#context-modal').style.display = 'flex';
    } catch (err) {
        console.error('Context modal error:', err);
    }
}

// ========== Loading States ==========
function showUploadLoading() {
    $('#upload-loading').style.display = 'flex';
}

function hideUploadLoading() {
    $('#upload-loading').style.display = 'none';
}

function showAnalysisLoading(text) {
    $('#analysis-loading-text').textContent = text;
    $('#analysis-loading').style.display = 'flex';
}

function hideAnalysisLoading() {
    $('#analysis-loading').style.display = 'none';
}

// ========== Utilities ==========
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return String(num);
}
