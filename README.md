# 🎮 GPU Tycoon

An incremental management game about scaling GPU infrastructure - from a single workstation to a datacenter. Built for hackathons!

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python app.py
```

Then open your browser to: **http://localhost:5000**

## 🎯 How to Play

### Goal
Manage a GPU cluster, complete computational jobs, and grow your datacenter empire!

### Core Loop
1. **Jobs arrive** in your queue (Inference or Training)
2. Jobs **auto-assign** to available GPUs
3. Jobs complete and **earn cash**
4. **Reinvest** in more GPUs and marketing upgrades
5. Scale up to manage a full datacenter!

### Starting Out
- You begin with 1x NVIDIA L4 GPU and $3,000
- Small inference jobs will start arriving
- Complete jobs to earn money
- Buy more GPUs or invest in marketing
- Infrastructure (cooling, networking, schedulers) **auto-upgrades** as you grow!

## 📊 Game Systems

### GPUs (4 Core Tiers) - **Cooling Bundled!**
- **L4** ($3K) - Your desk GPU, air-cooled
- **A100** ($18K) - First pro GPU, liquid cooling included
- **H100** ($40K) - AI training beast, high-performance cooling
- **GB200** ($120K) - Endgame superchip, advanced cooling included

### Job Types (Simplified!)
- **Inference** (1 GPU): Fast jobs, $50, tight SLA (20s)
- **Training** (4 GPUs): Big jobs, $250, relaxed SLA (50s)

### Marketing Upgrades (Like Paperclips' Trust!)
- **Sales Team** ($10K) → +50% job volume
- **Marketing Campaign** ($40K) → +40% jobs, +30% value
- **Customer Success** ($60K) → +20% jobs, +40% value, +10s SLA buffer
- **Enterprise Sales** ($80K) → +30% jobs, +50% value
- **Platform Partnerships** ($120K) → +60% jobs, +60% value

### Auto-Managed Infrastructure (No Purchase Needed!)

**Cooling** - Auto-bundled with GPU purchases
- L4 → Air cooling (PUE 1.45)
- A100/H100 → Liquid cooling (PUE 1.28)
- GB200 → Advanced liquid (PUE 1.22)

**Networking** - Auto-scales with cluster size
- 1-4 GPUs → Basic Ethernet (25% penalty)
- 5-12 GPUs → 10GbE (15% penalty)
- 13-24 GPUs → NVLink (8% penalty)
- 25+ GPUs → InfiniBand/Fabric (3% penalty)

**Schedulers** - Auto-unlock at revenue milestones
- $0 → FIFO
- $50K → Priority Queue
- $150K → Backfill
- $400K → Preemptive

## 🎓 Learning Outcomes

This game teaches real datacenter concepts through **gameplay, not menus**:
- **GPU scaling**: From 1 GPU to 50+ (see infrastructure grow!)
- **Job types**: Inference vs Training workloads
- **Power efficiency**: PUE improves as you upgrade cooling
- **Network effects**: Larger clusters = better networking
- **Scheduling**: Auto-unlocks teach different algorithms
- **Real hardware**: L4, A100, H100, GB200 are actual NVIDIA products
- **Customer types**: Learn who uses GPU compute (Anthropic, Perplexity, etc.)

## 🏗️ Tech Stack

- **Backend**: Flask (Python) - simple REST API
- **Frontend**: Vanilla HTML/CSS/JavaScript - no frameworks
- **State**: In-memory (no database needed)
- **Audio**: Web Audio API for sound effects

## 📁 Project Structure

```
gpu-maximizer/
├── app.py                    # Flask server
├── game/
│   ├── game_state.py        # Game state management
│   ├── jobs.py              # Job generation & scheduling
│   ├── gpus.py              # GPU specs & management
│   └── economy.py           # Revenue, costs, unlocks
├── static/
│   ├── css/style.css        # Dark theme styling
│   ├── js/
│   │   ├── game.js          # Main game loop
│   │   ├── ui.js            # DOM updates
│   │   └── audio.js         # Sound effects
│   └── sounds/              # Audio files
├── templates/
│   └── index.html           # Game UI
└── requirements.txt
```

## 🎮 Controls

- **1x / 2x / 5x / 20x** - Game speed controls
- **Reset** - Start over from scratch
- **Shop Buttons** - Purchase GPUs and upgrades

## 🏆 Progression Phases

### Phase 1: Desk (0-5 min, $0-$30K)
- 1-4 L4 GPUs ($3K each)
- Inference jobs only
- Basic Ethernet networking
- **Unlock:** Sales Team marketing

### Phase 2: First Rack (5-10 min, $30K-$150K)
- Upgrade to A100 GPUs ($18K, liquid cooling included!)
- Training jobs start appearing (25% mix)
- 10GbE auto-enables at 5+ GPUs
- Priority Queue scheduler auto-unlocks
- **Unlock:** Marketing Campaign, Customer Success

### Phase 3: Datacenter (10-20 min, $150K+)
- H100 ($40K) and GB200 ($120K) available
- Balanced workload (40% inference, 60% training)
- NVLink networking (13+ GPUs)
- Backfill scheduler auto-unlocks
- **Unlock:** Enterprise Sales, Platform Partnerships
- Goal: Maximize $/min!

## 🔧 Development

### Run in Development Mode
```bash
python app.py
```

The server will reload automatically when you make changes.

### API Endpoints
- `GET /` - Game page
- `GET /api/state` - Current game state (JSON)
- `POST /api/tick` - Advance simulation
- `POST /api/action` - Purchase/upgrade actions
- `GET /api/catalog` - Item catalog

## 📝 Design Documents

See the `context/` folder for detailed specifications:
- `CONTEXT.md` - Complete game design document
- `GPU_SPECS.md` - GPU specifications and economics
- `NETWORKING_AND_SCHEDULING_SPECS.md` - Network and scheduler details
- `COHERENCE_CHECK.md` - Validation of all specs

## 🤝 Credits

Created for hackathons to teach datacenter GPU management concepts in a fun, interactive way.

Inspired by [Universal Paperclips](https://www.decisionproblem.com/paperclips/) and real-world GPU cluster operations.

## 📜 License

MIT License - Feel free to use for educational purposes!


