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

### 4.2 GPU System

<TBD>

### 4.3 Node & Rack System

<TBD>

### 4.4 Scheduler Policies

<TBD>

- **FIFO (First In First Out)** — simplest, baseline
- **SJF (Shortest Job First)** — lower average wait time, risk starving large jobs
- **Backfill** — reserves space for large job but fills idle capacity with small ones
- **Preempt** — interrupts large jobs for urgent small ones (5% penalty)

Scheduler policies are purchasable upgrades. Each affects admission order and queue dynamics.

### 4.5 Power and PUE System

**Formulas:**
- IT Power (kW) = Σ(active GPU TDP × utilization) / 1000
- Facility Power (kW) = IT Power × PUE
- Electric cost ($/s) = Facility Power × $0.15 / 3600

**PUE upgrades:**
- Base 1.45 → Row containment (1.35) → Liquid cooling (1.28) → Airflow optimization (1.22)

Each step lowers energy cost, indirectly increasing net profit.

### 4.6 Network System

<TBD>

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
