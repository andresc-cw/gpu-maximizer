"""GPU specifications and management"""
import random

class GPU:
    """Represents a single GPU instance"""
    def __init__(self, gpu_type, gpu_id):
        self.gpu_id = gpu_id
        self.gpu_type = gpu_type
        spec = GPU_CATALOG[gpu_type]
        self.name = spec['name']
        self.vram = spec['vram']
        self.tdp = spec['tdp']
        self.performance = spec['performance']
        self.cost = spec['cost']
        
        # Runtime state
        self.current_job = None
        self.utilization = 0.0
        self.vram_used = 0
    
    def is_available(self):
        return self.current_job is None
    
    def assign_job(self, job):
        self.current_job = job
        self.vram_used = job.vram_per_gpu
        self.utilization = 1.0
    
    def clear_job(self):
        self.current_job = None
        self.vram_used = 0
        self.utilization = 0.0
    
    def to_dict(self):
        return {
            'id': self.gpu_id,
            'type': self.gpu_type,
            'name': self.name,
            'vram': self.vram,
            'vram_used': self.vram_used,
            'tdp': self.tdp,
            'utilization': self.utilization,
            'current_job': self.current_job.job_id if self.current_job else None
        }


# GPU Catalog - Simplified to 4 core tiers
# Cooling costs are auto-bundled into GPU prices
GPU_CATALOG = {
    'L4': {
        'name': 'NVIDIA L4',
        'vram': 24,
        'tdp': 72,
        'performance': 1.0,
        'cost': 3000,
        'unlock_revenue': 0,
        'cooling_tier': 'air',
        'description': 'Your desk GPU. Ada Lovelace architecture optimized for AI inference. 72W TDP enables air cooling. Perfect starter GPU for inference workloads.'
    },
    'A100': {
        'name': 'NVIDIA A100',
        'vram': 80,
        'tdp': 300,
        'performance': 4.0,
        'cost': 18000,  # Includes liquid cooling costs (+$6K bundled)
        'unlock_revenue': 30000,
        'cooling_tier': 'liquid',
        'description': 'First pro GPU. Ampere architecture with 80GB HBM2e memory. Multi-Instance GPU support. Liquid cooling included. Great for training and high-throughput inference.'
    },
    'H100': {
        'name': 'NVIDIA H100 SXM',
        'vram': 80,
        'tdp': 700,
        'performance': 10.0,
        'cost': 40000,  # Includes liquid cooling costs (+$15K bundled)
        'unlock_revenue': 150000,
        'cooling_tier': 'liquid',
        'description': 'AI training beast. Hopper architecture with Transformer Engine and FP8 precision. 9x faster training for LLMs. NVLink Gen 4 for multi-GPU workloads.'
    },
    'GB200': {
        'name': 'NVIDIA GB200',
        'vram': 192,
        'tdp': 1200,
        'performance': 30.0,
        'cost': 120000,  # Includes advanced cooling costs (+$50K bundled)
        'unlock_revenue': 500000,
        'cooling_tier': 'advanced_liquid',
        'description': 'Endgame superchip. Grace Blackwell with 72-core ARM CPU + Blackwell GPU. 672GB unified memory. For trillion-parameter models. Advanced cooling included.'
    }
}

