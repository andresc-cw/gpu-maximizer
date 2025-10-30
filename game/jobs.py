"""Job generation and scheduling system"""
import random
import time

# Fictional GPU cloud customers by job type
INFERENCE_CUSTOMERS = [
    'QueryMind AI',
    'ChatBuddy Corp',
    'PixelFlow Studio',
    'ModelHub Systems',
    'VoiceGen Labs',
    'DreamRender AI'
]

TRAINING_CUSTOMERS = [
    'SafetyFirst AI',
    'EnterpriseNLP Corp',
    'AutoDrive Systems',
    'ArtGen Studio',
    'AgentFlow AI',
    'PersonalAI Labs',
    'NeuralCore Research',
    'CogniTech Labs'
]

# Task descriptions for each customer
CUSTOMER_TASKS = {
    # Inference customers
    'QueryMind AI': 'Search Query Processing',
    'ChatBuddy Corp': 'Conversational Inference',
    'PixelFlow Studio': 'Video Generation',
    'ModelHub Systems': 'Model API Inference',
    'VoiceGen Labs': 'Voice Synthesis',
    'DreamRender AI': 'Image Generation',
    
    # Training customers
    'SafetyFirst AI': 'LLM Model Training',
    'EnterpriseNLP Corp': 'LLM Fine-tuning',
    'AutoDrive Systems': 'Perception Model Training',
    'ArtGen Studio': 'Diffusion Model Training',
    'AgentFlow AI': 'Action Transformer Training',
    'PersonalAI Labs': 'Large-scale Pretraining',
    'NeuralCore Research': 'Foundation Model Training',
    'CogniTech Labs': 'Multi-modal Training'
}

