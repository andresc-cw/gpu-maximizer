"""Enterprise contract system"""
import time

# Contract definitions for enterprise GPU deals
CONTRACTS_CATALOG = {
    'openai_spot': {
        'id': 'openai_spot',
        'name': 'NeuralCore Research',
        'title': 'Spot Capacity Reserve',
        'description': 'Reserved spot capacity for inference bursts',
        'customer_logo': '🔷',
        'requires': {
            'min_gpus': 20,
            'min_h100s': 10,
            'network': None,
            'min_revenue': 50000
        },
        'reserves_gpus': 20,
        'monthly_income': 8000,
        'negotiation_cost_total': 15000,  # Total cost to complete negotiation
        'duration_months': 3,
        'negotiation_time': 30,  # seconds of real time to negotiate
        'priority': 1
    },
    'meta_llama': {
        'id': 'meta_llama',
        'name': 'PersonalAI Labs',
        'title': 'LLM Training Cluster',
        'description': 'Dedicated cluster for next-gen LLM training',
        'customer_logo': '🟦',
        'requires': {
            'min_gpus': 50,
            'min_h100s': 40,
            'network': 'infiniband',
            'min_revenue': 200000
        },
        'reserves_gpus': 50,
        'monthly_income': 35000,
        'negotiation_cost_total': 40000,
        'duration_months': 6,
        'negotiation_time': 60,
        'priority': 2
    },
    'microsoft_azure': {
        'id': 'microsoft_azure',
        'name': 'CloudAI Systems',
        'title': 'Overflow Capacity Reserve',
        'description': 'Emergency overflow for enterprise AI services',
        'customer_logo': '🔶',
        'requires': {
            'min_gpus': 100,
            'min_h100s': 80,
            'network': 'infiniband',
            'cooling': 'liquid',
            'min_revenue': 500000
        },
        'reserves_gpus': 100,
        'monthly_income': 95000,
        'negotiation_cost_total': 100000,
        'duration_months': 12,
        'negotiation_time': 120,
        'priority': 3
    },
    'anthropic_claude': {
        'id': 'anthropic_claude',
        'name': 'SafetyFirst AI',
        'title': 'LLM Training Reserve',
        'description': 'Long-term reserved capacity for large model development',
        'customer_logo': '🟪',
        'requires': {
            'min_gpus': 150,
            'min_h100s': 120,
            'network': 'nvlink_fabric',
            'cooling': 'liquid',
            'min_revenue': 1000000
        },
        'reserves_gpus': 150,
        'monthly_income': 180000,
        'negotiation_cost_total': 200000,
        'duration_months': 18,
        'negotiation_time': 180,
        'priority': 4
    }
}


