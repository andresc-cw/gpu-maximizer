"""Flask application for GPU Tycoon"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from game.game_state import GameState
from game.gpus import GPU_CATALOG
from game.economy import COOLING_TIERS, SCHEDULER_TIERS

app = Flask(__name__)
CORS(app)

# Global game state (in-memory, single player)
game = GameState()

@app.route('/')
def index():
    """Serve the game page"""
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    """Get current game state"""
    return jsonify(game.to_dict())

@app.route('/api/tick', methods=['POST'])
def tick():
    """Advance game simulation"""
    data = request.json or {}
    dt = data.get('dt', 0.2)  # Default 200ms
    
    game.update(dt)
    return jsonify({'success': True})

@app.route('/api/action', methods=['POST'])
def action():
    """Handle player actions (purchases)"""
    data = request.json
    action_type = data.get('type')
    
    if action_type == 'buy_gpu':
        gpu_type = data.get('gpu_type')
        success, message = game.purchase_gpu(gpu_type)
        return jsonify({'success': success, 'message': message})
    
    elif action_type == 'upgrade_marketing':
        success, message = game.upgrade_marketing()
        return jsonify({'success': success, 'message': message})
    
    elif action_type == 'reset':
        game.reset()
        return jsonify({'success': True, 'message': 'Game reset'})
    
    elif action_type == 'assign_job':
        job_id = data.get('job_id')
        gpu_ids = data.get('gpu_ids', [])
        success, message = game.assign_job_to_gpus(job_id, gpu_ids)
        return jsonify({'success': success, 'message': message})
    
    elif action_type == 'toggle_auto_assign':
        auto_enabled = game.toggle_auto_assign()
        mode = "automatic" if auto_enabled else "manual"
        return jsonify({'success': True, 'message': f'Job assignment: {mode}', 'auto_assign': auto_enabled})
    
    elif action_type == 'start_contract_negotiation':
        contract_id = data.get('contract_id')
        success, message = game.start_contract_negotiation(contract_id)
        return jsonify({'success': success, 'message': message})
    
    elif action_type == 'invest_in_contract':
        contract_id = data.get('contract_id')
        amount = data.get('amount', 0)
        success, message = game.invest_in_contract(contract_id, amount)
        return jsonify({'success': success, 'message': message})
    
    return jsonify({'success': False, 'message': 'Unknown action'})

@app.route('/api/catalog')
def get_catalog():
    """Get item catalog for shop (simplified - only GPUs purchasable)"""
    return jsonify({
        'gpus': GPU_CATALOG,
        # For display purposes only (not purchasable)
        'cooling_info': COOLING_TIERS,
        'scheduler_info': SCHEDULER_TIERS
    })

if __name__ == '__main__':
    print("🎮 GPU Tycoon starting...")
    print("📊 Visit http://localhost:5000 to play!")
    app.run(debug=True, host='0.0.0.0', port=5000)