class Job:
    """Represents a compute job"""
    _next_id = 1
    
    def __init__(self, job_type, base_duration, vram_per_gpu, base_payout, sla_window, gpu_count, customer_name, task_description):
        self.job_id = Job._next_id
        Job._next_id += 1
        
        self.job_type = job_type  # 'inference' or 'training'
        # Size classification: S (1 GPU), M (2 GPUs), L (4 GPUs)
        if gpu_count == 1:
            self.size = 'S'
        elif gpu_count == 2:
            self.size = 'M'
        else:
            self.size = 'L'
        self.gpu_count = gpu_count
        self.base_duration = base_duration
        self.duration = base_duration
        self.vram_per_gpu = vram_per_gpu
        self.base_payout = base_payout
        
        self.customer_name = customer_name
        self.task_description = task_description
        
        self.created_at = time.time()
        self.sla_deadline = self.created_at + sla_window
        self.started_at = None
        self.progress = 0.0
        
        # Assigned GPUs
        self.assigned_gpus = []
        self.cross_node_penalty = 0.0
        
        # Multi-GPU coordination (for 2+ GPU jobs)
        self.is_multi_gpu = gpu_count > 1
        self.gpu_sync_points = []  # Track synchronization events
        self.last_sync_time = None
        self.performance_multiplier = 1.0  # Bonus for well-matched GPUs
    
    def start(self, gpus, cross_node_penalty=0.0):
        """Start job on assigned GPUs"""
        self.started_at = time.time()
        self.assigned_gpus = gpus
        self.cross_node_penalty = cross_node_penalty
        
        # Multi-GPU performance calculation
        if gpus:
            if len(gpus) == 1:
                # Single GPU: straightforward
                avg_performance = gpus[0].performance
                self.performance_multiplier = 1.0
            else:
                # Multi-GPU: Calculate based on parallelism type
                avg_performance = sum(g.performance for g in gpus) / len(gpus)
                
                # DATA PARALLELISM BONUS: Well-matched GPUs work better together
                # Check if GPUs are the same type (perfect sync) or different (sync overhead)
                gpu_types = [g.gpu_type for g in gpus]
                unique_types = len(set(gpu_types))
                
                if unique_types == 1:
                    # Perfect match: All same GPU type
                    # Bonus: Near-linear scaling (95% efficiency per GPU)
                    self.performance_multiplier = 0.95 * len(gpus)
                    
                    # Additional bonus for high-end GPUs (better interconnect)
                    if gpus[0].gpu_type in ['H100', 'H200', 'B200', 'GB200']:
                        self.performance_multiplier *= 1.05  # NVLink benefit
                else:
                    # Mixed GPUs: Limited by slowest GPU + sync overhead
                    # This is realistic: heterogeneous clusters have coordination costs
                    min_performance = min(g.performance for g in gpus)
                    max_performance = max(g.performance for g in gpus)
                    performance_variance = (max_performance - min_performance) / max_performance
                    
                    # Penalty based on variance (0-20% overhead)
                    sync_penalty = 1.0 - (performance_variance * 0.2)
                    
                    # Slower GPUs bottleneck the batch processing
                    # Use weighted average favoring the slowest GPU
                    weighted_avg = (min_performance * 0.6 + avg_performance * 0.4)
                    self.performance_multiplier = weighted_avg * len(gpus) * sync_penalty * 0.85
                
                # Initialize sync points for visual feedback
                # Multi-GPU jobs sync every 25% of progress (realistic for gradient sync)
                self.gpu_sync_points = [0.25, 0.50, 0.75, 1.0]
                self.last_sync_time = self.started_at
            
            self.duration = self.base_duration / avg_performance
        
        # Apply cross-node penalty (network bandwidth limitations)
        self.duration = self.duration * (1 + cross_node_penalty)
    
    def update(self, dt):
        """Update job progress, returns True if completed"""
        if self.started_at is None:
            return False
        
        old_progress = self.progress
        self.progress += dt / self.duration
        
        # Check for sync points (gradient synchronization in multi-GPU training)
        if self.is_multi_gpu and self.gpu_sync_points:
            for sync_point in self.gpu_sync_points[:]:  # Copy list to avoid modification during iteration
                if old_progress < sync_point <= self.progress:
                    # We just crossed a sync point!
                    self.last_sync_time = time.time()
                    # Remove this sync point so we don't trigger it again
                    self.gpu_sync_points.remove(sync_point)
        
        if self.progress >= 1.0:
            return True
        return False
    
    def calculate_payout(self):
        """Calculate final payout including SLA penalty"""
        payout = self.base_payout
        
        # SLA miss penalty: -30%
        if self.started_at and self.started_at > self.sla_deadline:
            payout *= 0.7
        
        return payout
    
    def is_sla_missed(self):
        """Check if job missed SLA"""
        if self.started_at is None:
            return time.time() > self.sla_deadline
        return self.started_at > self.sla_deadline
    
    def to_dict(self):
        # Check if we recently synced (within last 0.5 seconds) for visual feedback
        is_syncing = False
        if self.is_multi_gpu and self.last_sync_time:
            is_syncing = (time.time() - self.last_sync_time) < 0.5
        
        # Determine GPU coordination status
        gpu_coordination = 'single'
        if self.is_multi_gpu and self.assigned_gpus:
            gpu_types = [g.gpu_type for g in self.assigned_gpus]
            if len(set(gpu_types)) == 1:
                gpu_coordination = 'matched'  # Same GPU types
            else:
                gpu_coordination = 'mixed'    # Different GPU types
        
        return {
            'id': self.job_id,
            'type': self.job_type,
            'size': self.size,
            'gpu_count': self.gpu_count,
            'vram_per_gpu': self.vram_per_gpu,
            'base_payout': self.base_payout,
            'progress': self.progress,
            'started': self.started_at is not None,
            'sla_missed': self.is_sla_missed(),
            'assigned_gpus': [g.gpu_id for g in self.assigned_gpus],
            'customer_name': self.customer_name,
            'task_description': self.task_description,
            'is_multi_gpu': self.is_multi_gpu,
            'is_syncing': is_syncing,
            'gpu_coordination': gpu_coordination,
            'performance_multiplier': round(self.performance_multiplier, 2)
        }


