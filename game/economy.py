"""Economy and progression system"""

# Cooling tiers - AUTO-ASSIGNED based on GPU purchases
# No longer purchasable separately - costs bundled into GPU prices
COOLING_TIERS = {
    'air': {
        'name': 'Air Cooling',
        'pue': 1.45,
        'description': 'Basic air cooling for low-power GPUs (L4)'
    },
    'liquid': {
        'name': 'Liquid Cooling',
        'pue': 1.28,
        'description': 'Liquid cooling for high-performance GPUs (A100, H100)'
    },
    'advanced_liquid': {
        'name': 'Advanced Liquid Cooling',
        'pue': 1.22,
        'description': 'Advanced cooling for extreme GPUs (GB200)'
    }
}

# Scheduler tiers - AUTO-UPGRADE at revenue milestones
# No longer purchasable separately
SCHEDULER_TIERS = {
    'fifo': {
        'name': 'FIFO',
        'unlock_revenue': 0,
        'description': 'First In First Out scheduling'
    },
    'priority': {
        'name': 'Priority Queue',
        'unlock_revenue': 50000,
        'description': 'Auto-unlocked at $50K. Prioritizes urgent jobs for better SLA compliance.'
    },
    'backfill': {
        'name': 'Backfill',
        'unlock_revenue': 150000,
        'description': 'Auto-unlocked at $150K. Fills idle GPU gaps while reserving space for large jobs.'
    },
    'preemptive': {
        'name': 'Preemptive',
        'unlock_revenue': 400000,
        'description': 'Auto-unlocked at $400K. Can pause low-priority jobs for urgent work.'
    }
}

# Network performance - AUTO-IMPROVES with GPU count
# No longer purchasable separately
def get_network_penalty(gpu_count):
    """Returns cross-node job penalty based on cluster size
    
    As you scale, networking automatically improves:
    - 1-4 GPUs: Basic Ethernet (25% penalty)
    - 5-12 GPUs: 10GbE (15% penalty)
    - 13-24 GPUs: NVLink (8% penalty)
    - 25+ GPUs: InfiniBand/Fabric (3% penalty)
    """
    if gpu_count <= 4:
        return 0.25  # Basic Ethernet
    elif gpu_count <= 12:
        return 0.15  # 10 Gigabit Ethernet
    elif gpu_count <= 24:
        return 0.08  # NVLink
    else:
        return 0.03  # InfiniBand / NVLink Fabric

class Economy:
    """Handles economy calculations and unlocks"""
    
    @staticmethod
    def calculate_power_cost(gpus, pue, dt):
        """Calculate electricity cost for time period dt (seconds)"""
        # Power cost formula: (Σ GPU TDP × utilization / 1000) × PUE × $0.15 / 3600
        total_watts = sum(gpu.tdp * gpu.utilization for gpu in gpus)
        kw = total_watts / 1000.0
        facility_kw = kw * pue
        
        # $0.15 per kWh, convert dt to hours
        cost_per_second = facility_kw * 0.15 / 3600.0
        return cost_per_second * dt
    
    @staticmethod
    def get_current_cooling_tier(gpus):
        """Auto-determine cooling tier based on GPU inventory"""
        if not gpus:
            return 'air'
        
        # Find highest cooling tier needed
        from .gpus import GPU_CATALOG
        max_tier = 'air'
        
        for gpu in gpus:
            gpu_tier = GPU_CATALOG[gpu.gpu_type]['cooling_tier']
            if gpu_tier == 'advanced_liquid':
                max_tier = 'advanced_liquid'
            elif gpu_tier == 'liquid' and max_tier != 'advanced_liquid':
                max_tier = 'liquid'
        
        return max_tier
    
    @staticmethod
    def get_current_pue(gpus):
        """Get current PUE based on cooling tier"""
        cooling_tier = Economy.get_current_cooling_tier(gpus)
        return COOLING_TIERS[cooling_tier]['pue']
    
    @staticmethod
    def get_current_scheduler(total_revenue):
        """Auto-determine current scheduler based on revenue"""
        if total_revenue >= 400000:
            return 'preemptive'
        elif total_revenue >= 150000:
            return 'backfill'
        elif total_revenue >= 50000:
            return 'priority'
        else:
            return 'fifo'
    
    @staticmethod
    def get_unlocked_gpus(total_revenue):
        """Return list of GPU types that are unlocked based on revenue"""
        from .gpus import GPU_CATALOG
        
        unlocked = []
        for gpu_type, spec in GPU_CATALOG.items():
            if total_revenue >= spec['unlock_revenue']:
                unlocked.append(gpu_type)
        
        return unlocked
    
    @staticmethod
    def can_purchase(item_type, item_id, cash, total_revenue):
        """Check if player can purchase an item"""
        if item_type == 'gpu':
            from .gpus import GPU_CATALOG
            if item_id not in GPU_CATALOG:
                return False, "GPU type not found"
            
            spec = GPU_CATALOG[item_id]
            if cash < spec['cost']:
                return False, f"Need ${spec['cost']:,}"
            
            if total_revenue < spec['unlock_revenue']:
                return False, f"Unlock at ${spec['unlock_revenue']:,} revenue"
            
            return True, ""
        
        return False, "Unknown item type"

