/**
 * Educational Content Manager for GPU Tycoon
 * Manages educational popups, tips, and GPU descriptions
 */

class EducationManager {
    constructor() {
        this.shownMilestones = new Set(this.loadShownMilestones());
        this.lastRevenue = 0;
        this.lastGPUCount = 0;
        
        // GPU Educational Descriptions (from SHOP_ITEM_EDUCATION.md)
        this.gpuDescriptions = {
            'L4': {
                short: "Your entry point into AI infrastructure! Ada Lovelace efficiency at 72W TDP.",
                long: `<strong>The Humble L4</strong><br>
                    Don't let the 72W TDP fool you—Ada Lovelace's efficiency makes this GPU punch way above its weight class. 
                    Built on a 4nm process, it's perfect for inference workloads like Stable Diffusion or small LLM serving.<br><br>
                    <strong>Real-World Use:</strong> CoreWeave customers use L4s for burst inference capacity—when Character.AI 
                    goes viral, they spin up hundreds of L4 instances instantly.<br><br>
                    <strong>Fun Fact:</strong> You can fit 10 L4s in a standard 1U server while consuming less power than two H100s!`
            },
            'L40S': {
                short: "The 'Swiss Army Knife' of GPUs—graphics AND AI in one package.",
                long: `<strong>The Versatile L40S</strong><br>
                    With 48GB of VRAM, you can actually fit some decent models in memory without resorting to model sharding trickery. 
                    Ada's RT cores + Tensor cores = graphics AND AI workloads.<br><br>
                    <strong>Real-World Use:</strong> DNEG (VFX studio) uses L40S clusters to render "Dune" VFX during the day, 
                    then switches to fine-tuning Stable Diffusion models at night. GPU utilization: 💯<br><br>
                    <strong>Tech Detail:</strong> 18,176 CUDA cores—exactly 2.37x more than the L4. NVIDIA's die binning is chef's kiss.`
            },
            'A100': {
                short: "The OG datacenter king. HBM2e memory at 2TB/s bandwidth!",
                long: `<strong>The GPU That Made AI Mainstream</strong><br>
                    Released in 2020, the A100 powered GPT-3's training and every major LLM since. HBM2e memory at 2TB/s bandwidth 
                    means this thing feeds data to tensor cores faster than you can say "attention is all you need."<br><br>
                    <strong>Multi-Instance GPU (MIG):</strong> Slice one A100 into 7 isolated GPUs—perfect for multi-tenant 
                    cloud environments (hi, CoreWeave!).<br><br>
                    <strong>Real-World Use:</strong> Anthropic trained Claude 1.0 on A100 clusters. Cohere's production inference 
                    still runs on A100s because "if it ain't broke..."<br><br>
                    <strong>Mind-Blowing Stat:</strong> 312 TFLOPS of FP16 compute. That's 312 TRILLION operations per second!`
            },
            'H100': {
                short: "Jensen Huang's leather jacket special. Transformer Engine with FP8 precision!",
                long: `<strong>The Hopper Revolution</strong><br>
                    It's not just 'faster,' it's fundamentally different. Hopper introduced the Transformer Engine with FP8 precision—
                    specifically designed for modern LLM architectures. NVLink boosted to 900GB/s. Training LLaMA 2? You need H100s.<br><br>
                    <strong>What Makes It Special:</strong><br>
                    • FP8 precision with automatic loss scaling = 2x throughput for LLMs<br>
                    • NVLink Gen 4: 900GB/s per GPU = 7.2TB/s in an 8-GPU node<br>
                    • HBM3 Memory: 3.35TB/s bandwidth (1.6x faster than A100)<br><br>
                    <strong>Real-World Use:</strong> Meta trained LLaMA 2 70B on H100 clusters. OpenAI's GPT-4 inference runs on H100s.<br><br>
                    <strong>Power Note:</strong> At 700W, you can fry 7 eggs simultaneously on an H100's heatsink. Don't try this!`
            },
            'H200': {
                short: "Memory monster! 141GB HBM3e and 4.8TB/s bandwidth.",
                long: `<strong>More Memory = More Better</strong><br>
                    Same Hopper architecture as H100, but with a memory glow-up: 141GB of HBM3e (vs 80GB) and 4.8TB/s bandwidth 
                    (vs 3.35TB/s). That 141GB is the magic number—it can fit LLaMA 2 70B in FP16 with room to spare!<br><br>
                    <strong>Why It Matters:</strong> No tensor parallelism required for 70B models. What previously needed 
                    multi-GPU setups now fits on one H200.<br><br>
                    <strong>Real-World Use:</strong> CoreWeave was FIRST to market with H200 instances (Dec 2023). 
                    Customers use them for serving 70B models efficiently.<br><br>
                    <strong>Tech Tidbit:</strong> HBM3e's "e" stands for "extreme"—SK Hynix engineers achieved 1.15Tb/s per stack, 
                    a 50% improvement over base HBM3!`
            },
            'B200': {
                short: "Two GPUs in a trench coat! 208 billion transistors, FP4 precision.",
                long: `<strong>Welcome to the Future</strong><br>
                    Blackwell isn't just a new architecture—it's two dies fused with 10TB/s interconnect bandwidth, creating the 
                    world's largest chip. The second-gen Transformer Engine supports FP4 precision for inference, doubling throughput again.<br><br>
                    <strong>Dual-Die Design:</strong> Two chips act as one via ultra-high-bandwidth interconnect. It's not "multi-GPU," 
                    it's "one really thicc GPU."<br><br>
                    <strong>Real-World Use:</strong> OpenAI reportedly ordered 100,000+ B200 GPUs for GPT-5 training. 
                    Meta's future LLaMA models will train on Blackwell clusters.<br><br>
                    <strong>The 1000W Problem:</strong> At 1000W per GPU, an 8-GPU node consumes 8kW under load. 
                    That's why liquid cooling isn't optional—it's mandatory!`
            },
            'GB200': {
                short: "NVIDIA's 'screw it, we're making the whole server' moment. 672GB unified memory!",
                long: `<strong>The Ultimate Superchip</strong><br>
                    The GB200 fuses a 72-core ARM CPU (Grace) with a Blackwell GPU via 900GB/s NVLink-C2C. The CPU can access all 
                    192GB of GPU HBM3e directly—no PCIe bottleneck. It's not a GPU, it's a compute platform.<br><br>
                    <strong>Unified Memory Architecture:</strong> 672GB total (GPU + CPU) accessible by both processors. 
                    Designed for trillion-parameter models that don't fit anywhere else.<br><br>
                    <strong>No PCIe:</strong> CPU-GPU connected via 900GB/s NVLink-C2C—50x faster than PCIe 5.0.<br><br>
                    <strong>Real-World Use:</strong> The GB200 NVL72 rack (72 GB200s) offers 720 petaFLOPS—enough to train 
                    foundation models in record time. CoreWeave is deploying these for frontier AI workloads.<br><br>
                    <strong>Cooling Reality:</strong> At 1200W, one GB200 consumes more power than 16 L4 GPUs combined!`
            }
        };
        
        // Educational milestones
        this.milestones = {
            'first_gpu_purchase': {
                title: '🎉 Your First GPU!',
                content: `<h3 style="color: #10b981; margin-bottom: 15px;">Congratulations on expanding your datacenter!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        In the real world, GPU datacenters measure success by <strong>utilization</strong> (percentage of time GPUs 
                        are working) and <strong>revenue per GPU</strong>. Your goal is to keep those GPUs busy!
                    </p>
                    <div style="background: rgba(15, 255, 255, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #0fffff;">
                        <strong>💡 Pro Tip:</strong> Watch your utilization metric. High utilization (80%+) means you're maximizing 
                        revenue. Low utilization? You might have too many GPUs for your current workload.
                    </div>`
            },
            'first_4_gpu_job': {
                title: '🚀 Multi-GPU Training Job!',
                content: `<h3 style="color: #a855f7; margin-bottom: 15px;">Your first large-scale AI training job!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Large language models like GPT-4 and LLaMA 2 require <strong>multiple GPUs</strong> to train. These "Training" 
                        jobs need 4 GPUs working together, synchronized via high-speed interconnects.
                    </p>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        <strong>GPU Clusters:</strong> Try dragging one GPU onto another of the <em>same type</em> to create a cluster! 
                        Matched GPU types work better together (bonus performance), while mixed types have penalties.
                    </p>
                    <div style="background: rgba(168, 85, 247, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #a855f7;">
                        <strong>📚 Real World:</strong> Meta's LLaMA 2 70B was trained on clusters of H100 GPUs. The network between 
                        GPUs is critical—that's why you see networking auto-upgrade as your cluster grows!
                    </div>`
            },
            'cooling_upgrade': {
                title: '❄️ Liquid Cooling Unlocked!',
                content: `<h3 style="color: #0fffff; margin-bottom: 15px;">Your datacenter just got a major infrastructure upgrade!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        When GPUs hit 700W+ power consumption (like the H100), air cooling becomes physically impossible. 
                        <strong>Liquid cooling</strong> uses water-cooled plates directly on GPU dies to handle the heat.
                    </p>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Notice your <strong>PUE (Power Usage Effectiveness)</strong> improved? That's because liquid cooling 
                        is more efficient than air. Lower PUE = lower electricity bills!
                    </p>
                    <div style="background: rgba(15, 255, 255, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #0fffff;">
                        <strong>📊 The Numbers:</strong> PUE of 1.45 means for every 1kW powering GPUs, you're spending 0.45kW cooling them. 
                        Liquid cooling drops this to 1.28—a 12% energy savings!
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #10b981; margin-top: 12px;">
                        <strong>🌍 Real World:</strong> Meta's RSC (Research SuperCluster) uses liquid cooling for 16,000 A100s. 
                        The chilled water plant processes 5,000 gallons per minute!
                    </div>`
            },
            'phase_2_datacenter': {
                title: '🏢 Welcome to Phase 2: First Rack!',
                content: `<h3 style="color: #ffa500; margin-bottom: 15px;">You're no longer running GPUs under your desk!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Your infrastructure has grown significantly. Notice how your <strong>networking</strong> automatically upgraded? 
                        With more GPUs, the game gave you better interconnects (10 Gigabit Ethernet) to reduce multi-GPU job penalties.
                    </p>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        <strong>New Unlocks Available:</strong><br>
                        • A100 and H100 GPUs (with liquid cooling)<br>
                        • Better job schedulers (Priority Queue)<br>
                        • Marketing upgrades to attract bigger customers
                    </p>
                    <div style="background: rgba(255, 165, 0, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #ffa500;">
                        <strong>🎯 Phase 2 Goals:</strong> Focus on SLA compliance (meeting deadlines) and utilization. 
                        Consider investing in marketing to increase job flow!
                    </div>`
            },
            'first_contract': {
                title: '🤝 Enterprise Contract Signed!',
                content: `<h3 style="color: #8b5cf6; margin-bottom: 15px;">Congratulations on your first enterprise deal!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        <strong>Contracts</strong> represent real-world cloud commitments. Companies like OpenAI and Meta sign 
                        multi-month contracts guaranteeing GPU capacity in exchange for predictable income.
                    </p>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        <strong>How it works:</strong><br>
                        • Reserved GPUs can't be used for regular jobs<br>
                        • You earn passive income every month<br>
                        • Contracts run for a fixed duration
                    </p>
                    <div style="background: rgba(139, 92, 246, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #8b5cf6;">
                        <strong>💼 Real World:</strong> CoreWeave signs contracts with AI companies for thousands of GPUs at a time. 
                        These long-term commitments help datacenters predict revenue and plan infrastructure expansion.
                    </div>`
            },
            'high_utilization': {
                title: '⚡ Efficiency Expert!',
                content: `<h3 style="color: #10b981; margin-bottom: 15px;">You're running a highly efficient datacenter!</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Your utilization is above 80%—that means your GPUs are staying busy and generating revenue. 
                        This is what datacenter operators dream of!
                    </p>
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #10b981;">
                        <strong>📈 Industry Benchmark:</strong> Top cloud providers aim for 70-80% utilization. You're beating 
                        the industry average! Keep balancing GPU capacity with job demand.
                    </div>`
            }
        };
    }
    
