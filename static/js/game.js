/**
 * Game Manager for GPU Tycoon
 * Main game loop and API communication
 */

class GameManager {
    constructor() {
        this.isRunning = false;
        this.gameSpeed = 5; // Fixed at 5x speed
        this.tickInterval = 200; // 200ms default
        this.lastState = null;
    }
    
    /**
     * Initialize the game
     */
    async init() {
        console.log('🎮 Initializing GPU Tycoon...');
        
        // Load catalog
        await uiManager.loadCatalog();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start game loop
        this.start();
        
        console.log('✅ Game initialized!');
    }
    
    /**
     * Set up button click handlers
     */
    setupEventListeners() {
        // Initialize shop tabs
        uiManager.initShopTabs();

        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to reset the game? All progress will be lost.')) {
                this.resetGame();
            }
        });
        
        // Toggle auto-assign button
        document.getElementById('toggle-auto-assign').addEventListener('click', async () => {
            await this.toggleAutoAssign();
        });
        
        // Note: Marketing upgrade button listener is attached dynamically in renderMarketingShop()
        
        // Shop buttons (using event delegation)
        document.getElementById('shop-section').addEventListener('click', async (e) => {
            if (e.target.classList.contains('shop-btn') && !e.target.disabled) {
                const action = e.target.dataset.action;
                
                if (action === 'buy_gpu') {
                    const gpuType = e.target.dataset.gpuType;
                    await this.buyGPU(gpuType);
                } else if (action === 'buy_upgrade') {
                    const upgradeType = e.target.dataset.upgradeType;
                    const upgradeId = e.target.dataset.upgradeId;
                    await this.buyUpgrade(upgradeType, upgradeId);
                }
            }
        });
        
        // Job assignment buttons (using event delegation)
        document.getElementById('job-queue').addEventListener('click', (e) => {
            if (e.target.classList.contains('job-assign-btn')) {
                // Get job IDs from the data attribute (may be multiple grouped jobs)
                const jobIds = JSON.parse(e.target.dataset.jobIds || '[]');
                // Use the first (oldest) job from the group
                if (jobIds.length > 0) {
                    this.showJobAssignment(jobIds[0]);
                }
            }
        });

        // Speed controls and audio toggle
        const setActive = (id) => {
            const container = document.getElementById('speed-controls');
            if (!container) return;
            container.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
            const el = document.getElementById(id);
            if (el) el.classList.add('active');
        };

        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (this.isRunning) {
                    this.stop();
                    pauseBtn.textContent = '▶️ Resume';
                } else {
                    this.start();
                    pauseBtn.textContent = '⏸️ Pause';
                }
            });
        }

        const speed1 = document.getElementById('speed-1x');
        if (speed1) speed1.addEventListener('click', () => { this.gameSpeed = 1; setActive('speed-1x'); });
        const speed2 = document.getElementById('speed-2x');
        if (speed2) speed2.addEventListener('click', () => { this.gameSpeed = 2; setActive('speed-2x'); });
        const speed5 = document.getElementById('speed-5x');
        if (speed5) speed5.addEventListener('click', () => { this.gameSpeed = 5; setActive('speed-5x'); });

        const audioToggle = document.getElementById('audio-toggle');
        if (audioToggle) {
            audioToggle.addEventListener('click', () => {
                const enabled = audioManager.toggle();
                audioToggle.textContent = enabled ? '🔊 Audio: ON' : '🔇 Audio: OFF';
            });
        }
    }
    
    /**
     * Start the game loop
     */
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.gameLoop();
    }
    
    /**
     * Stop the game loop
     */
    stop() {
        this.isRunning = false;
    }
    
    /**
     * Main game loop
     */
    async gameLoop() {
        if (!this.isRunning) return;
        
        // Send tick to server
        await this.tick();
        
        // Fetch and update state
        await this.updateState();
        
        // Schedule next tick based on speed
        const delay = this.tickInterval / this.gameSpeed;
        setTimeout(() => this.gameLoop(), delay);
    }
    
    /**
     * Send tick command to server
     */
    async tick() {
        try {
            const dt = this.tickInterval / 1000; // Always send the same dt, regardless of speed
            await fetch('/api/tick', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dt })
            });
        } catch (e) {
            console.error('Tick error:', e);
        }
    }
    
    /**
     * Fetch game state from server and update UI
     */
    async updateState() {
        try {
            const response = await fetch('/api/state');
            const state = await response.json();
            
            // Update UI
            uiManager.update(state);
            
            this.lastState = state;
        } catch (e) {
            console.error('State update error:', e);
        }
    }
    
    /**
     * Buy a GPU
     */
    async buyGPU(gpuType) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'buy_gpu',
                    gpu_type: gpuType
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Buy GPU error:', e);
            uiManager.showNotification('Failed to purchase GPU', 'error');
        }
    }
    
    /**
     * Buy an upgrade
     */
    async buyUpgrade(upgradeType, upgradeId) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'buy_upgrade',
                    upgrade_type: upgradeType,
                    upgrade_id: upgradeId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Buy upgrade error:', e);
            uiManager.showNotification('Failed to purchase upgrade', 'error');
        }
    }
    
    /**
     * Reset the game
     */
    async resetGame() {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'reset' })
            });

            const result = await response.json();

            if (result.success) {
                uiManager.showNotification('Game reset!', 'success');
                await this.updateState();
            }
        } catch (e) {
            console.error('Reset error:', e);
        }
    }

    /**
     * Toggle auto-assign mode
     */
    async toggleAutoAssign() {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'toggle_auto_assign' })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Toggle auto-assign error:', e);
        }
    }
    
    /**
     * Upgrade marketing level
     */
    async upgradeMarketing() {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'upgrade_marketing' })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Upgrade marketing error:', e);
            uiManager.showNotification('Failed to upgrade marketing', 'error');
        }
    }
    
    /**
     * Show job assignment interface
     */
    showJobAssignment(jobId) {
        if (!this.lastState) return;

        // Find the job in the queue
        const job = this.lastState.job_queue.find(j => j.id === jobId);
        if (!job) {
            console.error('Job not found:', jobId);
            return;
        }

        // Show GPU selector modal with clusters
        uiManager.showGPUSelector(job, this.lastState.gpus, this.lastState.clusters);
    }
    
    /**
     * Assign a job to specific GPUs
     */
    async assignJobToGPUs(jobId, gpuIds) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'assign_job',
                    job_id: jobId,
                    gpu_ids: gpuIds
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Assign job error:', e);
            uiManager.showNotification('Failed to assign job', 'error');
        }
    }
    
    /**
     * Start contract negotiation
     */
    async startContractNegotiation(contractId) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'start_contract_negotiation',
                    contract_id: contractId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Start contract negotiation error:', e);
            uiManager.showNotification('Failed to start negotiation', 'error');
        }
    }
    
    /**
     * Invest in contract negotiation
     */
    async investInContract(contractId, amount) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'invest_in_contract',
                    contract_id: contractId,
                    amount: amount
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                uiManager.showNotification(result.message, 'success');
                audioManager.purchase();
            } else {
                uiManager.showNotification(result.message, 'error');
            }
            
            // Force update
            await this.updateState();
        } catch (e) {
            console.error('Invest in contract error:', e);
            uiManager.showNotification('Failed to invest in contract', 'error');
        }
    }
}

// Global game manager instance
const gameManager = new GameManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    gameManager.init();
});

// Show loading message
console.log('🎮 GPU Tycoon - Loading...');

