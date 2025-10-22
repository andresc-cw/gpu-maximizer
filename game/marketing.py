"""Marketing and sales system - improves job queue quality and quantity"""

# Marketing levels inspired by CoreWeave's actual marketing evolution
# Each level represents a realistic stage in cloud GPU provider marketing
MARKETING_LEVELS = [
    {
        'level': 0,
        'name': 'No Marketing',
        'description': 'Relying on organic discovery. Jobs trickle in slowly.',
        'job_spawn_multiplier': 1.0,
        'job_value_multiplier': 1.0
    },
    {
        'level': 1,
        'name': 'Twitter Account',
        'description': 'Created @YourGPUCloud. Tweeting about GPU availability. Some techies notice.',
        'cost': 2000,
        'unlock_revenue': 5000,
        'job_spawn_multiplier': 1.15,
        'job_value_multiplier': 1.0
    },
    {
        'level': 2,
        'name': 'HackerNews Post',
        'description': '"Show HN: GPU cloud for $X/hr" hits front page. Traffic spike incoming.',
        'cost': 5000,
        'unlock_revenue': 15000,
        'job_spawn_multiplier': 1.3,
        'job_value_multiplier': 1.1
    },
    {
        'level': 3,
        'name': 'Technical Blog',
        'description': 'Publishing GPU benchmarks & ML tutorials. SEO starting to work.',
        'cost': 8000,
        'unlock_revenue': 30000,
        'job_spawn_multiplier': 1.45,
        'job_value_multiplier': 1.15
    },
    {
        'level': 4,
        'name': 'Discord Community',
        'description': 'Built active Discord with 500+ ML engineers. Word-of-mouth growth.',
        'cost': 12000,
        'unlock_revenue': 50000,
        'job_spawn_multiplier': 1.6,
        'job_value_multiplier': 1.2
    },
    {
        'level': 5,
        'name': 'NeurIPS Booth',
        'description': 'Sponsored ML conference. Giving out GPU credits at booth. Meeting researchers.',
        'cost': 20000,
        'unlock_revenue': 80000,
        'job_spawn_multiplier': 1.75,
        'job_value_multiplier': 1.3
    },
    {
        'level': 6,
        'name': 'Hugging Face Integration',
        'description': 'Official integration with Hugging Face. Direct pipeline from their platform.',
        'cost': 30000,
        'unlock_revenue': 120000,
        'job_spawn_multiplier': 2.0,
        'job_value_multiplier': 1.4
    },
    {
        'level': 7,
        'name': 'First Sales Hire',
        'description': 'Hired AE ($120K/yr + commission). Actively cold-calling AI startups.',
        'cost': 40000,
        'unlock_revenue': 180000,
        'job_spawn_multiplier': 2.2,
        'job_value_multiplier': 1.5
    },
    {
        'level': 8,
        'name': 'Case Studies',
        'description': 'Published customer success stories. "How Anthropic trained Claude on our H100s."',
        'cost': 50000,
        'unlock_revenue': 250000,
        'job_spawn_multiplier': 2.4,
        'job_value_multiplier': 1.65
    },
    {
        'level': 9,
        'name': 'Enterprise Outreach',
        'description': 'Targeting Fortune 500. Direct line to Meta, OpenAI, Stability AI.',
        'cost': 75000,
        'unlock_revenue': 350000,
        'job_spawn_multiplier': 2.7,
        'job_value_multiplier': 1.85
    },
    {
        'level': 10,
        'name': 'Sales Team (5 AEs)',
        'description': 'Full sales org with SDRs, AEs, and SEs. Predictable pipeline.',
        'cost': 100000,
        'unlock_revenue': 500000,
        'job_spawn_multiplier': 3.0,
        'job_value_multiplier': 2.1
    },
    {
        'level': 11,
        'name': 'Customer Success Team',
        'description': 'Dedicated CSMs ensuring retention. Upselling existing accounts. +10s SLA buffer.',
        'cost': 120000,
        'unlock_revenue': 700000,
        'job_spawn_multiplier': 3.2,
        'job_value_multiplier': 2.3,
        'sla_extension': 10
    },
    {
        'level': 12,
        'name': 'Gartner Magic Quadrant',
        'description': 'Featured in analyst reports. Enterprise buyers finding you via research.',
        'cost': 150000,
        'unlock_revenue': 1000000,
        'job_spawn_multiplier': 3.5,
        'job_value_multiplier': 2.6
    },
    {
        'level': 13,
        'name': 'Platform Partnerships',
        'description': 'Integrated with Jupyter, VSCode, major ML tools. Embedded in workflows.',
        'cost': 200000,
        'unlock_revenue': 1400000,
        'job_spawn_multiplier': 3.9,
        'job_value_multiplier': 2.9
    },
    {
        'level': 14,
        'name': 'Brand Recognition',
        'description': 'Mentioned in TechCrunch, Wired. "The CoreWeave of X" comparisons.',
        'cost': 250000,
        'unlock_revenue': 2000000,
        'job_spawn_multiplier': 4.3,
        'job_value_multiplier': 3.3
    },
    {
        'level': 15,
        'name': 'Market Leader',
        'description': 'Industry standard for GPU cloud. Inbound leads flooding sales. Waitlist for H100s.',
        'cost': 350000,
        'unlock_revenue': 3000000,
        'job_spawn_multiplier': 5.0,
        'job_value_multiplier': 4.0,
        'sla_extension': 20
    }
]

