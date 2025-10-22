/**
 * UI Manager for GPU Tycoon
 * Handles all DOM updates and rendering
 */

class UIManager {
    constructor() {
        this.lastJobCount = 0;
        this.lastCompletedCount = 0;
        this.catalog = null;
        this.jobCards = new Map(); // Track job cards by ID to avoid recreation
        this.gpuBars = new Map(); // Track GPU bars by ID
        this.lastShopState = null; // Track last shop state to avoid unnecessary re-renders
        this.currentShopTab = 'gpus'; // Track active shop tab
    }
    
    /**
     * Initialize shop tabs
     */
    initShopTabs() {
        const tabs = document.querySelectorAll('.shop-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchShopTab(tabName);
            });
        });
    }
    
    /**
     * Switch to a different shop tab
     */
    switchShopTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.shop-tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update visible content
        document.querySelectorAll('.shop-tab-content').forEach(content => {
            if (content.id === `shop-tab-${tabName}`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
        
        this.currentShopTab = tabName;
    }
    
    /**
     * Load item catalog from server
     */
    async loadCatalog() {
        try {
            const response = await fetch('/api/catalog');
            this.catalog = await response.json();
        } catch (e) {
            console.error('Failed to load catalog:', e);
        }
    }
    
    /**
     * Update all UI elements with new game state
     */
    update(state) {
        this.updateCapacity(state);
        this.updateMetrics(state);
        this.updateJobs(state);
        this.updateGPUs(state);
        this.updateShop(state);
        this.updateSystemInfo(state);
        this.updatePhaseIndicator(state);
        this.updateAutoAssignToggle(state);
        this.checkAchievements(state);
    }
    
    /**
     * Update capacity bar
     */
    updateCapacity(state) {
        if (!state.capacity) return;
        
        const { total, reserved, available } = state.capacity;
        const reservedPct = total > 0 ? (reserved / total) * 100 : 0;
        const availablePct = total > 0 ? (available / total) * 100 : 100;
        
        document.getElementById('capacity-text').textContent = 
            `${available} Available / ${reserved} Reserved / ${total} Total GPUs`;
        
        document.getElementById('capacity-bar-available').style.width = `${availablePct}%`;
        document.getElementById('capacity-bar-reserved').style.width = `${reservedPct}%`;
    }
    
    /**
     * Update metrics panel
     */
    updateMetrics(state) {
        document.getElementById('cash-display').textContent = this.formatCurrency(state.cash);
        document.getElementById('revenue-rate').textContent = this.formatCurrency(state.stats.revenue_per_hour) + '/hr';
        document.getElementById('gpu-count').textContent = state.stats.total_gpus;
        document.getElementById('utilization').textContent = state.stats.utilization.toFixed(1) + '%';
        document.getElementById('sla-compliance').textContent = state.stats.sla_compliance.toFixed(1) + '%';
        document.getElementById('pue').textContent = state.pue.toFixed(2);
    }
    
    /**
     * Update job queue and active jobs
     */
    updateJobs(state) {
        // Update counts
        document.getElementById('queue-count').textContent = `(${state.job_queue.length})`;
        document.getElementById('active-count').textContent = `(${state.active_jobs.length})`;
        
        // Update job queue (incremental)
        this.updateJobContainer('job-queue', state.job_queue, false, state.auto_assign);
        
        // Update active jobs (incremental with progress updates)
        this.updateJobContainer('active-jobs', state.active_jobs, true, state.auto_assign);
        
        // Check for completed jobs (play sound)
        if (state.stats.jobs_completed > this.lastCompletedCount) {
            audioManager.jobComplete();
            this.lastCompletedCount = state.stats.jobs_completed;
        }
    }
    
    /**
     * Update a job container incrementally to avoid flickering
     */
    updateJobContainer(containerId, jobs, showProgress, autoAssign = true) {
        const container = document.getElementById(containerId);
        
        // Handle empty state
        if (jobs.length === 0) {
            const emptyMsg = '<div class="empty-msg" style="color: #666; text-align: center; padding: 20px;">No jobs ' + 
                           (containerId === 'job-queue' ? 'waiting' : 'active') + '</div>';
            if (container.innerHTML !== emptyMsg) {
                container.innerHTML = emptyMsg;
                // Clear tracked cards for this container
                for (let [key, card] of this.jobCards.entries()) {
                    if (card.container === containerId) {
                        this.jobCards.delete(key);
                    }
                }
            }
            return;
        }
        
        // Remove empty message if it exists
        const emptyMsg = container.querySelector('.empty-msg');
        if (emptyMsg) {
            emptyMsg.remove();
        }
        
        // For job queue (not active jobs), group similar jobs
        if (containerId === 'job-queue') {
            this.updateGroupedJobQueue(container, jobs, autoAssign);
        } else {
            // Active jobs are shown individually with progress
            this.updateActiveJobsList(container, jobs);
        }
    }
    
    /**
     * Update job queue with grouped jobs
     */
    updateGroupedJobQueue(container, jobs, autoAssign = true) {
        // Group jobs by their characteristics
        const jobGroups = new Map();
        
        jobs.forEach(job => {
            const groupKey = `${job.type}-${job.size}-${job.gpu_count}-${job.vram_per_gpu}-${job.base_payout}`;
            if (!jobGroups.has(groupKey)) {
                jobGroups.set(groupKey, []);
            }
            jobGroups.get(groupKey).push(job);
        });
        
        // Create a set of current group keys
        const currentGroupKeys = new Set(jobGroups.keys());
        
        // Remove cards for groups that no longer exist
        for (let [key, cardInfo] of this.jobCards.entries()) {
            if (cardInfo.container === 'job-queue' && !currentGroupKeys.has(cardInfo.groupKey)) {
                cardInfo.element.remove();
                this.jobCards.delete(key);
            }
        }
        
        // Update or create cards for current groups
        jobGroups.forEach((groupJobs, groupKey) => {
            const key = `job-queue-${groupKey}`;
            let cardInfo = this.jobCards.get(key);
            
            // Use the first (oldest) job as the representative
            const representativeJob = groupJobs[0];
            const count = groupJobs.length;
            
            if (!cardInfo) {
                // Create new card
                const card = this.createJobCard(representativeJob, false, count, groupJobs.map(j => j.id), autoAssign);
                container.appendChild(card);
                this.jobCards.set(key, {
                    element: card,
                    container: 'job-queue',
                    groupKey: groupKey,
                    jobIds: groupJobs.map(j => j.id)
                });
            } else {
                // Update count badge if changed
                const countBadge = cardInfo.element.querySelector('.job-count-badge');
                if (countBadge && count > 1) {
                    countBadge.textContent = `×${count}`;
                } else if (countBadge && count === 1) {
                    countBadge.style.display = 'none';
                } else if (!countBadge && count > 1) {
                    // Add count badge if it doesn't exist
                    const header = cardInfo.element.querySelector('.job-header');
                    const badge = document.createElement('span');
                    badge.className = 'job-count-badge';
                    badge.textContent = `×${count}`;
                    header.appendChild(badge);
                }
                
                // Update job IDs in card info
                cardInfo.jobIds = groupJobs.map(j => j.id);
                
                // Update data attribute
                const assignBtn = cardInfo.element.querySelector('.job-assign-btn');
                if (assignBtn) {
                    assignBtn.dataset.jobIds = JSON.stringify(groupJobs.map(j => j.id));
                }
            }
        });
    }
    
    /**
     * Update active jobs list (individual cards with progress)
     */
    updateActiveJobsList(container, jobs) {
        // Create a set of current job IDs
        const currentJobIds = new Set(jobs.map(j => j.id));
        
        // Remove cards for jobs that no longer exist
        for (let [key, cardInfo] of this.jobCards.entries()) {
            if (cardInfo.container === 'active-jobs' && !currentJobIds.has(cardInfo.jobId)) {
                cardInfo.element.remove();
                this.jobCards.delete(key);
            }
        }
        
        // Update or create cards for current jobs
        jobs.forEach((job, index) => {
            const key = `active-jobs-${job.id}`;
            let cardInfo = this.jobCards.get(key);
            
            if (!cardInfo) {
                // Create new card
                const card = this.createJobCard(job, true);
                container.appendChild(card);
                this.jobCards.set(key, {
                    element: card,
                    container: 'active-jobs',
                    jobId: job.id
                });
            } else {
                // Update progress bar for active jobs
                const progressFill = cardInfo.element.querySelector('.job-progress-fill');
                if (progressFill) {
                    progressFill.style.width = `${(job.progress * 100).toFixed(1)}%`;
                }
                
                // Update SLA status if changed
                if (job.sla_missed && !cardInfo.element.classList.contains('sla-missed')) {
                    cardInfo.element.classList.add('sla-missed');
                    const details = cardInfo.element.querySelector('.job-details');
                    if (details && !details.textContent.includes('SLA MISSED')) {
                        details.innerHTML += ' | ⚠️ SLA MISSED';
                    }
                }
            }
        });
    }
    
    /**
     * Create a job card element
     */
    createJobCard(job, showProgress = false, count = 1, jobIds = null, showAssignBtn = true) {
        const card = document.createElement('div');
        card.className = `job-card ${job.type}`;
        if (job.sla_missed) card.classList.add('sla-missed');
        
        // If jobIds is provided, use it; otherwise use single job id
        const dataJobIds = jobIds || [job.id];
        
        card.innerHTML = `
            <div class="job-header">
                <span class="job-type">${job.type.charAt(0).toUpperCase() + job.type.slice(1)}</span>
                <span class="job-size">${job.size} (${job.gpu_count} GPU${job.gpu_count > 1 ? 's' : ''})</span>
                ${count > 1 ? `<span class="job-count-badge">×${count}</span>` : ''}
            </div>
            <div class="job-customer">
                <strong>${job.customer_name || 'Unknown Client'}</strong>
                <div class="job-task">${job.task_description || 'Processing'}</div>
            </div>
            <div class="job-details">
                💰 $${job.base_payout} | 🎮 ${job.vram_per_gpu}GB VRAM
                ${job.sla_missed ? ' | ⚠️ SLA MISSED' : ''}
            </div>
            ${showProgress ? `
                <div class="job-progress-bar">
                    <div class="job-progress-fill" style="width: ${job.progress * 100}%"></div>
                </div>
            ` : (showAssignBtn ? `
                <button class="job-assign-btn" data-job-ids='${JSON.stringify(dataJobIds)}'>
                    ⚡ Assign to GPUs
                </button>
            ` : '')}
        `;
        
        return card;
    }
    
    /**
     * Update GPU rack visualization (incremental to avoid flickering)
     */
    updateGPUs(state) {
        const rackContainer = document.getElementById('gpu-rack');
        
        // Handle empty state
        if (state.gpus.length === 0) {
            const emptyMsg = '<div class="empty-msg" style="color: #666; text-align: center; padding: 20px;">No GPUs installed</div>';
            if (rackContainer.innerHTML !== emptyMsg) {
                rackContainer.innerHTML = emptyMsg;
                this.gpuBars.clear();
            }
            return;
        }
        
        // Remove empty message if it exists
        const emptyMsg = rackContainer.querySelector('.empty-msg');
        if (emptyMsg) {
            emptyMsg.remove();
        }
        
        // Create a set of current GPU IDs
        const currentGpuIds = new Set(state.gpus.map(g => g.id));
        
        // Remove bars for GPUs that no longer exist
        for (let [gpuId, barInfo] of this.gpuBars.entries()) {
            if (!currentGpuIds.has(gpuId)) {
                barInfo.element.remove();
                this.gpuBars.delete(gpuId);
            }
        }
        
        // Update or create bars for current GPUs
        state.gpus.forEach(gpu => {
            let barInfo = this.gpuBars.get(gpu.id);
            
            if (!barInfo) {
                // Create new GPU bar
                const bar = this.createGPUBar(gpu);
                rackContainer.appendChild(bar);
                this.gpuBars.set(gpu.id, { element: bar });
            } else {
                // Update existing bar
                this.updateGPUBar(barInfo.element, gpu);
            }
        });
    }
    
    /**
     * Create a GPU utilization bar
     */
    createGPUBar(gpu) {
        const bar = document.createElement('div');
        bar.className = 'gpu-bar';
        bar.dataset.gpuId = gpu.id;
        
        const utilPercent = (gpu.utilization * 100).toFixed(0);
        
        bar.innerHTML = `
            <div class="gpu-header">
                <span class="gpu-name">${gpu.name} #${gpu.id}</span>
                <span class="gpu-vram">${gpu.vram_used}/${gpu.vram} GB VRAM</span>
            </div>
            <div class="gpu-utilization-bar">
                <div class="gpu-utilization-fill ${utilPercent > 80 ? 'high' : ''}" 
                     style="width: ${utilPercent}%"></div>
                <div class="gpu-utilization-text">${utilPercent}%</div>
            </div>
        `;
        
        return bar;
    }
    
    /**
     * Update an existing GPU bar (avoid recreating DOM)
     */
    updateGPUBar(barElement, gpu) {
        const utilPercent = (gpu.utilization * 100).toFixed(0);
        
        // Update VRAM display
        const vramSpan = barElement.querySelector('.gpu-vram');
        if (vramSpan) {
            vramSpan.textContent = `${gpu.vram_used}/${gpu.vram} GB VRAM`;
        }
        
        // Update utilization bar
        const fillElement = barElement.querySelector('.gpu-utilization-fill');
        const textElement = barElement.querySelector('.gpu-utilization-text');
        
        if (fillElement) {
            fillElement.style.width = `${utilPercent}%`;
            
            // Update high utilization class
            if (utilPercent > 80 && !fillElement.classList.contains('high')) {
                fillElement.classList.add('high');
            } else if (utilPercent <= 80 && fillElement.classList.contains('high')) {
                fillElement.classList.remove('high');
            }
        }
        
        if (textElement) {
            textElement.textContent = `${utilPercent}%`;
        }
    }
    
    /**
     * Update shop items (only when state changes)
     */
    updateShop(state) {
        if (!this.catalog) return;
        
        // Create a hash of relevant shop state to detect changes
        const shopStateHash = JSON.stringify({
            cash: Math.floor(state.cash),
            cooling: state.cooling_tier,
            network: state.network_tier,
            revenue: Math.floor(state.total_revenue / 1000), // Round to nearest 1000
            gpuCount: state.gpus.length,
            contracts: state.contracts ? JSON.stringify(state.contracts) : '',
            marketing: state.marketing ? JSON.stringify(state.marketing.purchased) : ''
        });
        
        // Only re-render if state has changed
        if (this.lastShopState !== shopStateHash) {
            this.renderGPUShop(state);
            this.renderMarketingShop(state);
            this.renderContractsShop(state);
            this.lastShopState = shopStateHash;
        }
    }
    
    renderGPUShop(state) {
        const container = document.getElementById('gpu-shop');
        container.innerHTML = '';
        
        // Sort by price ascending (cheapest first)
        const sortedGPUs = Object.entries(this.catalog.gpus).sort((a, b) => a[1].cost - b[1].cost);
        
        sortedGPUs.forEach(([gpuType, spec]) => {
            const unlocked = state.unlocks.gpus.includes(gpuType);
            const canAfford = state.cash >= spec.cost;
            
            // Check if cooling is bundled (cooling_tier field exists)
            const coolingNote = spec.cooling_tier && spec.cooling_tier !== 'air' 
                ? `<div class="shop-item-note">❄️ Includes ${this.getCoolingName(spec.cooling_tier)}</div>` 
                : '';
            
            const item = document.createElement('div');
            item.className = 'shop-item';
            
            item.innerHTML = `
                <div class="shop-item-header">
                    <span class="shop-item-name">${spec.name}</span>
                    <span class="shop-item-cost">$${this.formatNumber(spec.cost)}</span>
                </div>
                <div class="shop-item-specs">
                    ${spec.vram}GB VRAM | ${spec.tdp}W TDP | ${spec.performance}x perf
                </div>
                ${coolingNote}
                ${spec.description ? `<div class="shop-item-description">${spec.description}</div>` : ''}
                <button class="shop-btn" 
                        data-action="buy_gpu" 
                        data-gpu-type="${gpuType}"
                        ${!unlocked || !canAfford ? 'disabled' : ''}>
                    ${!unlocked ? '🔒 Locked' : (canAfford ? 'Buy GPU' : 'Not enough $')}
                </button>
            `;
            
            container.appendChild(item);
        });
    }
    
    getCoolingName(tier) {
        const names = {
            'air': 'Air Cooling',
            'liquid': 'Liquid Cooling',
            'advanced_liquid': 'Advanced Liquid Cooling'
        };
        return names[tier] || tier;
    }
    
    renderContractsShop(state) {
        const container = document.getElementById('contracts-shop');
        if (!state.contracts) {
            container.innerHTML = '<p style="color: #888; padding: 20px;">Contracts system loading...</p>';
            return;
        }
        
        container.innerHTML = '';
        
        // Show active contracts first (sorted by monthly income ascending)
        if (state.contracts.active && state.contracts.active.length > 0) {
            const activeSection = document.createElement('div');
            activeSection.innerHTML = '<h3 style="color: #8b5cf6; margin-bottom: 10px;">🟣 Active Contracts</h3>';
            container.appendChild(activeSection);
            
            const sortedActive = [...state.contracts.active].sort((a, b) => a.monthly_income - b.monthly_income);
            sortedActive.forEach(contract => {
                container.appendChild(this.createContractCard(contract, 'active', state));
            });
        }
        
        // Show negotiating contracts (sorted by negotiation cost ascending)
        if (state.contracts.negotiating && state.contracts.negotiating.length > 0) {
            const negotiatingSection = document.createElement('div');
            negotiatingSection.innerHTML = '<h3 style="color: #f59e0b; margin: 20px 0 10px 0;">🟠 In Negotiation</h3>';
            container.appendChild(negotiatingSection);
            
            const sortedNegotiating = [...state.contracts.negotiating].sort((a, b) => a.negotiation_cost_total - b.negotiation_cost_total);
            sortedNegotiating.forEach(contract => {
                container.appendChild(this.createContractCard(contract, 'negotiating', state));
            });
        }
        
        // Show available contracts (sorted by negotiation cost ascending)
        if (state.contracts.available && state.contracts.available.length > 0) {
            const availableSection = document.createElement('div');
            availableSection.innerHTML = '<h3 style="color: #10b981; margin: 20px 0 10px 0;">🟢 Available Deals</h3>';
            container.appendChild(availableSection);
            
            const sortedAvailable = [...state.contracts.available].sort((a, b) => a.contract.negotiation_cost_total - b.contract.negotiation_cost_total);
            sortedAvailable.forEach(item => {
                container.appendChild(this.createContractCard(item.contract, item.eligible ? 'available' : 'locked', state, item.issues));
            });
        }
        
        // Show summary if there are active contracts
        if (state.contracts.active && state.contracts.active.length > 0) {
            const summary = document.createElement('div');
            summary.style.cssText = 'margin-top: 20px; padding: 15px; background: rgba(139, 92, 246, 0.2); border-radius: 8px; text-align: center;';
            summary.innerHTML = `
                <div style="color: #8b5cf6; font-weight: bold; font-size: 1.1em;">Total Contract Income</div>
                <div style="color: #8b5cf6; font-size: 1.5em; margin-top: 5px;">$${this.formatNumber(state.contracts.total_monthly_income)}/month</div>
                <div style="color: #888; font-size: 0.9em; margin-top: 5px;">${state.contracts.total_reserved_gpus} GPUs Reserved</div>
            `;
            container.appendChild(summary);
        }
    }
    
    createContractCard(contract, status, state, issues = []) {
        const card = document.createElement('div');
        card.className = `contract-card ${status}`;
        
        let content = `
            <div class="contract-header">
                <div class="contract-customer">
                    <div class="contract-logo">
                        <img src="${contract.customer_logo}" alt="${contract.name}" onerror="this.style.display='none'">
                    </div>
                    <div>
                        <div class="contract-name">${contract.name}</div>
                        <div class="contract-title">${contract.title}</div>
                    </div>
                </div>
                <div class="contract-status-badge ${status}">${status}</div>
            </div>
            <div class="contract-description">${contract.description}</div>
            <div class="contract-details">
                <div class="contract-detail">
                    <span class="contract-detail-label">Reserves:</span>
                    <span class="contract-detail-value">${contract.reserves_gpus} GPUs</span>
                </div>
                <div class="contract-detail">
                    <span class="contract-detail-label">Income:</span>
                    <span class="contract-detail-value">$${this.formatNumber(contract.monthly_income)}/mo</span>
                </div>
                <div class="contract-detail">
                    <span class="contract-detail-label">Duration:</span>
                    <span class="contract-detail-value">${contract.duration_months} months</span>
                </div>
                <div class="contract-detail">
                    <span class="contract-detail-label">Investment:</span>
                    <span class="contract-detail-value">$${this.formatNumber(contract.negotiation_cost_total)}</span>
                </div>
            </div>
        `;
        
        // Show requirements for locked/available contracts
        if (status === 'locked' || status === 'available') {
            const reqs = contract.requires;
            content += `
                <div class="contract-requirements">
                    <h4>Requirements:</h4>
                    ${reqs.min_gpus ? `<div class="contract-requirement ${issues.some(i => i.includes('GPU')) ? 'not-met' : 'met'}">${reqs.min_gpus}+ GPUs</div>` : ''}
                    ${reqs.min_h100s ? `<div class="contract-requirement ${issues.some(i => i.includes('H100')) ? 'not-met' : 'met'}">${reqs.min_h100s}+ H100-class GPUs</div>` : ''}
                    ${reqs.network ? `<div class="contract-requirement ${issues.some(i => i.includes('network')) ? 'not-met' : 'met'}">${reqs.network} networking</div>` : ''}
                    ${reqs.cooling ? `<div class="contract-requirement ${issues.some(i => i.includes('cooling')) ? 'not-met' : 'met'}">${reqs.cooling} cooling</div>` : ''}
                    ${reqs.min_revenue ? `<div class="contract-requirement ${issues.some(i => i.includes('revenue')) ? 'not-met' : 'met'}">$${this.formatNumber(reqs.min_revenue)} total revenue</div>` : ''}
                </div>
            `;
        }
        
        // Show negotiation progress
        if (status === 'negotiating') {
            content += `
                <div class="contract-negotiation">
                    <div class="negotiation-progress">
                        <span>Progress: ${contract.negotiation_progress}%</span>
                        <span>$${this.formatNumber(contract.money_invested)} / $${this.formatNumber(contract.negotiation_cost_total)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${contract.negotiation_progress}%">${contract.negotiation_progress}%</div>
                    </div>
                </div>
            `;
        }
        
        // Show income for active contracts
        if (status === 'active') {
            content += `
                <div class="contract-income">
                    <div>💰 Passive Income</div>
                    <div class="contract-income-amount">$${this.formatNumber(contract.monthly_income)}/month</div>
                    <div style="color: #888; font-size: 0.85em; margin-top: 4px;">${contract.months_remaining} months remaining</div>
                </div>
            `;
        }
        
        // Add action buttons
        if (status === 'available') {
            const canStart = issues.length === 0;
            content += `
                <div class="contract-actions">
                    <button class="contract-btn contract-btn-primary" 
                            onclick="gameManager.startContractNegotiation('${contract.id}')"
                            ${!canStart ? 'disabled' : ''}>
                        ${canStart ? 'Start Negotiation' : '🔒 Requirements Not Met'}
                    </button>
                </div>
            `;
        }
        
        if (status === 'negotiating') {
            const remaining = contract.negotiation_cost_total - contract.money_invested;
            const investAmount = Math.min(5000, remaining);
            const canInvest = state.cash >= investAmount;
            
            content += `
                <div class="contract-actions">
                    <button class="contract-btn contract-btn-invest" 
                            onclick="gameManager.investInContract('${contract.id}', ${investAmount})"
                            ${!canInvest ? 'disabled' : ''}>
                        ${canInvest ? `Invest $${this.formatNumber(investAmount)}` : 'Need More Cash'}
                    </button>
                </div>
            `;
        }
        
        card.innerHTML = content;
        return card;
    }
    
    /**
     * Render marketing shop (Simple Universal Paperclips style)
     */
    renderMarketingShop(state) {
        const container = document.getElementById('marketing-shop');
        if (!state.marketing) {
            container.innerHTML = '<p style="color: #888; padding: 20px;">Loading...</p>';
            return;
        }
        
        const { current, next, job_spawn_multiplier, job_value_multiplier, sla_extension, level } = state.marketing;
        
        const jobBoost = ((job_spawn_multiplier - 1) * 100).toFixed(0);
        const valueBoost = ((job_value_multiplier - 1) * 100).toFixed(0);
        
        let content = `
            <div class="marketing-simple">
                <div class="marketing-current">
                    <div class="marketing-level-title">Level ${level}: ${current.name}</div>
                    <div style="color: #aaa; font-size: 0.9em; margin-top: 8px; font-style: italic;">
                        ${current.description}
                    </div>
                    <div class="marketing-stats-simple">
                        📈 +${jobBoost}% Jobs | 💰 +${valueBoost}% Value${sla_extension > 0 ? ` | ⏱️ +${sla_extension}s SLA` : ''}
                    </div>
                </div>
        `;
        
        if (next) {
            const canAfford = state.cash >= next.cost;
            const unlocked = state.total_revenue >= next.unlock_revenue;
            
            let buttonText = '';
            let disabled = false;
            
            if (!unlocked) {
                buttonText = `🔒 Unlock at $${this.formatNumber(next.unlock_revenue)} revenue`;
                disabled = true;
            } else if (!canAfford) {
                buttonText = `Upgrade Marketing ($${this.formatNumber(next.cost)}) - Need more cash`;
                disabled = true;
            } else {
                buttonText = `Upgrade Marketing ($${this.formatNumber(next.cost)})`;
                disabled = false;
            }
            
            content += `
                <div style="color: #888; font-size: 0.9em; margin-bottom: 12px;">
                    <strong>Next:</strong> ${next.name}
                </div>
                <button id="marketing-upgrade-btn" class="marketing-upgrade-simple" ${disabled ? 'disabled' : ''}>
                    ${buttonText}
                </button>
            `;
        } else {
            content += `
                <div style="color: #10b981; font-size: 1.1em; margin-top: 20px;">
                    ✓ Max Marketing Level
                </div>
            `;
        }
        
        content += '</div>';
        container.innerHTML = content;
        
        // Re-attach event listener if button exists
        const upgradeBtn = document.getElementById('marketing-upgrade-btn');
        if (upgradeBtn) {
            upgradeBtn.addEventListener('click', async () => {
                await gameManager.upgradeMarketing();
            });
        }
    }
    
    /**
     * Update system info display
     */
    updateSystemInfo(state) {
        // Cooling (auto-managed)
        const coolingName = this.catalog && this.catalog.cooling_info && this.catalog.cooling_info[state.cooling_tier] 
            ? this.catalog.cooling_info[state.cooling_tier].name 
            : state.cooling_tier;
        document.getElementById('cooling-display').textContent = coolingName;
        
        // Network (auto-managed, show penalty %)
        const networkText = this.getNetworkText(state.stats.total_gpus, state.network_penalty_pct);
        document.getElementById('network-display').textContent = networkText;
        
        // Scheduler (auto-managed)
        const schedulerName = this.catalog && this.catalog.scheduler_info && this.catalog.scheduler_info[state.scheduler_tier]
            ? this.catalog.scheduler_info[state.scheduler_tier].name
            : state.scheduler_tier;
        document.getElementById('scheduler-display').textContent = schedulerName;
    }
    
    getNetworkText(gpuCount, penalty) {
        if (gpuCount <= 4) {
            return `Basic Ethernet (${penalty}%)`;
        } else if (gpuCount <= 12) {
            return `10 Gigabit Ethernet (${penalty}%)`;
        } else if (gpuCount <= 24) {
            return `NVLink (${penalty}%)`;
        } else {
            return `InfiniBand/Fabric (${penalty}%)`;
        }
    }
    
    /**
     * Update phase indicator
     */
    updatePhaseIndicator(state) {
        let phase = 'Phase 1: Desk';
        if (state.total_revenue >= 150000) {
            phase = 'Phase 3: Datacenter';
        } else if (state.total_revenue >= 30000) {
            phase = 'Phase 2: First Rack';
        }
        document.getElementById('phase-indicator').textContent = phase;
    }
    
    /**
     * Update auto-assign toggle button state
     */
    updateAutoAssignToggle(state) {
        const toggleBtn = document.getElementById('toggle-auto-assign');
        if (toggleBtn) {
            toggleBtn.textContent = state.auto_assign ? '🤖 Auto: ON' : '👆 Manual: ON';
            toggleBtn.classList.toggle('active', state.auto_assign);
        }
    }
    
    /**
     * Check for achievements and show notifications
     */
    checkAchievements(state) {
        // TODO: Implement achievement system
    }
    
    /**
     * Show a notification message
     */
    showNotification(message, type = 'success') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    /**
     * Format currency
     */
    formatCurrency(amount) {
        return '$' + this.formatNumber(Math.floor(amount));
    }
    
    /**
     * Format number with commas
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    
    /**
     * Show GPU selection modal for a job
     */
    showGPUSelector(job, availableGPUs) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'gpu-selector-modal';
        
        // Filter GPUs by requirements
        const compatibleGPUs = availableGPUs.filter(gpu => 
            gpu.vram >= job.vram_per_gpu && !gpu.current_job
        );
        const incompatibleGPUs = availableGPUs.filter(gpu => 
            gpu.vram < job.vram_per_gpu || gpu.current_job
        );
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Assign Job #${job.id}</h2>
                    <button class="modal-close" id="close-gpu-selector">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="job-requirements">
                        <h3>${job.type.charAt(0).toUpperCase() + job.type.slice(1)} - ${job.size}</h3>
                        <div class="requirement-item">
                            <strong>Required GPUs:</strong> ${job.gpu_count}
                        </div>
                        <div class="requirement-item">
                            <strong>VRAM per GPU:</strong> ${job.vram_per_gpu}GB
                        </div>
                        <div class="requirement-item">
                            <strong>Payout:</strong> $${job.base_payout}
                        </div>
                    </div>
                    
                    <div class="gpu-selection-info">
                        <p><strong>Select ${job.gpu_count} GPU${job.gpu_count > 1 ? 's' : ''}:</strong></p>
                        <p class="selection-count" id="selection-count">0 / ${job.gpu_count} selected</p>
                    </div>
                    
                    <div class="gpu-list">
                        ${compatibleGPUs.length > 0 ? `
                            <h4>Compatible GPUs</h4>
                            <div class="gpu-grid">
                                ${compatibleGPUs.map(gpu => `
                                    <div class="gpu-selector-card compatible" data-gpu-id="${gpu.id}">
                                        <div class="gpu-card-header">
                                            <span class="gpu-card-name">${gpu.name} #${gpu.id}</span>
                                            <input type="checkbox" class="gpu-checkbox" data-gpu-id="${gpu.id}">
                                        </div>
                                        <div class="gpu-card-specs">
                                            ${gpu.vram}GB VRAM
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <p class="no-gpus-message">No compatible GPUs available!</p>
                        `}
                        
                        ${incompatibleGPUs.length > 0 ? `
                            <h4 style="margin-top: 20px;">Incompatible GPUs</h4>
                            <div class="gpu-grid">
                                ${incompatibleGPUs.map(gpu => `
                                    <div class="gpu-selector-card incompatible" data-gpu-id="${gpu.id}">
                                        <div class="gpu-card-header">
                                            <span class="gpu-card-name">${gpu.name} #${gpu.id}</span>
                                        </div>
                                        <div class="gpu-card-specs">
                                            ${gpu.vram}GB VRAM
                                            ${gpu.current_job ? ' - Busy' : gpu.vram < job.vram_per_gpu ? ' - Not enough VRAM' : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" id="cancel-assignment">Cancel</button>
                    <button class="btn-confirm" id="confirm-assignment" disabled>Assign Job</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Set up event listeners
        this.setupGPUSelectorListeners(job, compatibleGPUs);
    }
    
    /**
     * Set up event listeners for GPU selector modal
     */
    setupGPUSelectorListeners(job, compatibleGPUs) {
        const modal = document.getElementById('gpu-selector-modal');
        const confirmBtn = document.getElementById('confirm-assignment');
        const cancelBtn = document.getElementById('cancel-assignment');
        const closeBtn = document.getElementById('close-gpu-selector');
        const checkboxes = modal.querySelectorAll('.gpu-checkbox');
        const selectionCount = document.getElementById('selection-count');
        
        let selectedGPUs = [];
        
        // Handle checkbox changes
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const gpuId = parseInt(e.target.dataset.gpuId);
                
                if (e.target.checked) {
                    // Check if we can add more
                    if (selectedGPUs.length < job.gpu_count) {
                        selectedGPUs.push(gpuId);
                    } else {
                        e.target.checked = false;
                        return;
                    }
                } else {
                    selectedGPUs = selectedGPUs.filter(id => id !== gpuId);
                }
                
                // Update selection count
                selectionCount.textContent = `${selectedGPUs.length} / ${job.gpu_count} selected`;
                
                // Enable/disable confirm button
                confirmBtn.disabled = selectedGPUs.length !== job.gpu_count;
            });
        });
        
        // Handle confirm
        confirmBtn.addEventListener('click', async () => {
            await gameManager.assignJobToGPUs(job.id, selectedGPUs);
            this.hideGPUSelector();
        });
        
        // Handle cancel/close
        const closeModal = () => this.hideGPUSelector();
        cancelBtn.addEventListener('click', closeModal);
        closeBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
    
    /**
     * Hide GPU selector modal
     */
    hideGPUSelector() {
        const modal = document.getElementById('gpu-selector-modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Global UI manager instance
const uiManager = new UIManager();

