# GPU TYCOON — DESIGN DOSSIER

## 1. Overview

GPU Tycoon is a lightweight incremental management game about scaling GPU infrastructure—from a single workstation to a miniature datacenter.

Players manage a queue of computational jobs, earn money by completing them efficiently, and reinvest profits into new NVIDIA GPUs, cooling upgrades, and scheduling algorithms.

The game's educational goal is to teach players the fundamentals of GPU resource management, scheduling, and datacenter efficiency in an intuitive, visual, and playful way.

The experience should feel like *Universal Paperclips meets Cluster Scheduler Simulator*: simple interactions, real-world analogies, and exponential growth tempered by real engineering constraints.

## 2. Theme & Learning Goals

### Theme

- **Player role:** operator/engineer scaling CoreWeave-style GPU clusters
- **Narrative arc:** begin with a single GPU under your desk; end with a small rack-managed cluster
- **Tone:** lighthearted but grounded; players see the invisible physics of compute (power, heat, queueing)

### Learning Outcomes

- Understand GPU utilization, VRAM constraints, and co-location effects
- Learn what PUE (Power Usage Effectiveness) means and why cooling matters
- Experience scheduling trade-offs: FIFO vs SJF vs Backfill vs Preemption
- Recognize that scaling hardware introduces bottlenecks and diminishing returns
- Appreciate that datacenters balance energy, policy, and performance—not just "more GPUs"

## 3. Core Loop

1. Jobs arrive in a queue with specific resource requirements (GPUs, VRAM, duration, SLA)
2. Scheduler places jobs on available GPUs based on policy
3. Jobs complete, generating cash proportional to performance and SLA adherence
4. Player spends cash to:
   - Buy GPUs or nodes
   - Unlock racks
   - Upgrade scheduler, network, or cooling systems
5. Loop repeats with faster, more complex job streams and new events (heat waves, inference spikes)

**Goal:** maximize profit and utilization efficiency over time.

## 4. Gameplay Systems

### 4.1 Job System

Jobs are discrete tasks with:

- **size:** S (1 GPU), M (2 GPUs), L (4 GPUs)
- **duration:** base seconds before modifiers (6–28)
- **slaStart:** time window to start before penalty
- **basePayout:** $30–$240
- **vramPerGpu:** 8–60 GB depending on size

Jobs spawn on a timer (2–4 s random intervals). They enter a queue ordered per scheduler.

- **SLA miss penalty:** −30% payout
- **Cross-node jobs** suffer a network penalty unless upgraded

#### Workload Types

Jobs come in three categories reflecting real datacenter workloads:

**Training (Long-running, High VRAM)**
- Duration: 20–28 seconds
- VRAM: 40–60 GB per GPU
- Payout: $180–$240
- Typically Large (4 GPU) jobs
- Most affected by cross-node penalties

**Inference (Short bursts, Latency-sensitive)**
- Duration: 6–10 seconds
- VRAM: 8–16 GB per GPU
- Payout: $30–$60
- Typically Small (1 GPU) jobs
- High SLA urgency; benefits from preemptive scheduling

**Rendering (Medium duration)**
- Duration: 12–18 seconds
- VRAM: 16–32 GB per GPU
- Payout: $80–$140
- Typically Medium (2 GPU) jobs
- Balanced workload; good for testing scheduler efficiency

### 4.2 GPU System

See GPU_SPECS.md

### 4.3 Node & Rack System

**Simplified Model (Hackathon-Friendly):**
Players buy **individual GPUs** directly. The game automatically organizes GPUs into nodes and racks behind the scenes, with infrastructure costs factored into GPU pricing and cooling upgrades.

**How It Works:**
- **1-2 GPUs:** Auto-organized as single node (air-cooled, under desk)
- **3-8 GPUs:** Auto-organized into first rack with multiple nodes
- **9-32 GPUs:** Expands to 2 racks with proper datacenter infrastructure
- **33+ GPUs:** Multi-rack datacenter with advanced cooling and networking

**Key Mechanics:**
- **Intra-node jobs:** GPUs in same logical group (≤8) communicate faster
  - Penalty reduced by NVLink upgrade ($20K) — applies to all current and future GPUs
  
- **Inter-node jobs:** GPUs across groups use network fabric
  - Penalty reduced by Ethernet/InfiniBand upgrades
  