class MarketingManager:
    """Manages marketing level progression (Universal Paperclips style)"""
    
    def __init__(self):
        self.level = 0  # Start at level 0 (no marketing)
    
    def can_upgrade(self, cash, total_revenue):
        """Check if player can upgrade to next marketing level"""
        if self.level >= len(MARKETING_LEVELS) - 1:
            return False, "Max marketing level reached"
        
        next_level_data = MARKETING_LEVELS[self.level + 1]
        
        if total_revenue < next_level_data['unlock_revenue']:
            return False, f"Unlock at ${next_level_data['unlock_revenue']:,} total revenue"
        
        if cash < next_level_data['cost']:
            return False, f"Need ${next_level_data['cost']:,}"
        
        return True, "Can upgrade"
    
    def upgrade(self, cash, total_revenue):
        """Attempt to upgrade marketing level"""
        can_upgrade, message = self.can_upgrade(cash, total_revenue)
        
        if not can_upgrade:
            return False, message
        
        next_level_data = MARKETING_LEVELS[self.level + 1]
        self.level += 1
        
        return True, f"Marketing upgraded: {next_level_data['name']}"
    
    def get_current_level_data(self):
        """Get data for current marketing level"""
        return MARKETING_LEVELS[self.level]
    
    def get_next_level_data(self):
        """Get data for next marketing level (or None if maxed)"""
        if self.level >= len(MARKETING_LEVELS) - 1:
            return None
        return MARKETING_LEVELS[self.level + 1]
    
    def get_job_spawn_multiplier(self):
        """Get current job spawn rate multiplier"""
        return MARKETING_LEVELS[self.level]['job_spawn_multiplier']
    
    def get_job_value_multiplier(self):
        """Get current job value multiplier"""
        return MARKETING_LEVELS[self.level]['job_value_multiplier']
    
    def get_sla_extension(self):
        """Get current SLA window extension in seconds"""
        current = MARKETING_LEVELS[self.level]
        return current.get('sla_extension', 0)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        current = self.get_current_level_data()
        next_level = self.get_next_level_data()
        
        return {
            'level': self.level,
            'current': current,
            'next': next_level,
            'job_spawn_multiplier': round(self.get_job_spawn_multiplier(), 2),
            'job_value_multiplier': round(self.get_job_value_multiplier(), 2),
            'sla_extension': self.get_sla_extension()
        }
