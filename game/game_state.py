"""Main game state management"""
import time
import random
from .gpus import GPU, GPU_CATALOG
from .jobs import Job, JobGenerator, Scheduler
from .economy import Economy, COOLING_TIERS, SCHEDULER_TIERS, get_network_penalty
from .contracts import ContractManager
from .marketing import MarketingManager

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
        
        # Note: Cooling, networking, and schedulers are now AUTO-UPGRADED
        # - Cooling: Based on GPU inventory (auto-detected)
        # - Network: Based on GPU count (auto-scales)
        # - Scheduler: Based on revenue milestones (auto-unlocks)
        
        # Job assignment mode
        self.auto_assign = True  # Start with automation (Paperclips style)
        
        # Timing
        self.last_update = time.time()
        self.last_job_spawn = time.time()
        self.base_job_spawn_interval = 3.0  # Base spawn interval (modified by marketing)
        self.job_spawn_interval = 3.0  # Actual spawn interval
        
        # Stats
        self.jobs_completed = 0
        self.sla_misses = 0
        
        # Buy starting GPU
        self.purchase_gpu('L4')
    
    def update(self, dt=None):
        """Update game state"""
        current_time = time.time()
        if dt is None:
            dt = current_time - self.last_update
        self.last_update = current_time
        
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
    
    def _spawn_job(self):
        """Spawn a new job based on current phase"""
        # Apply marketing multipliers
        job_value_multiplier = self.marketing_manager.get_job_value_multiplier()
        sla_extension = self.marketing_manager.get_sla_extension()
        
        job = JobGenerator.generate_job(self.total_revenue, job_value_multiplier, sla_extension)
        self.job_queue.append(job)
        
        # Update job spawn interval based on marketing
        spawn_multiplier = self.marketing_manager.get_job_spawn_multiplier()
        self.job_spawn_interval = self.base_job_spawn_interval / spawn_multiplier
    
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
            
            # Free up GPUs
            for gpu in job.assigned_gpus:
                gpu.clear_job()
    
    def _schedule_jobs(self):
        """Try to schedule waiting jobs using simple FIFO"""
        if not self.job_queue or not self.gpus:
            return
        
        # Get GPUs that are NOT reserved by contracts
        available_gpus = self._get_available_gpus()
        if not available_gpus:
            return
        
        # Get current network penalty (auto-scales with GPU count)
        network_penalty = get_network_penalty(len(self.gpus))
        
        # Use simple FIFO scheduling with available GPUs only
        # Note: Scheduler automatically upgrades at revenue milestones
        placed = []
        for _ in range(len(self.job_queue)):
            if Scheduler.schedule_fifo(self.job_queue, available_gpus):
                # Find the job that was placed (has started)
                for job in self.job_queue:
                    if job.started_at is not None and job not in placed:
                        placed.append(job)
                        break
            else:
                break
        
        # Move placed jobs to active
        for job in placed:
            self.job_queue.remove(job)
            self.active_jobs.append(job)
            
            # Apply network penalty
            if job.cross_node_penalty > 0:
                job.cross_node_penalty = network_penalty
                job.duration = job.base_duration / (sum(g.performance for g in job.assigned_gpus) / len(job.assigned_gpus))
                job.duration *= (1 + network_penalty)
    
    def _get_available_gpus(self):
        """Get GPUs that are not reserved by contracts"""
        reserved_ids = set()
        for contract in self.contract_manager.get_active_contracts():
            reserved_ids.update(contract.reserved_gpu_ids)
        
        return [gpu for gpu in self.gpus if gpu.gpu_id not in reserved_ids]
    
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
        
        # Validate: correct number of GPUs
        if len(selected_gpus) != job.gpu_count:
            return False, f"Job requires exactly {job.gpu_count} GPU(s), but {len(selected_gpus)} selected"
        
        # Validate: all GPUs are available
        for gpu in selected_gpus:
            if not gpu.is_available():
                return False, f"GPU #{gpu.gpu_id} ({gpu.name}) is already busy"
        
        # Validate: all GPUs have enough VRAM
        for gpu in selected_gpus:
            if gpu.vram < job.vram_per_gpu:
                return False, f"GPU #{gpu.gpu_id} ({gpu.name}) has insufficient VRAM ({gpu.vram}GB < {job.vram_per_gpu}GB required)"
        
        # Calculate cross-node penalty (if GPUs are different types)
        cross_node_penalty = 0.0
        if job.gpu_count > 1 and len(set(g.gpu_type for g in selected_gpus)) > 1:
            cross_node_penalty = get_network_penalty(len(self.gpus))
        
        # Assign the job
        job.start(selected_gpus, cross_node_penalty)
        for gpu in selected_gpus:
            gpu.assign_job(job)
        
        # Move job from queue to active
        self.job_queue.remove(job)
        self.active_jobs.append(job)
        
        return True, f"Job #{job_id} assigned to {len(selected_gpus)} GPU(s)"
    
    def toggle_auto_assign(self):
        """Toggle between auto and manual job assignment"""
        self.auto_assign = not self.auto_assign
        return self.auto_assign
    
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
        sla_compliance = 100.0 if self.jobs_completed == 0 else (1 - self.sla_misses / max(self.jobs_completed, 1)) * 100
        
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
            'marketing': self.marketing_manager.to_dict()
        }
    
    def _get_unlocks(self):
        """Get all unlocked items"""
        return {
            'gpus': Economy.get_unlocked_gpus(self.total_revenue)
        }