- **Cooling Requirements:**
  - **Air Cooling (Base):** Supports L4, L40S (up to 350W per GPU)
  - **Liquid Cooling ($15K):** Unlocks A100, H100, H200 (up to 700W per GPU) + improves PUE to 1.28
  - **Advanced Liquid ($30K):** Unlocks B200, GB200 (up to 1200W per GPU) + improves PUE to 1.22

**Infrastructure Auto-Scaling:**
- **Phase 1 (1-2 GPUs):** Small form factor node, air-cooled
- **Phase 2 (3-8 GPUs):** First rack appears, liquid cooling available
- **Phase 3 (9-32 GPUs):** Second rack appears, advanced networking recommended
- **Phase 4 (33+ GPUs):** Multi-rack datacenter, fabric networking optimal

**2025 Realism:**
- Modern GPU servers: 4-8 GPUs per node is standard (DGX H100 = 8 GPUs)
- Liquid cooling: Required for 700W+ GPUs (H100, H200, B200, GB200)
- Rack density: 30-60 kW per rack is current high-density standard
- NVLink: Connects up to 8 GPUs within a node at 900 GB/s (Hopper gen)

### 4.4 Scheduler Policies

Scheduler policies are purchasable upgrades. Start simple, unlock smarter algorithms:

1. **FIFO** (free) — Jobs run in arrival order; simple but inefficient
2. **SJF** ($3K) — Shortest jobs first; +15% SLA compliance for small jobs
3. **Priority Queue** ($8K) — SLA-urgency weighted; +25% SLA compliance
4. **Backfill** ($15K) — Fills idle GPUs while reserving large job slots; +20% utilization
5. **Preemptive Priority** ($30K) — Can pause jobs for urgent work; +35% SLA compliance

*See NETWORKING_AND_SCHEDULING_SPECS.md for full details.*

### 4.5 Power and PUE System

**Formulas:**
- IT Power (kW) = Σ(active GPU TDP × utilization) / 1000
- Facility Power (kW) = IT Power × PUE
- Electric cost ($/s) = Facility Power × $0.15 / 3600

**PUE Progression (tied to cooling upgrades):**
- **Base Air Cooling:** PUE 1.45 (free, supports L4, L40S)
- **Liquid Cooling:** PUE 1.28 ($15K, unlocks A100/H100/H200)
- **Advanced Liquid:** PUE 1.22 ($30K, unlocks B200/GB200)

**Why It Matters:**
- Lower PUE = less wasted energy = lower electricity bills
- Example: 10 kW IT load at PUE 1.45 = 14.5 kW facility power ($0.60/hour)
- Same load at PUE 1.22 = 12.2 kW facility power ($0.51/hour) — **15% savings!**

Each cooling upgrade both unlocks higher-TDP GPUs AND improves efficiency.

### 4.6 Network System

Network upgrades reduce cross-node job penalties. Simple progression:

1. **Basic Ethernet** (free) — -25% cross-node penalty; motivates first upgrade
2. **10 Gigabit Ethernet** ($5K) — -15% penalty; first major improvement
3. **NVLink** ($20K) — -5% penalty for same-server GPUs (up to 8)
4. **InfiniBand** ($40K) — -8% penalty; professional inter-server fabric
5. **NVLink Fabric** ($100K) — -2% penalty; endgame datacenter fabric (up to 256 GPUs)

**Key Teaching:** NVLink = fast intra-server, InfiniBand = fast inter-server.

*See NETWORKING_AND_SCHEDULING_SPECS.md for full details.*

### 4.7 Economy System

- Money inflow from completed jobs
- Continuous cost from energy consumption
- Balance tuned for visible progression every 1–2 minutes
- No hard fail state—player can always recover through smarter upgrades

### 4.8 Events

Random timed modifiers:

- **Heat Wave:** temporarily increases PUE (+0.08)
- **Inference Rush:** doubles job spawn rate for 20 s
- **Power Surge:** doubles electricity cost briefly

### 4.9 UI & Dashboard

The interface mirrors real datacenter monitoring tools (Grafana, Prometheus-style):

**Main Dashboard (Center)**
- Job queue visualization (cards flowing left to right)
- Active jobs on GPUs with progress bars
- GPU utilization bars (per GPU, color-coded by load)
- Visual heat indicators on overworked GPUs

**Metrics Panel (Top)**
- Real-time graphs: Utilization %, Revenue/hour, Queue depth
- Current stats: Cash, Revenue rate, Power cost, Net profit
- KPIs: SLA compliance %, Average job wait time