    /**
     * Load which milestones have been shown from localStorage
     */
    loadShownMilestones() {
        try {
            const stored = localStorage.getItem('gpu_tycoon_milestones');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            return [];
        }
    }
    
    /**
     * Save shown milestones to localStorage
     */
    saveShownMilestones() {
        localStorage.setItem('gpu_tycoon_milestones', JSON.stringify([...this.shownMilestones]));
    }
    
    /**
     * Check for educational milestones based on game state
     */
    checkMilestones(state) {
        // First GPU purchase (beyond starting GPU)
        if (state.stats.total_gpus >= 2 && !this.shownMilestones.has('first_gpu_purchase')) {
            this.showMilestone('first_gpu_purchase');
        }
        
        // First 4-GPU job appears
        const has4GPUJob = state.job_queue.some(j => j.gpu_count >= 4) || 
                          state.active_jobs.some(j => j.gpu_count >= 4);
        if (has4GPUJob && !this.shownMilestones.has('first_4_gpu_job')) {
            this.showMilestone('first_4_gpu_job');
        }
        
        // Cooling upgrade (liquid cooling)
        if (state.cooling_tier !== 'air' && !this.shownMilestones.has('cooling_upgrade')) {
            this.showMilestone('cooling_upgrade');
        }
        
        // Phase 2 reached
        if (state.total_revenue >= 30000 && state.total_revenue < 40000 && 
            !this.shownMilestones.has('phase_2_datacenter')) {
            this.showMilestone('phase_2_datacenter');
        }
        
        // First contract
        if (state.contracts && state.contracts.active && state.contracts.active.length > 0 &&
            !this.shownMilestones.has('first_contract')) {
            this.showMilestone('first_contract');
        }
        
        // High utilization achievement (80%+ with 5+ GPUs)
        if (state.stats.utilization >= 80 && state.stats.total_gpus >= 5 &&
            !this.shownMilestones.has('high_utilization')) {
            this.showMilestone('high_utilization');
        }
        
        // Update contextual hints
        this.updateContextualHints(state);
    }
    