class JobGenerator:
    """Generates jobs based on game progression"""
    
    @staticmethod
    def generate_job(total_revenue, value_multiplier=1.0, sla_extension=0, available_gpu_count=1):
        """Generate a random job appropriate for current phase
        
        Args:
            total_revenue: Total revenue earned (determines phase)
            value_multiplier: Multiplier for job payouts (from marketing)
            sla_extension: Additional seconds added to SLA window (from marketing)
            available_gpu_count: Number of available GPUs (affects job size distribution)
        """
        
        # Adaptive job sizing based on GPU count to avoid queue blockage
        # This ensures we generate jobs that can actually run on current infrastructure
        
        # Phase 1 (0-30K): Mix of small and medium jobs
        if total_revenue < 30000:
            # Early game: mostly small jobs, some medium to encourage GPU purchases
            if available_gpu_count < 2:
                return JobGenerator._create_inference_job(value_multiplier, sla_extension)
            else:
                # 70% small, 30% medium once you have 2+ GPUs
                if random.random() < 0.7:
                    return JobGenerator._create_inference_job(value_multiplier, sla_extension)
                else:
                    return JobGenerator._create_medium_job(value_multiplier, sla_extension)
        
        # Phase 2 (30K-150K): Introduce large jobs when infrastructure supports it
        elif total_revenue < 150000:
            if available_gpu_count < 2:
                # Only small jobs if limited GPUs
                return JobGenerator._create_inference_job(value_multiplier, sla_extension)
            elif available_gpu_count < 4:
                # 60% small, 40% medium - no large jobs yet
                if random.random() < 0.6:
                    return JobGenerator._create_inference_job(value_multiplier, sla_extension)
                else:
                    return JobGenerator._create_medium_job(value_multiplier, sla_extension)
            else:
                # 50% small, 30% medium, 20% large - full mix
                roll = random.random()
                if roll < 0.5:
                    return JobGenerator._create_inference_job(value_multiplier, sla_extension)
                elif roll < 0.8:
                    return JobGenerator._create_medium_job(value_multiplier, sla_extension)
                else:
                    return JobGenerator._create_training_job(value_multiplier, sla_extension)
        
        # Phase 3 (150K+): More large jobs, but still balanced
        else:
            if available_gpu_count < 2:
                return JobGenerator._create_inference_job(value_multiplier, sla_extension)
            elif available_gpu_count < 4:
                # 50% small, 50% medium
                if random.random() < 0.5:
                    return JobGenerator._create_inference_job(value_multiplier, sla_extension)
                else:
                    return JobGenerator._create_medium_job(value_multiplier, sla_extension)
            else:
                # 30% small, 30% medium, 40% large - favor large jobs
                roll = random.random()
                if roll < 0.3:
                    return JobGenerator._create_inference_job(value_multiplier, sla_extension)
                elif roll < 0.6:
                    return JobGenerator._create_medium_job(value_multiplier, sla_extension)
                else:
                    return JobGenerator._create_training_job(value_multiplier, sla_extension)
    
    @staticmethod
    def _create_inference_job(value_multiplier=1.0, sla_extension=0):
        """Small (1 GPU), short, latency-sensitive"""
        customer = random.choice(INFERENCE_CUSTOMERS)
        return Job(
            job_type='inference',
            base_duration=5,  # Faster for better visual feedback (was 8)
            vram_per_gpu=16,  # Modest VRAM needs
            base_payout=int(45 * value_multiplier),   # Slightly lower to balance faster completion
            sla_window=20 + sla_extension,    # Tight SLA + marketing extension
            gpu_count=1,
            customer_name=customer,
            task_description=CUSTOMER_TASKS[customer]
        )
    
    @staticmethod
    def _create_medium_job(value_multiplier=1.0, sla_extension=0):
        """Medium (2 GPUs), medium duration - the sweet spot for mid-game"""
        # Mix of inference and training customers for medium jobs
        if random.random() < 0.5:
            customer = random.choice(INFERENCE_CUSTOMERS)
            task_type = 'inference'
        else:
            customer = random.choice(TRAINING_CUSTOMERS)
            task_type = 'training'
        
        return Job(
            job_type=task_type,
            base_duration=12,  # Medium duration
            vram_per_gpu=32,   # Medium VRAM needs
            base_payout=int(120 * value_multiplier),   # ~2.6x per GPU vs small jobs
            sla_window=35 + sla_extension,    # Medium SLA
            gpu_count=2,
            customer_name=customer,
            task_description=CUSTOMER_TASKS[customer]
        )
    
    @staticmethod
    def _create_training_job(value_multiplier=1.0, sla_extension=0):
        """Large (4 GPUs), long, high VRAM"""
        customer = random.choice(TRAINING_CUSTOMERS)
        return Job(
            job_type='training',
            base_duration=20,  # Shorter for better pacing (was 25)
            vram_per_gpu=50,   # High VRAM needs
            base_payout=int(220 * value_multiplier),   # ~2.4x per GPU vs medium
            sla_window=50 + sla_extension,    # More relaxed SLA
            gpu_count=4,
            customer_name=customer,
            task_description=CUSTOMER_TASKS[customer]
        )


class Scheduler:
    """Simple FIFO job scheduler"""
    
    @staticmethod
    def schedule_fifo(job_queue, gpus, network_penalty=0.25):
        """First In First Out - simplest scheduler"""
        for job in job_queue:
            if Scheduler._try_place_job(job, gpus, network_penalty):
                return True
        return False
    
    @staticmethod
    def _try_place_job(job, gpus, network_penalty=0.25):
        """Try to place a job on available GPUs with enough VRAM"""
        available_gpus = [g for g in gpus if g.is_available() and g.vram >= job.vram_per_gpu]
        
        if len(available_gpus) >= job.gpu_count:
            # Assign job to GPUs
            assigned = available_gpus[:job.gpu_count]
            
            # Calculate cross-node penalty (simplified: assume penalty if not all same type)
            cross_node_penalty = 0.0
            if job.gpu_count > 1 and len(set(g.gpu_type for g in assigned)) > 1:
                cross_node_penalty = network_penalty
            
            job.start(assigned, cross_node_penalty)
            for gpu in assigned:
                gpu.assign_job(job)
            
            return True
        
        return False