**Status Panel (Right)**
- GPU inventory with VRAM usage
- Current PUE value and temperature indicator
- Active scheduler and network tier
- Event notifications (Heat Wave alert, etc.)

**Controls (Bottom)**
- Shop/upgrade buttons (GPUs, Cooling, Scheduler, Network)
- Speed controls (pause, 1x, 2x, 5x)

**Visual Design**
- Dark theme with neon accents (teal/purple for CoreWeave vibes)
- Minimal, dashboard-style UI (not cartoony)
- Smooth animations for job flow and completion
- Sound effects: satisfying "ding" on job complete, alert beeps for SLA misses

### 4.10 Progression & Unlocks

Clear milestone-based progression for demos:

**Phase 1: Desk (0–5 min)**
- **Start:** 1x L4 GPU ($3K), FIFO scheduler, Basic Ethernet, Air cooling (PUE 1.45)
- **Available Jobs:** Small (S) inference jobs only
- **Goal:** Earn $10,000 total revenue
- **Unlocks at $10K:** L40S GPU ($8K), SJF scheduler ($3K)
- **Teaching:** "Queue is backing up! Need more GPUs or better scheduling."

**Phase 2: First Rack (5–10 min)**
- **Situation:** 3-4 GPUs, Medium (M) jobs appearing, multi-GPU workloads start
- **Goal:** Earn $50,000 total revenue + 70% SLA compliance
- **Unlocks at $50K:** 
  - Liquid Cooling ($15K) → unlocks A100 ($12K), H100 ($25K) + PUE 1.28
  - 10GbE networking ($5K)
  - Priority Queue scheduler ($8K)
- **Teaching:** "Multi-GPU jobs are slow! Need better networking. Power bills rising!"

**Phase 3: Small Cluster (10–15 min)**
- **Situation:** 8-16 GPUs, Large (L) training jobs appearing, first Inference Rush event
- **Goal:** Earn $200,000 total revenue
- **Unlocks at $200K:**
  - H200 GPU ($35K)
  - NVLink ($20K) — reduces intra-node penalty to -5%
  - Backfill scheduler ($15K)
  - InfiniBand networking ($40K)
- **Teaching:** "Backfill fills gaps! NVLink makes same-server jobs blazing fast."

**Phase 4: Datacenter (15+ min)**
- **Situation:** 20-64 GPUs, complex multi-node large jobs, frequent events
- **Goal:** Maximize profit/hour and GPU utilization
- **Unlocks at $500K:**
  - Advanced Liquid Cooling ($30K) → unlocks B200 ($50K), GB200 ($70K) + PUE 1.22
  - NVLink Fabric ($100K) — reduces cross-rack penalty to -2%
  - Preemptive Priority scheduler ($30K)
- **Teaching:** "I'm running a real datacenter! Managing 50+ GPUs efficiently."

**Unlock Logic:**
- **Revenue milestones** unlock hardware tiers (GPUs, cooling, networking)
- **Pain points** unlock schedulers (5+ queued jobs, 3+ SLA misses in 60s)
- **Achievement pop-ups:** "Cluster Operator" (10 GPUs), "SLA Champion" (90% compliance), "Power Efficiency Expert" (PUE < 1.25)

---

## 5. Purchase Model Summary

**What Players Buy:**
- ✅ **Individual GPUs** ($3K-$70K) — see GPU_SPECS.md
- ✅ **Cooling Upgrades** ($15K, $30K) — unlock GPU tiers + improve PUE
- ✅ **Schedulers** ($3K-$30K) — improve efficiency + SLA compliance
- ✅ **Networking** ($5K-$100K) — reduce cross-node penalties

**What's Automatic:**
- ✅ **Nodes & Racks** — auto-scale based on GPU count (visual only, no separate purchase)
- ✅ **Power delivery** — included in cooling upgrades
- ✅ **Basic infrastructure** — cost abstracted into GPU prices

**Revenue Sources:**
- Job completion payouts ($30-$240 per job)
- SLA bonuses (full payout if started on time, -30% if missed)
- Higher performance GPUs = more jobs completed per hour

**Costs:**
- GPU purchase (one-time)
- Cooling/Scheduler/Network upgrades (one-time)
- Electricity (continuous, based on TDP × PUE × $0.15/kWh)

**Key Balance:**
- Power costs are ~0.1-1% of revenue (realistic for AI datacenters)
- ROI on GPU: L4 pays for itself in ~50 jobs (~5 minutes at high utilization)
- Upgrades have clear teaching moments (pain → purchase → relief)
