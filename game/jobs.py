"""Job generation and scheduling system"""
import random
import time

# Realistic CoreWeave customers by job type
INFERENCE_CUSTOMERS = [
    'Perplexity AI',
    'Character.AI',
    'Runway ML',
    'Hugging Face',
    'ElevenLabs',
    'Stability AI'
]

TRAINING_CUSTOMERS = [
    'Anthropic',
    'Cohere',
    'Waymo',
    'Midjourney',
    'Adept AI',
    'Inflection AI',
    'OpenAI',
    'DeepMind'
]

# Task descriptions for each customer
CUSTOMER_TASKS = {
    # Inference customers
    'Perplexity AI': 'Search Query Processing',
    'Character.AI': 'Conversational Inference',
    'Runway ML': 'Video Generation',
    'Hugging Face': 'Model API Inference',
    'ElevenLabs': 'Voice Synthesis',
    'Stability AI': 'Image Generation',
    
    # Training customers
    'Anthropic': 'Claude Model Training',
    'Cohere': 'LLM Fine-tuning',
    'Waymo': 'Perception Model Training',
    'Midjourney': 'Diffusion Model Training',
    'Adept AI': 'Action Transformer Training',
    'Inflection AI': 'Large-scale Pretraining',
    'OpenAI': 'Foundation Model Training',
    'DeepMind': 'Multi-modal Training'
}

class Job:
    """Represents a compute job"""
    _next_id = 1
    
    def __init__(self, job_type, base_duration, vram_per_gpu, base_payout, sla_window, gpu_count, customer_name, task_description):
        self.job_id = Job._next_id
        Job._next_id += 1
        
        self.job_type = job_type  # 'inference' or 'training'
        self.size = 'S' if gpu_count == 1 else 'L'  # Small (1 GPU) or Large (4 GPUs)
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
    
    def start(self, gpus, cross_node_penalty=0.0):
        """Start job on assigned GPUs"""
        self.started_at = time.time()
        self.assigned_gpus = gpus
        self.cross_node_penalty = cross_node_penalty
        
        # Apply performance multiplier from GPUs
        if gpus:
            avg_performance = sum(g.performance for g in gpus) / len(gpus)
            self.duration = self.base_duration / avg_performance
        
        # Apply cross-node penalty
        self.duration = self.duration * (1 + cross_node_penalty)
    
    def update(self, dt):
        """Update job progress, returns True if completed"""
        if self.started_at is None:
            return False
        
        self.progress += dt / self.duration
        
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
            'task_description': self.task_description
        }


class JobGenerator:
    """Generates jobs based on game progression"""
    
    @staticmethod
    def generate_job(total_revenue, value_multiplier=1.0, sla_extension=0):
        """Generate a random job appropriate for current phase
        
        Args:
            total_revenue: Total revenue earned (determines phase)
            value_multiplier: Multiplier for job payouts (from marketing)
            sla_extension: Additional seconds added to SLA window (from marketing)
        """
        
        # Phase 1 (0-30K): Only inference jobs (small, fast)
        if total_revenue < 30000:
            return JobGenerator._create_inference_job(value_multiplier, sla_extension)
        
        # Phase 2 (30K-150K): Mostly inference, some training
        elif total_revenue < 150000:
            if random.random() < 0.75:
                return JobGenerator._create_inference_job(value_multiplier, sla_extension)
            else:
                return JobGenerator._create_training_job(value_multiplier, sla_extension)
        
        # Phase 3 (150K+): Balanced mix favoring training
        else:
            if random.random() < 0.4:
                return JobGenerator._create_inference_job(value_multiplier, sla_extension)
            else:
                return JobGenerator._create_training_job(value_multiplier, sla_extension)
    
    @staticmethod
    def _create_inference_job(value_multiplier=1.0, sla_extension=0):
        """Small (1 GPU), short, latency-sensitive"""
        customer = random.choice(INFERENCE_CUSTOMERS)
        return Job(
            job_type='inference',
            base_duration=8,  # Fast jobs
            vram_per_gpu=16,  # Modest VRAM needs
            base_payout=int(50 * value_multiplier),   # Apply marketing multiplier
            sla_window=20 + sla_extension,    # Tight SLA + marketing extension
            gpu_count=1,
            customer_name=customer,
            task_description=CUSTOMER_TASKS[customer]
        )
    
    @staticmethod
    def _create_training_job(value_multiplier=1.0, sla_extension=0):
        """Large (4 GPUs), long, high VRAM"""
        customer = random.choice(TRAINING_CUSTOMERS)
        return Job(
            job_type='training',
            base_duration=25,  # Longer jobs
            vram_per_gpu=50,   # High VRAM needs
            base_payout=int(250 * value_multiplier),   # Apply marketing multiplier
            sla_window=50 + sla_extension,    # More relaxed SLA
            gpu_count=4,
            customer_name=customer,
            task_description=CUSTOMER_TASKS[customer]
        )


class Scheduler:
    """Simple FIFO job scheduler"""
    
    @staticmethod
    def schedule_fifo(job_queue, gpus):
        """First In First Out - simplest scheduler"""
        for job in job_queue:
            if Scheduler._try_place_job(job, gpus):
                return True
        return False
    
    @staticmethod
    def _try_place_job(job, gpus):
        """Try to place a job on available GPUs with enough VRAM"""
        available_gpus = [g for g in gpus if g.is_available() and g.vram >= job.vram_per_gpu]
        
        if len(available_gpus) >= job.gpu_count:
            # Assign job to GPUs
            assigned = available_gpus[:job.gpu_count]
            
            # Calculate cross-node penalty (simplified: assume penalty if not all same type)
            cross_node_penalty = 0.0
            if job.gpu_count > 1 and len(set(g.gpu_type for g in assigned)) > 1:
                cross_node_penalty = 0.25  # Base penalty, will be modified by network upgrades
            
            job.start(assigned, cross_node_penalty)
            for gpu in assigned:
                gpu.assign_job(job)
            
            return True
        
        return False