class Contract:
    """Represents an enterprise contract"""
    
    def __init__(self, contract_id):
        if contract_id not in CONTRACTS_CATALOG:
            raise ValueError(f"Unknown contract: {contract_id}")
        
        spec = CONTRACTS_CATALOG[contract_id]
        self.id = contract_id
        self.name = spec['name']
        self.title = spec['title']
        self.description = spec['description']
        self.customer_logo = spec['customer_logo']
        self.requires = spec['requires']
        self.reserves_gpus = spec['reserves_gpus']
        self.monthly_income = spec['monthly_income']
        self.negotiation_cost_total = spec['negotiation_cost_total']
        self.duration_months = spec['duration_months']
        self.negotiation_time = spec['negotiation_time']
        self.priority = spec['priority']
        
        # State
        self.status = 'available'  # available, negotiating, active, expired
        self.negotiation_progress = 0.0  # 0.0 to 1.0
        self.money_invested = 0
        self.negotiation_start_time = None
        self.activation_time = None
        self.months_remaining = spec['duration_months']
        
        # Reserved GPUs (will be filled when contract activates)
        self.reserved_gpu_ids = []
    
    def start_negotiation(self):
        """Begin contract negotiation"""
        if self.status != 'available':
            return False, "Contract not available"
        
        self.status = 'negotiating'
        self.negotiation_start_time = time.time()
        self.negotiation_progress = 0.0
        self.money_invested = 0
        return True, f"Started negotiating with {self.name}"
    
    def invest_in_negotiation(self, amount):
        """Invest money to advance negotiation"""
        if self.status != 'negotiating':
            return False, "Contract not in negotiation"
        
        self.money_invested += amount
        # Progress is based on money invested
        self.negotiation_progress = min(1.0, self.money_invested / self.negotiation_cost_total)
        
        return True, f"Invested ${amount:,} in {self.name} deal"
    
    def can_activate(self):
        """Check if contract can be activated (negotiation complete)"""
        return self.status == 'negotiating' and self.negotiation_progress >= 1.0
    
    def activate(self, gpu_ids):
        """Activate the contract and reserve GPUs"""
        if not self.can_activate():
            return False, "Negotiation not complete"
        
        if len(gpu_ids) != self.reserves_gpus:
            return False, f"Need exactly {self.reserves_gpus} GPUs to reserve"
        
        self.status = 'active'
        self.activation_time = time.time()
        self.reserved_gpu_ids = gpu_ids[:]
        self.months_remaining = self.duration_months
        return True, f"{self.name} contract activated!"
    
    def update(self, dt):
        """Update contract state (for active contracts)"""
        if self.status == 'active':
            # Calculate passive income per tick
            # monthly_income / (30 days * 24 hours * 3600 seconds) * dt
            income_per_second = self.monthly_income / (30 * 24 * 3600)
            return income_per_second * dt
        return 0.0
    
    def check_requirements(self, game_state):
        """Check if player meets contract requirements"""
        reqs = self.requires
        issues = []
        
        # Check minimum GPUs
        total_gpus = len(game_state.gpus)
        if total_gpus < reqs['min_gpus']:
            issues.append(f"Need {reqs['min_gpus']} GPUs (have {total_gpus})")
        
        # Check H100 count
        if 'min_h100s' in reqs:
            # H100+ includes: H100, GB200 (simplified GPU lineup)
            h100_count = sum(1 for gpu in game_state.gpus if gpu.gpu_type in ['H100', 'GB200'])
            if h100_count < reqs['min_h100s']:
                issues.append(f"Need {reqs['min_h100s']} H100+ GPUs (have {h100_count})")
        
        # Check network tier (now auto-managed based on GPU count)
        if reqs.get('network'):
            # Map old network requirements to GPU count thresholds
            network_gpu_requirements = {
                'infiniband': 13,  # Need 13+ GPUs for NVLink/InfiniBand tier
                'nvlink_fabric': 25  # Need 25+ GPUs for fabric tier
            }
            min_gpus = network_gpu_requirements.get(reqs['network'], 0)
            if len(game_state.gpus) < min_gpus:
                issues.append(f"Need {min_gpus}+ GPUs for {reqs['network']} networking (auto-unlocks)")
        
        # Check cooling tier (now auto-managed based on GPU types)
        if reqs.get('cooling'):
            from .economy import Economy
            current_cooling = Economy.get_current_cooling_tier(game_state.gpus)
            cooling_hierarchy = {'air': 0, 'liquid': 1, 'advanced_liquid': 2}
            required_level = cooling_hierarchy.get(reqs['cooling'], 0)
            current_level = cooling_hierarchy.get(current_cooling, 0)
            if current_level < required_level:
                issues.append(f"Need {reqs['cooling']} cooling (buy GPUs that require it)")
        
        # Check revenue
        if game_state.total_revenue < reqs['min_revenue']:
            issues.append(f"Need ${reqs['min_revenue']:,} total revenue")
        
        return len(issues) == 0, issues
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'customer_logo': self.customer_logo,
            'requires': self.requires,
            'reserves_gpus': self.reserves_gpus,
            'monthly_income': self.monthly_income,
            'negotiation_cost_total': self.negotiation_cost_total,
            'duration_months': self.duration_months,
            'status': self.status,
            'negotiation_progress': round(self.negotiation_progress * 100, 1),
            'money_invested': self.money_invested,
            'months_remaining': self.months_remaining,
            'reserved_gpu_ids': self.reserved_gpu_ids,
            'priority': self.priority
        }


class ContractManager:
    """Manages all contracts"""
    
    def __init__(self):
        self.contracts = {}
        self.initialize_contracts()
    
    def initialize_contracts(self):
        """Initialize all available contracts"""
        for contract_id in CONTRACTS_CATALOG.keys():
            self.contracts[contract_id] = Contract(contract_id)
    
    def get_available_contracts(self, game_state):
        """Get contracts that player is eligible for"""
        available = []
        for contract in self.contracts.values():
            if contract.status == 'available':
                meets_reqs, issues = contract.check_requirements(game_state)
                available.append({
                    'contract': contract,
                    'eligible': meets_reqs,
                    'issues': issues
                })
        return sorted(available, key=lambda x: x['contract'].priority)
    
    def get_active_contracts(self):
        """Get all active contracts"""
        return [c for c in self.contracts.values() if c.status == 'active']
    
    def get_negotiating_contracts(self):
        """Get contracts currently being negotiated"""
        return [c for c in self.contracts.values() if c.status == 'negotiating']
    
    def get_total_reserved_gpus(self):
        """Get total number of GPUs reserved by contracts"""
        return sum(len(c.reserved_gpu_ids) for c in self.get_active_contracts())
    
    def get_total_monthly_income(self):
        """Get total monthly income from all active contracts"""
        return sum(c.monthly_income for c in self.get_active_contracts())
    
    def update(self, dt):
        """Update all contracts and return total passive income for this tick"""
        total_income = 0.0
        for contract in self.get_active_contracts():
            total_income += contract.update(dt)
        return total_income
    
    def to_dict(self, game_state):
        """Convert manager state to dictionary"""
        available = self.get_available_contracts(game_state)
        
        return {
            'available': [
                {
                    'contract': a['contract'].to_dict(),
                    'eligible': a['eligible'],
                    'issues': a['issues']
                }
                for a in available
            ],
            'active': [c.to_dict() for c in self.get_active_contracts()],
            'negotiating': [c.to_dict() for c in self.get_negotiating_contracts()],
            'total_reserved_gpus': self.get_total_reserved_gpus(),
            'total_monthly_income': self.get_total_monthly_income()
        }