    /**
     * Update contextual tutorial hints based on game state
     */
    updateContextualHints(state) {
        // Cluster hint: Show when player has 2+ GPUs of the same type and multi-GPU jobs exist
        const clusterHint = document.getElementById('cluster-hint');
        if (clusterHint) {
            const hasMultiGPUJobs = state.job_queue.some(j => j.gpu_count >= 2) || 
                                   state.active_jobs.some(j => j.gpu_count >= 2);
            const gpuTypeCounts = {};
            state.gpus.forEach(gpu => {
                gpuTypeCounts[gpu.type] = (gpuTypeCounts[gpu.type] || 0) + 1;
            });
            const hasPotentialCluster = Object.values(gpuTypeCounts).some(count => count >= 2);
            const hasClusters = state.clusters && state.clusters.clusters && state.clusters.clusters.length > 0;
            
            // Show hint if conditions are met and player hasn't created clusters yet
            if (hasMultiGPUJobs && hasPotentialCluster && !hasClusters) {
                clusterHint.style.display = 'block';
            } else {
                clusterHint.style.display = 'none';
            }
        }
        
        // Utilization hint: Show when utilization is low (<40%) with 3+ GPUs
        const utilizationHint = document.getElementById('utilization-hint');
        if (utilizationHint) {
            const lowUtilization = state.stats.utilization < 40 && state.stats.total_gpus >= 3;
            const queueNotFull = state.job_queue.length < 5;
            utilizationHint.style.display = (lowUtilization && queueNotFull) ? 'block' : 'none';
        }
        
        // SLA hint: Show when SLA compliance is low (<85%) and job queue is backing up
        const slaHint = document.getElementById('sla-hint');
        if (slaHint) {
            const poorSLA = state.stats.sla_compliance < 85 && state.stats.jobs_completed > 10;
            const largeQueue = state.job_queue.length >= 8;
            slaHint.style.display = (poorSLA || largeQueue) ? 'block' : 'none';
        }
    }
    
