"""Main game state management"""
import time
from collections import deque
import random
from .gpus import GPU, GPU_CATALOG
from .jobs import Job, JobGenerator, Scheduler
from .economy import Economy, COOLING_TIERS, SCHEDULER_TIERS, get_network_penalty
from .contracts import ContractManager
from .marketing import MarketingManager
from .clusters import ClusterManager

class GameState:
    """Central game state manager"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset game to initial state"""
        self.cash = 3000  # Start with enough to buy first L4
        self.total_revenue = 0
        self.total_power_cost = 0
        
        # GPU inventory
        self.gpus = []
        self.next_gpu_id = 1
        
        # Jobs
        self.job_queue = []
        self.active_jobs = []
        
        # Contracts
        self.contract_manager = ContractManager()
        
        # Marketing
        self.marketing_manager = MarketingManager()
        
        # GPU Clusters (drag-and-drop grouping)
        self.cluster_manager = ClusterManager()
        
        # Note: Cooling, networking, and schedulers are now AUTO-UPGRADED
        # - Cooling: Based on GPU inventory (auto-detected)
        # - Network: Based on GPU count (auto-scales)
        # - Scheduler: Based on revenue milestones (auto-unlocks)
        
        # Job assignment mode
        self.auto_assign = True  # Start with automation (Paperclips style)
        
        # Timing
        self.last_update = time.time()
        self.last_job_spawn = time.time()
        self.base_job_spawn_interval = 2.0  # Base spawn interval (modified by marketing + GPU count) - faster for better pacing
        self.job_spawn_interval = 2.0  # Actual spawn interval
        
        # Stats
        self.jobs_completed = 0
        self.sla_misses = 0
        # Rolling SLA history (recent jobs window)
        self.sla_history = deque(maxlen=200)
        
        # Victory & Achievements
        self.victory_achieved = False
        self.victory_type = None
        self.achievements = set()
        
        # Events
        self.active_event = None
        self.last_event_check = time.time()
        
        # Buy starting GPU
        self.purchase_gpu('L4')
    
    def update(self, dt=None):
        """Update game state"""
        current_time = time.time()
        if dt is None:
            dt = current_time - self.last_update
        self.last_update = current_time
        
        # Check for random events (every 60 seconds)
        if current_time - self.last_event_check >= 60:
            self._check_for_event()
            self.last_event_check = current_time
        
        # Update active event
        if self.active_event:
            self.active_event['time_remaining'] -= dt
            if self.active_event['time_remaining'] <= 0:
                self.active_event = None
        
        # Spawn new jobs
        if current_time - self.last_job_spawn >= self.job_spawn_interval:
            self._spawn_job()
            self.last_job_spawn = current_time
        
        # Update active jobs
        self._update_jobs(dt)
        
        # Schedule jobs (auto or manual mode)
        if self.auto_assign:
            self._schedule_jobs()
        
        # Calculate power costs (PUE auto-determined by GPU inventory)
        pue = Economy.get_current_pue(self.gpus)
        power_cost = Economy.calculate_power_cost(self.gpus, pue, dt)
        self.cash -= power_cost
        self.total_power_cost += power_cost
        
        # Update contracts and get passive income
        contract_income = self.contract_manager.update(dt)
        if contract_income > 0:
            self.cash += contract_income
            self.total_revenue += contract_income
        
        # Check for achievements
        self._check_achievements()
        
        # Check for victory conditions
        if not self.victory_achieved:
            self._check_victory()
    
    def _spawn_job(self):
        """Spawn a new job based on current phase"""
        # Apply marketing multipliers
        job_value_multiplier = self.marketing_manager.get_job_value_multiplier()
        sla_extension = self.marketing_manager.get_sla_extension()
        
        # Apply active event multipliers if any
        if self.active_event:
            job_value_multiplier *= self.active_event.get('value_multiplier', 1.0)
        
        # Get available GPU count for adaptive job generation
        available_gpus = self._get_available_gpus()
        available_gpu_count = len(available_gpus)

        # Queue-aware backpressure to avoid SLA spiral when scaling
        backlog = len(self.job_queue)
        target_queue_depth = 3 + max(0, available_gpu_count // 4)
        
        # Dynamic SLA extension when backlog grows
        backlog_sla_extension = 0
        if backlog > target_queue_depth:
            backlog_sla_extension = min(20, (backlog - target_queue_depth) * 2)

        # Generate job with awareness of current infrastructure
        if backlog < target_queue_depth * 2:
            job = JobGenerator.generate_job(
                self.total_revenue, 
                job_value_multiplier, 
                sla_extension + backlog_sla_extension,
                available_gpu_count
            )
            self.job_queue.append(job)
        
        # Update job spawn interval based on marketing AND GPU count
        # More GPUs = more jobs needed to keep them busy
        spawn_multiplier = self.marketing_manager.get_job_spawn_multiplier()
        
        # Dynamic scaling: More aggressive scaling for better GPU utilization
        # Target: Keep 60-80% of GPUs busy with visible queue (3-5 jobs waiting)
        # New formula provides faster scaling: 1 GPU = 1.5x, 5 GPUs = 4x, 10 GPUs = 7x, 50 GPUs = 20x
        if available_gpu_count > 0:
            # Square root scaling for more aggressive early game pacing
            capacity_multiplier = 1.5 + (available_gpu_count ** 0.7) / 1.5
        else:
            capacity_multiplier = 1.0
        
        # Combine marketing and capacity multipliers
        total_multiplier = spawn_multiplier * capacity_multiplier
        
        # Apply event multiplier if active
        if self.active_event:
            total_multiplier *= self.active_event.get('spawn_multiplier', 1.0)
        
        # Apply backpressure to spawn interval (slow down when backlog is high)
        backpressure_factor = 1.0 + max(0, backlog - target_queue_depth) * 0.2
        self.job_spawn_interval = (self.base_job_spawn_interval * backpressure_factor) / total_multiplier
    
    def _update_jobs(self, dt):
        """Update progress of active jobs"""
        completed = []
        
        for job in self.active_jobs:
            if job.update(dt):
                completed.append(job)
        
        # Handle completed jobs
        for job in completed:
            self.active_jobs.remove(job)
            
            # Calculate payout
            payout = job.calculate_payout()
            self.cash += payout
            self.total_revenue += payout
            self.jobs_completed += 1
            
            if job.is_sla_missed():
                self.sla_misses += 1
                self.sla_history.append(0)
            else:
                self.sla_history.append(1)
            
            # Free up GPUs
            for gpu in job.assigned_gpus:
                gpu.clear_job()

            # Also clear cluster busy flag if this job was running on a cluster
            # Find any cluster that contains all assigned GPUs
            for cluster in self.cluster_manager.clusters:
                assigned_ids = set(g.gpu_id for g in job.assigned_gpus)
                if assigned_ids.issubset(set(cluster.gpu_ids)):
                    if getattr(cluster, 'current_job', None) is job:
                        cluster.current_job = None
                    # A job can only belong to a single cluster unit; break after clearing
                    break
    
    def _schedule_jobs(self):
        """Try to schedule waiting jobs - cluster-aware with EDF ordering"""
        if not self.job_queue or not self.gpus:
            return

        # Get GPUs that are NOT reserved by contracts
        available_gpus = self._get_available_gpus()
        if not available_gpus:
            return

        # Get current network penalty (auto-scales with GPU count)
        network_penalty = get_network_penalty(len(self.gpus))

        # New cluster-aware scheduling with earliest-deadline-first (EDF)
        placed = []
        for job in sorted(self.job_queue[:], key=lambda j: j.sla_deadline):
            if job.started_at is not None:  # Skip already placed
                continue

            # Try to place on a cluster first (preferred)
            cluster_placed = self._try_place_on_cluster(job, available_gpus, network_penalty)

            if not cluster_placed:
                # Fall back to individual GPU scheduling
                # CRITICAL: Only use GPUs that are NOT in clusters for individual scheduling
                # Clustered GPUs must only be used as complete units
                unclustered_gpus = [gpu for gpu in available_gpus
                                   if self.cluster_manager.get_cluster_for_gpu(gpu.gpu_id) is None]

                if unclustered_gpus:
                    individual_placed = Scheduler.schedule_fifo([job], unclustered_gpus)
                    if individual_placed:
                        placed.append(job)
            else:
                placed.append(job)

        # Move placed jobs to active
        for job in placed:
            if job in self.job_queue:
                self.job_queue.remove(job)
                self.active_jobs.append(job)
    
    def _try_place_on_cluster(self, job, available_gpus, network_penalty):
        """Try to place a job on a suitable cluster.

        New semantics: clusters function as unified units that run a single task at a time
        using their combined VRAM. A cluster is eligible if:
        - All member GPUs are available
        - Total VRAM across the cluster >= job.vram_per_gpu * job.gpu_count

        Returns True if job was placed, False otherwise.
        """
        # Unified cluster semantics: pooled VRAM must satisfy the job's VRAM requirement
        # We do NOT multiply by job.gpu_count when using a cluster-as-one unit
        required_total_vram = job.vram_per_gpu

        suitable_clusters = []
        for cluster in self.cluster_manager.clusters:
            # Check availability of entire cluster
            cluster_gpus = [g for g in available_gpus if g.gpu_id in cluster.gpu_ids]
            if len(cluster_gpus) != len(cluster.gpu_ids):
                continue  # Some GPUs in cluster are reserved or missing

            if not all(g.is_available() for g in cluster_gpus):
                continue

            # Verify pooled VRAM capacity
            total_vram = sum(g.vram for g in cluster_gpus)
            if total_vram < required_total_vram:
                continue

            suitable_clusters.append((cluster, cluster_gpus, total_vram))

        if not suitable_clusters:
            return False

        # Prefer homogeneous clusters (all same GPU type)
        homogeneous = [(c, gpus, tv) for c, gpus, tv in suitable_clusters if c.is_homogeneous(self.gpus)]
        if homogeneous:
            cluster, cluster_gpus, _ = homogeneous[0]
        else:
            cluster, cluster_gpus, _ = suitable_clusters[0]

        assigned_gpus = cluster_gpus  # Use ALL cluster GPUs as a unified unit

        # Cross-node penalty if mixed GPU types and multi-GPU job semantics
        cross_penalty = 0.0
        gpu_types = [g.gpu_type for g in assigned_gpus]
        if len(set(gpu_types)) > 1 and job.gpu_count > 1:
            cross_penalty = network_penalty

        # Start the job and distribute VRAM needs across the cluster
        job.start(assigned_gpus, cross_penalty)

        remaining = required_total_vram
        # Greedy distribution by GPU VRAM capacity (largest first)
        for gpu in sorted(assigned_gpus, key=lambda x: x.vram, reverse=True):
            if remaining <= 0:
                alloc = 0
            else:
                alloc = min(gpu.vram, remaining)
            gpu.assign_job(job, vram_override=alloc)
            remaining -= alloc

        # Mark cluster as busy with this job
        cluster.current_job = job

        return True
    
    def _get_available_gpus(self):
        """Get GPUs that are not reserved by contracts"""
        reserved_ids = set()
        for contract in self.contract_manager.get_active_contracts():
            reserved_ids.update(contract.reserved_gpu_ids)
        
        return [gpu for gpu in self.gpus if gpu.gpu_id not in reserved_ids]
    
    def _check_for_event(self):
        """Randomly trigger demand spike events"""
        # Don't trigger if event already active or if too early in game
        if self.active_event or self.total_revenue < 10000:
            return
        
        # 20% chance every 60 seconds = ~1 event every 5 minutes
        if random.random() < 0.20:
            events = [
                {
                    'name': 'ChatGPT Launch Spike',
                    'description': 'OpenAI just launched a new model! Inference demand surging!',
                    'spawn_multiplier': 3.0,
                    'value_multiplier': 1.5,
                    'time_remaining': 30,
                    'duration': 30
                },
                {
                    'name': 'Training Rush',
                    'description': 'Major AI lab needs emergency compute for deadline!',
                    'spawn_multiplier': 2.0,
                    'value_multiplier': 2.0,
                    'time_remaining': 45,
                    'duration': 45
                },
                {
                    'name': 'Conference Demo Season',
                    'description': 'NeurIPS demos this week - everyone needs inference!',
                    'spawn_multiplier': 2.5,
                    'value_multiplier': 1.3,
                    'time_remaining': 60,
                    'duration': 60
                },
                {
                    'name': 'Viral AI App',
                    'description': 'A new AI app went viral! Burst capacity needed!',
                    'spawn_multiplier': 4.0,
                    'value_multiplier': 1.2,
                    'time_remaining': 20,
                    'duration': 20
                }
            ]
            self.active_event = random.choice(events)
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        # GPU milestones
        gpu_count = len(self.gpus)
        if gpu_count >= 10 and 'gpu_10' not in self.achievements:
            self.achievements.add('gpu_10')
        if gpu_count >= 50 and 'gpu_50' not in self.achievements:
            self.achievements.add('gpu_50')
        if gpu_count >= 100 and 'gpu_100' not in self.achievements:
            self.achievements.add('gpu_100')
        
        # Revenue milestones
        if self.total_revenue >= 100000 and 'revenue_100k' not in self.achievements:
            self.achievements.add('revenue_100k')
        if self.total_revenue >= 500000 and 'revenue_500k' not in self.achievements:
            self.achievements.add('revenue_500k')
        if self.total_revenue >= 1000000 and 'revenue_1m' not in self.achievements:
            self.achievements.add('revenue_1m')
        
        # SLA excellence
        if self.jobs_completed >= 100:
            sla_rate = 1 - (self.sla_misses / self.jobs_completed)
            if sla_rate >= 0.95 and 'sla_champion' not in self.achievements:
                self.achievements.add('sla_champion')
        
        # Efficiency
        if len(self.gpus) > 0:
            avg_util = sum(g.utilization for g in self.gpus) / len(self.gpus)
            if avg_util >= 0.85 and len(self.gpus) >= 20 and 'efficiency_expert' not in self.achievements:
                self.achievements.add('efficiency_expert')
        
        # PUE achievement
        pue = Economy.get_current_pue(self.gpus)
        if pue <= 1.25 and 'green_datacenter' not in self.achievements:
            self.achievements.add('green_datacenter')
        
        # Contract achievements
        active_contracts = len(self.contract_manager.get_active_contracts())
        if active_contracts >= 2 and 'enterprise_player' not in self.achievements:
            self.achievements.add('enterprise_player')
    
    def _check_victory(self):
        """Check for victory conditions"""
        # Victory Condition 1: Revenue Tycoon - Reach $5M total revenue
        if self.total_revenue >= 5000000 and not self.victory_achieved:
            self.victory_achieved = True
            self.victory_type = 'revenue_tycoon'
            return
        
        # Victory Condition 2: Datacenter Mogul - 200+ GPUs
        if len(self.gpus) >= 200 and not self.victory_achieved:
            self.victory_achieved = True
            self.victory_type = 'datacenter_mogul'
            return
        
        # Victory Condition 3: Enterprise King - All 4 major contracts active simultaneously
        active_contract_ids = [c.contract_id for c in self.contract_manager.get_active_contracts()]
        major_contracts = ['openai', 'meta', 'microsoft', 'anthropic']
        if all(cid in active_contract_ids for cid in major_contracts) and not self.victory_achieved:
            self.victory_achieved = True
            self.victory_type = 'enterprise_king'
            return
        
        # Victory Condition 4: Efficiency Master - 90%+ SLA, 80%+ utilization, PUE < 1.25, 50+ GPUs
        if (len(self.gpus) >= 50 and 
            self.jobs_completed >= 200 and
            not self.victory_achieved):
            sla_rate = 1 - (self.sla_misses / self.jobs_completed)
            avg_util = sum(g.utilization for g in self.gpus) / len(self.gpus)
            pue = Economy.get_current_pue(self.gpus)
            
            if sla_rate >= 0.90 and avg_util >= 0.80 and pue <= 1.25:
                self.victory_achieved = True
                self.victory_type = 'efficiency_master'
                return
    
    def purchase_gpu(self, gpu_type):
        """Purchase a new GPU (cooling costs auto-bundled)"""
        can_buy, reason = Economy.can_purchase('gpu', gpu_type, self.cash, self.total_revenue)
        
        if not can_buy:
            return False, reason
        
        cost = GPU_CATALOG[gpu_type]['cost']
        self.cash -= cost
        
        gpu = GPU(gpu_type, self.next_gpu_id)
        self.next_gpu_id += 1
        self.gpus.append(gpu)
        
        # Check if cooling tier upgraded automatically
        new_cooling = Economy.get_current_cooling_tier(self.gpus)
        message = f"Purchased {gpu.name}"
        
        return True, message
    
    def upgrade_marketing(self):
        """Upgrade marketing to next level"""
        success, message = self.marketing_manager.upgrade(self.cash, self.total_revenue)
        if success:
            next_level = self.marketing_manager.get_current_level_data()
            if 'cost' in next_level:  # First level has no cost
                self.cash -= next_level['cost']
        return success, message
    
    def assign_job_to_gpus(self, job_id, gpu_ids):
        """Manually assign a job from the queue to specific GPUs"""
        # Find the job in the queue
        job = None
        for j in self.job_queue:
            if j.job_id == job_id:
                job = j
                break

        if job is None:
            return False, "Job not found in queue"

        # Find the specified GPUs
        selected_gpus = []
        for gpu_id in gpu_ids:
            gpu = None
            for g in self.gpus:
                if g.gpu_id == gpu_id:
                    gpu = g
                    break
            if gpu is None:
                return False, f"GPU #{gpu_id} not found"
            selected_gpus.append(gpu)

        # If selection corresponds to an entire cluster, allow pooled VRAM semantics
        is_cluster_selection = False
        selected_cluster = None
        if gpu_ids:
            possible_cluster = self.cluster_manager.get_cluster_for_gpu(gpu_ids[0])
            if possible_cluster and set(gpu_ids) == set(possible_cluster.gpu_ids):
                is_cluster_selection = True
                selected_cluster = possible_cluster

        if is_cluster_selection:
            # Validate availability
            cluster_gpus = [g for g in self.gpus if g.gpu_id in selected_cluster.gpu_ids]
            if not all(g.is_available() for g in cluster_gpus):
                return False, f"Cluster #{selected_cluster.cluster_id} is busy"

            # Validate pooled VRAM
            # For cluster-as-one, total pooled requirement equals job.vram_per_gpu
            required_total_vram = job.vram_per_gpu
            total_vram = sum(g.vram for g in cluster_gpus)
            if total_vram < required_total_vram:
                return False, f"Cluster #{selected_cluster.cluster_id} does not have enough combined VRAM ({total_vram}GB < {required_total_vram}GB)"
        else:
            # Validate: correct number of GPUs for non-cluster manual selection
            if len(selected_gpus) != job.gpu_count:
                return False, f"Job requires exactly {job.gpu_count} GPU(s), but {len(selected_gpus)} selected"

        # NEW: Validate cluster integrity
        # - If cluster selection mode, do nothing (already validated as whole cluster)
        # - Otherwise, prevent mixing cluster GPUs with non-cluster GPUs
        if not is_cluster_selection:
            for gpu_id in gpu_ids:
                cluster = self.cluster_manager.get_cluster_for_gpu(gpu_id)
                if cluster:
                    cluster_gpu_set = set(cluster.gpu_ids)
                    selected_gpu_set = set(gpu_ids)
                    if cluster_gpu_set != selected_gpu_set:
                        missing = cluster_gpu_set - selected_gpu_set
                        extra = selected_gpu_set - cluster_gpu_set
                        if missing:
                            return False, f"Cluster #{cluster.cluster_id} must be used as a complete unit. Missing GPUs: {list(missing)}"
                        if extra:
                            return False, f"Cannot mix cluster GPUs with non-cluster GPUs"

        # Validate: all GPUs are available
        for gpu in selected_gpus:
            if not gpu.is_available():
                return False, f"GPU #{gpu.gpu_id} ({gpu.name}) is already busy"

        # Validate: VRAM
        if is_cluster_selection:
            pass  # pooled VRAM already validated above
        else:
            for gpu in selected_gpus:
                if gpu.vram < job.vram_per_gpu:
                    return False, f"GPU #{gpu.gpu_id} ({gpu.name}) has insufficient VRAM ({gpu.vram}GB < {job.vram_per_gpu}GB required)"

        # Calculate cross-node penalty (if GPUs are different types)
        cross_node_penalty = 0.0
        if is_cluster_selection:
            cluster_gpus = [g for g in self.gpus if g.gpu_id in selected_cluster.gpu_ids]
            if job.gpu_count > 1 and len(set(g.gpu_type for g in cluster_gpus)) > 1:
                cross_node_penalty = get_network_penalty(len(self.gpus))
            # Start the job across the entire cluster and distribute VRAM needs
            job.start(cluster_gpus, cross_node_penalty)

            required_total_vram = job.vram_per_gpu * job.gpu_count
            remaining = required_total_vram
            for gpu in sorted(cluster_gpus, key=lambda x: x.vram, reverse=True):
                if remaining <= 0:
                    alloc = 0
                else:
                    alloc = min(gpu.vram, remaining)
                gpu.assign_job(job, vram_override=alloc)
                remaining -= alloc

            # Mark cluster busy
            selected_cluster.current_job = job
        else:
            if job.gpu_count > 1 and len(set(g.gpu_type for g in selected_gpus)) > 1:
                cross_node_penalty = get_network_penalty(len(self.gpus))

            # Assign the job
            job.start(selected_gpus, cross_node_penalty)
            for gpu in selected_gpus:
                gpu.assign_job(job)

        # Move job from queue to active
        self.job_queue.remove(job)
        self.active_jobs.append(job)

        target_gpu_count = len(selected_cluster.gpu_ids) if is_cluster_selection else len(selected_gpus)
        return True, f"Job #{job_id} assigned to {target_gpu_count} GPU(s)"
    
    def toggle_auto_assign(self):
        """Toggle between auto and manual job assignment"""
        self.auto_assign = not self.auto_assign
        return self.auto_assign
    
    def create_gpu_cluster(self, gpu_ids):
        """Create a new GPU cluster from dragged GPUs"""
        # Validate GPUs exist and are not reserved
        available_gpu_ids = [g.gpu_id for g in self._get_available_gpus()]
        for gpu_id in gpu_ids:
            if gpu_id not in available_gpu_ids:
                return False, f"GPU #{gpu_id} is not available (reserved or doesn't exist)"
        
        success, result = self.cluster_manager.create_cluster(gpu_ids, self.gpus)
        return success, result
    
    def add_gpu_to_cluster(self, cluster_id, gpu_id):
        """Drag a GPU onto an existing cluster"""
        # Check if GPU is available
        available_gpu_ids = [g.gpu_id for g in self._get_available_gpus()]
        if gpu_id not in available_gpu_ids:
            return False, "GPU is not available"
        
        return self.cluster_manager.add_gpu_to_cluster(cluster_id, gpu_id, self.gpus)
    
    def remove_gpu_from_cluster(self, cluster_id, gpu_id):
        """Drag a GPU out of a cluster"""
        return self.cluster_manager.remove_gpu_from_cluster(cluster_id, gpu_id)
    
    def disband_cluster(self, cluster_id):
        """Disband an entire cluster"""
        return self.cluster_manager.disband_cluster(cluster_id)
    
    def start_contract_negotiation(self, contract_id):
        """Start negotiating a contract"""
        if contract_id not in self.contract_manager.contracts:
            return False, "Contract not found"
        
        contract = self.contract_manager.contracts[contract_id]
        
        # Check if player meets requirements
        meets_reqs, issues = contract.check_requirements(self)
        if not meets_reqs:
            return False, f"Requirements not met: {', '.join(issues)}"
        
        success, message = contract.start_negotiation()
        return success, message
    
    def invest_in_contract(self, contract_id, amount):
        """Invest money in contract negotiation"""
        if contract_id not in self.contract_manager.contracts:
            return False, "Contract not found"
        
        contract = self.contract_manager.contracts[contract_id]
        
        if self.cash < amount:
            return False, f"Need ${amount:,}"
        
        success, message = contract.invest_in_negotiation(amount)
        if success:
            self.cash -= amount
            
            # Auto-activate if negotiation is complete
            if contract.can_activate():
                return self._auto_activate_contract(contract)
        
        return success, message
    
    def _auto_activate_contract(self, contract):
        """Automatically activate a contract when negotiation completes"""
        # Select GPUs to reserve (prefer H100+ for these contracts)
        available_gpus = self._get_available_gpus()
        
        if len(available_gpus) < contract.reserves_gpus:
            return False, f"Not enough available GPUs! Need {contract.reserves_gpus}, have {len(available_gpus)}"
        
        # Prefer higher-end GPUs for contracts
        gpu_priority = {'GB200': 5, 'B200': 4, 'H200': 3, 'H100': 2, 'A100': 1}
        sorted_gpus = sorted(available_gpus, 
                           key=lambda g: gpu_priority.get(g.gpu_type, 0), 
                           reverse=True)
        
        selected_gpu_ids = [g.gpu_id for g in sorted_gpus[:contract.reserves_gpus]]
        
        success, message = contract.activate(selected_gpu_ids)
        return success, message
    
    def to_dict(self):
        """Convert game state to dictionary for JSON"""
        # Auto-calculate current infrastructure
        cooling_tier = Economy.get_current_cooling_tier(self.gpus)
        pue = Economy.get_current_pue(self.gpus)
        scheduler_tier = Economy.get_current_scheduler(self.total_revenue)
        network_penalty = get_network_penalty(len(self.gpus))
        
        # Calculate stats
        total_gpus = len(self.gpus)
        reserved_gpus = self.contract_manager.get_total_reserved_gpus()
        available_gpus = total_gpus - reserved_gpus
        
        avg_utilization = sum(g.utilization for g in self.gpus) / max(total_gpus, 1)
        # Rolling-window SLA compliance for UX-friendly pacing
        if len(getattr(self, 'sla_history', [])) > 0:
            sla_compliance = (sum(self.sla_history) / len(self.sla_history)) * 100.0
        else:
            sla_compliance = 100.0
        
        # Calculate revenue rate (per hour) - includes contract passive income
        revenue_per_hour = 0
        if self.jobs_completed > 0:
            avg_job_value = self.total_revenue / self.jobs_completed
            jobs_per_hour_per_gpu = 3600 / 10  # Rough estimate
            revenue_per_hour = avg_job_value * jobs_per_hour_per_gpu * available_gpus * avg_utilization
        
        # Add contract passive income (monthly to hourly)
        contract_monthly = self.contract_manager.get_total_monthly_income()
        revenue_per_hour += contract_monthly / (30 * 24)  # Convert monthly to hourly
        
        return {
            'cash': round(self.cash, 2),
            'total_revenue': round(self.total_revenue, 2),
            'total_power_cost': round(self.total_power_cost, 2),
            'gpus': [g.to_dict() for g in self.gpus],
            'job_queue': [j.to_dict() for j in self.job_queue],
            'active_jobs': [j.to_dict() for j in self.active_jobs],
            'cooling_tier': cooling_tier,
            'scheduler_tier': scheduler_tier,
            'network_penalty_pct': round(network_penalty * 100, 1),
            'auto_assign': self.auto_assign,
            'pue': round(pue, 2),
            'capacity': {
                'total': total_gpus,
                'reserved': reserved_gpus,
                'available': available_gpus,
                'utilization_pct': round(avg_utilization * 100, 1)
            },
            'stats': {
                'total_gpus': total_gpus,
                'utilization': round(avg_utilization * 100, 1),
                'sla_compliance': round(sla_compliance, 1),
                'jobs_completed': self.jobs_completed,
                'sla_misses': self.sla_misses,
                'revenue_per_hour': round(revenue_per_hour, 2)
            },
            'unlocks': self._get_unlocks(),
            'contracts': self.contract_manager.to_dict(self),
            'marketing': self.marketing_manager.to_dict(),
            'achievements': list(self.achievements),
            'victory': {
                'achieved': self.victory_achieved,
                'type': self.victory_type
            },
            'active_event': self.active_event,
            'clusters': self.cluster_manager.to_dict(self.gpus),
            'unclustered_gpus': self.cluster_manager.get_unclustered_gpus(self.gpus)
        }
    
    def _get_unlocks(self):
        """Get all unlocked items"""
        return {
            'gpus': Economy.get_unlocked_gpus(self.total_revenue)
        }

