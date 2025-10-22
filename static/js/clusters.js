/**
 * GPU Cluster Drag-and-Drop System
 * Phase 1: Manual cluster creation for multi-GPU jobs
 */

class ClusterManager {
    constructor() {
        this.draggedGpu = null;
    }
    
    /**
     * Initialize drag-and-drop on GPU cards
     */
    initializeDragDrop() {
        // This will be called after GPU rack is rendered
        const gpuRack = document.getElementById('gpu-rack');
        if (!gpuRack) return;
        
        // Set up drop zone for creating new clusters (drag GPU onto another GPU)
        gpuRack.addEventListener('dragover', this.handleDragOver.bind(this));
        gpuRack.addEventListener('drop', this.handleDrop.bind(this));
    }
    
    /**
     * Make a GPU card draggable
     */
    makeGPUDraggable(gpuElement, gpuId, gpuType, isInCluster = false) {
        if (isInCluster) {
            // Don't make clustered GPUs draggable, but return the element
            gpuElement.draggable = false;
            return gpuElement;
        }

        // Remove any existing event listeners by cloning
        const newElement = gpuElement.cloneNode(true);
        gpuElement.parentNode.replaceChild(newElement, gpuElement);
        gpuElement = newElement;
        
        gpuElement.draggable = true;
        gpuElement.dataset.gpuId = gpuId;
        gpuElement.dataset.gpuType = gpuType;
        gpuElement.dataset.isInCluster = isInCluster;
        
        gpuElement.addEventListener('dragstart', (e) => {
            this.draggedGpu = {
                id: gpuId,
                type: gpuType,
                element: gpuElement,
                isInCluster: isInCluster
            };
            
            gpuElement.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', gpuId);
            
            // Highlight all matching GPU types
            document.querySelectorAll(`.gpu-bar[data-gpu-type="${gpuType}"]`).forEach(el => {
                if (el !== gpuElement && el.dataset.clustered !== 'true') {
                    el.classList.add('drop-target-match');
                }
            });
            
            // Highlight existing clusters
            document.querySelectorAll('.cluster-card').forEach(el => {
                el.style.opacity = '1';
            });
            
            console.log(`🎯 Dragging ${gpuType} #${gpuId} - Looking for other ${gpuType} GPUs...`);
        });
        
        gpuElement.addEventListener('dragend', (e) => {
            gpuElement.classList.remove('dragging');
            this.draggedGpu = null;
            
            // Remove all visual highlights
            document.querySelectorAll('.drag-over, .drag-invalid, .drop-target-match').forEach(el => {
                el.classList.remove('drag-over', 'drag-invalid', 'drop-target-match');
            });
        });
        
        // Prevent default drag behavior on drag handle
        const dragHandle = gpuElement.querySelector('.gpu-drag-handle');
        if (dragHandle) {
            dragHandle.addEventListener('mousedown', (e) => {
                // Allow the drag to start
                gpuElement.style.cursor = 'grabbing';
            });
            dragHandle.addEventListener('mouseup', (e) => {
                gpuElement.style.cursor = 'grab';
            });
        }
        
        return gpuElement;
    }
    