    /**
     * Show an educational milestone
     */
    showMilestone(milestoneId) {
        const milestone = this.milestones[milestoneId];
        if (!milestone) return;
        
        this.shownMilestones.add(milestoneId);
        this.saveShownMilestones();
        
        const modal = document.getElementById('educational-modal');
        const title = document.getElementById('edu-modal-title');
        const body = document.getElementById('edu-modal-body');
        
        title.textContent = milestone.title;
        body.innerHTML = milestone.content;
        
        modal.style.display = 'flex';
        
        // Play sound if available
        if (window.audioManager) {
            audioManager.playSound('unlock');
        }
    }
    
    /**
     * Get GPU description for shop display
     */
    getGPUDescription(gpuType) {
        const desc = this.gpuDescriptions[gpuType];
        return desc ? desc.short : null;
    }
    
    /**
     * Show detailed GPU information modal
     */
    showGPUDetails(gpuType) {
        const desc = this.gpuDescriptions[gpuType];
        if (!desc) return;
        
        const modal = document.getElementById('educational-modal');
        const title = document.getElementById('edu-modal-title');
        const body = document.getElementById('edu-modal-body');
        
        title.innerHTML = `🎮 ${gpuType} Deep Dive`;
        body.innerHTML = desc.long;
        
        modal.style.display = 'flex';
    }
    
    /**
     * Reset all shown milestones (for debugging)
     */
    resetMilestones() {
        this.shownMilestones.clear();
        this.saveShownMilestones();
    }
}

// Create global education manager
const educationManager = new EducationManager();
window.educationManager = educationManager;

// Add a button to manually show welcome modal (for testing)
window.showWelcomeModal = function() {
    document.getElementById('welcome-modal').style.display = 'flex';
};

