"""Achievement and Victory system definitions"""

ACHIEVEMENTS = {
    'gpu_10': {
        'name': 'Small Cluster',
        'description': 'Own 10 GPUs',
        'icon': '🖥️'
    },
    'gpu_50': {
        'name': 'Medium Datacenter',
        'description': 'Own 50 GPUs',
        'icon': '🏢'
    },
    'gpu_100': {
        'name': 'Large Scale Infrastructure',
        'description': 'Own 100 GPUs',
        'icon': '🏭'
    },
    'revenue_100k': {
        'name': 'First $100K',
        'description': 'Earn $100,000 total revenue',
        'icon': '💰'
    },
    'revenue_500k': {
        'name': 'Half Million',
        'description': 'Earn $500,000 total revenue',
        'icon': '💵'
    },
    'revenue_1m': {
        'name': 'Millionaire',
        'description': 'Earn $1,000,000 total revenue',
        'icon': '💎'
    },
    'sla_champion': {
        'name': 'SLA Champion',
        'description': '95%+ SLA compliance over 100 jobs',
        'icon': '🏆'
    },
    'efficiency_expert': {
        'name': 'Efficiency Expert',
        'description': '85%+ utilization with 20+ GPUs',
        'icon': '⚡'
    },
    'green_datacenter': {
        'name': 'Green Datacenter',
        'description': 'Achieve PUE of 1.25 or lower',
        'icon': '🌱'
    },
    'enterprise_player': {
        'name': 'Enterprise Player',
        'description': 'Have 2+ active contracts',
        'icon': '🤝'
    }
}

VICTORY_CONDITIONS = {
    'revenue_tycoon': {
        'name': 'Revenue Tycoon',
        'description': 'Reached $5,000,000 total revenue!',
        'icon': '👑',
        'message': 'You\'ve built a massively profitable GPU empire!'
    },
    'datacenter_mogul': {
        'name': 'Datacenter Mogul',
        'description': 'Built a 200+ GPU datacenter!',
        'icon': '🏰',
        'message': 'Your datacenter rivals the biggest cloud providers!'
    },
    'enterprise_king': {
        'name': 'Enterprise King',
        'description': 'All 4 major contracts active simultaneously!',
        'icon': '🎖️',
        'message': 'OpenAI, Meta, Microsoft, AND Anthropic trust your infrastructure!'
    },
    'efficiency_master': {
        'name': 'Efficiency Master',
        'description': '90%+ SLA, 80%+ utilization, PUE < 1.25 with 50+ GPUs!',
        'icon': '🌟',
        'message': 'You\'ve mastered the art of datacenter optimization!'
    }
}