    /**
     * Make a cluster card accept GPU drops
     */
    makeClusterDroppable(clusterElement, clusterId) {
        clusterElement.dataset.clusterId = clusterId;
        
        clusterElement.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (this.draggedGpu && !this.draggedGpu.isInCluster) {
                clusterElement.classList.add('drag-over');
                e.dataTransfer.dropEffect = 'move';
            }
        });
        
        clusterElement.addEventListener('dragleave', (e) => {
            if (e.target === clusterElement) {
                clusterElement.classList.remove('drag-over');
            }
        });
        
        clusterElement.addEventListener('drop', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            clusterElement.classList.remove('drag-over');
            
            if (this.draggedGpu && !this.draggedGpu.isInCluster) {
                // Add GPU to cluster
                await this.addGPUToCluster(clusterId, this.draggedGpu.id);
            }
        });
    }
    
    /**
     * Handle drag over events
     */
    handleDragOver(e) {
        if (!this.draggedGpu) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        // Find the potential drop target
        const target = e.target.closest('.gpu-bar, .cluster-card');
        
        // Remove previous highlights
        document.querySelectorAll('.drag-over, .drag-invalid').forEach(el => {
            if (el !== target) {
                el.classList.remove('drag-over', 'drag-invalid');
            }
        });
        
        if (target && target !== this.draggedGpu.element) {
            // Check if this is a valid drop target
            const isValid = this.isValidDropTarget(target);
            
            if (isValid) {
                target.classList.add('drag-over');
                target.classList.remove('drag-invalid');
                e.dataTransfer.dropEffect = 'move';
            } else {
                target.classList.add('drag-invalid');
                target.classList.remove('drag-over');
                e.dataTransfer.dropEffect = 'none';
            }
        }
    }
    
    /**
     * Check if a drop target is valid (same GPU type)
     */
    isValidDropTarget(target) {
        if (!this.draggedGpu) return false;
        
        // Check if target is a GPU bar
        if (target.classList.contains('gpu-bar')) {
            const targetGpuType = target.dataset.gpuType;
            const targetClustered = target.dataset.clustered === 'true';
            
            // Can only drop on unclustered GPUs of the same type
            if (!targetClustered && targetGpuType === this.draggedGpu.type) {
                return true;
            }
        }
        
        // Check if target is a cluster
        if (target.classList.contains('cluster-card')) {
            const clusterId = parseInt(target.dataset.clusterId);
            // For now, allow adding to any cluster
            // Could add type checking here if needed
            return !this.draggedGpu.isInCluster;
        }
        
        return false;
    }
    
    /**
     * Handle drop events
     */
    async handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!this.draggedGpu) return;
        
        // Check if dropped on another GPU (create new cluster)
        const targetGpu = e.target.closest('.gpu-bar');
        if (targetGpu && targetGpu.dataset.gpuId) {
            const targetGpuId = parseInt(targetGpu.dataset.gpuId);
            const targetGpuType = targetGpu.dataset.gpuType;
            const targetClustered = targetGpu.dataset.clustered === 'true';
            const draggedGpuId = this.draggedGpu.id;
            const draggedGpuType = this.draggedGpu.type;
            
            // Validate: same GPU type, not already clustered, different GPUs
            if (targetGpuId !== draggedGpuId && !targetClustered && targetGpuType === draggedGpuType) {
                console.log(`✨ Creating cluster with ${draggedGpuType} #${draggedGpuId} + #${targetGpuId}`);
                await this.createCluster([draggedGpuId, targetGpuId]);
            } else if (targetGpuType !== draggedGpuType) {
                this.showNotification(`❌ Can only cluster same GPU types! (${draggedGpuType} ≠ ${targetGpuType})`, 'error');
            }
        }
        
        // Check if dropped on cluster
        const targetCluster = e.target.closest('.cluster-card');
        if (targetCluster && !this.draggedGpu.isInCluster) {
            const clusterId = parseInt(targetCluster.dataset.clusterId);
            console.log(`✨ Adding GPU to cluster #${clusterId}`);
            await this.addGPUToCluster(clusterId, this.draggedGpu.id);
        }
        
        // Remove all drag-over highlights
        document.querySelectorAll('.drag-over, .drag-invalid').forEach(el => {
            el.classList.remove('drag-over', 'drag-invalid');
        });
    }
    
    /**
     * Create a new cluster via API
     */
    async createCluster(gpuIds) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'create_cluster',
                    gpu_ids: gpuIds
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('✅ Cluster created:', result.message);
                this.showNotification('✅ ' + result.message, 'success');
            } else {
                console.error('❌ Failed to create cluster:', result.message);
                this.showNotification('❌ ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error creating cluster:', error);
            this.showNotification('❌ Network error', 'error');
        }
    }
    
    /**
     * Add GPU to existing cluster
     */
    async addGPUToCluster(clusterId, gpuId) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'add_to_cluster',
                    cluster_id: clusterId,
                    gpu_id: gpuId
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('✅ GPU added to cluster:', result.message);
                this.showNotification('✅ ' + result.message, 'success');
            } else {
                this.showNotification('❌ ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error adding GPU to cluster:', error);
        }
    }
    
    /**
     * Remove GPU from cluster
     */
    async removeGPUFromCluster(clusterId, gpuId) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'remove_from_cluster',
                    cluster_id: clusterId,
                    gpu_id: gpuId
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('✅ ' + result.message, 'success');
            } else {
                this.showNotification('❌ ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error removing GPU from cluster:', error);
        }
    }
    
    /**
     * Disband entire cluster
     */
    async disbandCluster(clusterId) {
        if (!confirm('Disband this cluster? GPUs will return to individual pool.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'disband_cluster',
                    cluster_id: clusterId
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('✅ Cluster disbanded', 'success');
            } else {
                this.showNotification('❌ ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error disbanding cluster:', error);
        }
    }
    
    /**
     * Show notification toast
     */
    showNotification(message, type = 'info') {
        // Simple notification - could be enhanced
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    /**
     * Render clusters in the GPU rack
     */
    renderClusters(state) {
        if (!state.clusters || !state.clusters.clusters) return;
        
        const rackContainer = document.getElementById('gpu-rack');
        if (!rackContainer) return;
        
        // Render each cluster
        state.clusters.clusters.forEach(cluster => {
            const existingCluster = document.querySelector(`[data-cluster-id="${cluster.id}"]`);
            
            if (!existingCluster) {
                // Create new cluster card
                const clusterCard = this.createClusterCard(cluster, state.gpus);
                rackContainer.insertBefore(clusterCard, rackContainer.firstChild);
                this.makeClusterDroppable(clusterCard, cluster.id);
            } else {
                // Update existing cluster
                this.updateClusterCard(existingCluster, cluster, state.gpus);
            }
        });
    }
    
    /**
     * Create a cluster card element
     */
    createClusterCard(cluster, allGpus) {
        const card = document.createElement('div');
        card.className = 'cluster-card';
        card.dataset.clusterId = cluster.id;
        
        // Find GPU objects for this cluster
        const clusterGpus = allGpus.filter(g => cluster.gpu_ids.includes(g.id));
        
        // Determine cluster type
        const clusterType = cluster.is_homogeneous ? 'homogeneous' : 'mixed';
        const statusIcon = cluster.is_homogeneous ? '🔗' : '⚠️';
        const statusText = cluster.is_homogeneous ? 'Synced' : 'Mixed';
        const statusColor = cluster.is_homogeneous ? '#10b981' : '#f59e0b';
        
        card.innerHTML = `
            <div class="cluster-header">
                <span class="cluster-title">
                    <span style="color: ${statusColor}">${statusIcon}</span>
                    GPU Cluster #${cluster.id}
                </span>
                <button class="cluster-disband-btn" onclick="clusterManager.disbandCluster(${cluster.id})">
                    ✕ Disband
                </button>
            </div>
            <div class="cluster-info">
                <div class="cluster-stat">
                    <span class="cluster-stat-label">${cluster.size} GPUs</span>
                    <span class="cluster-stat-value" style="color: ${statusColor}">${statusText}</span>
                </div>
                <div class="cluster-stat">
                    <span class="cluster-stat-label">Total VRAM:</span>
                    <span class="cluster-stat-value">${cluster.total_vram}GB</span>
                </div>
                <div class="cluster-stat">
                    <span class="cluster-stat-label">Available:</span>
                    <span class="cluster-stat-value">${cluster.available_vram}GB</span>
                </div>
            </div>
            <div class="cluster-gpus">
                ${clusterGpus.map(gpu => `
                    <div class="cluster-gpu-chip" data-gpu-id="${gpu.id}">
                        ${gpu.name.replace('NVIDIA ', '')} #${gpu.id}
                        <button class="cluster-gpu-remove" onclick="clusterManager.removeGPUFromCluster(${cluster.id}, ${gpu.id})">
                            ×
                        </button>
                    </div>
                `).join('')}
            </div>
            <div class="cluster-drop-hint">
                Drop GPU here to add to cluster
            </div>
        `;
        
        return card;
    }
    
    /**
     * Update an existing cluster card
     */
    updateClusterCard(cardElement, cluster, allGpus) {
        // Update VRAM stats
        const totalVramEl = cardElement.querySelector('.cluster-stat-value');
        if (totalVramEl) {
            totalVramEl.textContent = `${cluster.total_vram}GB`;
        }
        
        // Could add more dynamic updates here
    }
}

// Global instance
const clusterManager = new ClusterManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    clusterManager.initializeDragDrop();
});

