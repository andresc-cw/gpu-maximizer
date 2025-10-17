# GPU Specifications for GPU Maximizer

---

## Phase 1: Desk GPUs (Air-Cooled)

### 1. NVIDIA L4 (Starter)
- **VRAM**: 24 GB
- **TDP**: 72 W
- **Cost**: $3,000
- **Performance**: 1x (baseline)
- **Unlock**: Starting GPU
- **Cooling**: Air (PUE 1.45)
- **Best For**: Small inference jobs (6-10s, 8-16 GB VRAM)

### 2. NVIDIA L40S (Early Upgrade)
- **VRAM**: 48 GB
- **TDP**: 350 W
- **Cost**: $8,000
- **Performance**: 2.5x
- **Unlock**: $10K revenue
- **Cooling**: Air (PUE 1.45)
- **Best For**: Medium rendering jobs (12-18s, 16-32 GB VRAM)

---

## Phase 2: First Rack (Liquid-Cooled)

### 3. NVIDIA A100
- **VRAM**: 80 GB
- **TDP**: 300 W
- **Cost**: $12,000
- **Performance**: 4x
- **Unlock**: $50K revenue + Liquid Cooling ($15K)
- **Cooling**: Liquid (PUE 1.28)
- **Best For**: Large training jobs (20-28s, 40-60 GB VRAM per GPU)

### 4. NVIDIA H100 SXM
- **VRAM**: 80 GB
- **TDP**: 700 W
- **Cost**: $25,000
- **Performance**: 7x
- **Unlock**: $50K revenue + Liquid Cooling ($15K)
- **Cooling**: Liquid (PUE 1.28)
- **Best For**: High-performance training, NVLink-optimized workloads

---

## Phase 3: Small Cluster

### 5. NVIDIA H200
- **VRAM**: 141 GB
- **TDP**: 700 W
- **Cost**: $35,000
- **Performance**: 10x
- **Unlock**: $200K revenue
- **Cooling**: Liquid (PUE 1.28)
- **Best For**: LLM training, massive VRAM requirements (HBM3e memory)

---

## Phase 4: Datacenter (Advanced Liquid)

### 6. NVIDIA B200 (Blackwell)
- **VRAM**: 192 GB
- **TDP**: 1,000 W
- **Cost**: $50,000
- **Performance**: 18x
- **Unlock**: $500K revenue + Advanced Liquid Cooling ($30K)
- **Cooling**: Advanced Liquid (PUE 1.22)
- **Best For**: 2025 cutting-edge training, 30x faster inference than H100

### 7. NVIDIA GB200 (Grace Blackwell Superchip)
- **VRAM**: 192 GB
- **TDP**: 1,200 W
- **Cost**: $70,000
- **Performance**: 25x
- **Unlock**: $500K revenue + Advanced Liquid Cooling ($30K)
- **Cooling**: Advanced Liquid (PUE 1.22)
- **Best For**: Ultimate endgame GPU, integrated CPU+GPU for maximum efficiency

---

## Game Mechanics

### Job Types & VRAM Requirements

**Inference Jobs (Small - 1 GPU)**
- VRAM: 8-16 GB per GPU
- Duration: 6-10 seconds
- Payout: $30-$60
- Best GPUs: L4, L40S, A100
- Characteristics: Short, latency-sensitive, high frequency

**Rendering Jobs (Medium - 2 GPUs)**
- VRAM: 16-32 GB per GPU (32-64 GB total)
- Duration: 12-18 seconds
- Payout: $80-$140
- Best GPUs: L40S, A100, H100
- Characteristics: Balanced workload, moderate multi-GPU coordination

**Training Jobs (Large - 4 GPUs)**
- VRAM: 40-60 GB per GPU (160-240 GB total)
- Duration: 20-28 seconds
- Payout: $180-$240
- Best GPUs: A100, H100, H200, B200, GB200
- Characteristics: Long-running, high VRAM, benefits most from NVLink/fast networking

### Power & Economics

**Power Cost Formula:**
- Electric cost ($/s) = (Σ GPU TDP × utilization / 1000) × PUE × $0.15 / 3600

**Example Costs (per hour at 100% utilization):**
- 1x L4 @ PUE 1.45: $0.015/hour (negligible)
- 1x H100 @ PUE 1.28: $0.134/hour (noticeable)
- 8x H100 @ PUE 1.28: $1.08/hour (significant)
- 32x H100 @ PUE 1.22: $3.73/hour (datacenter scale)

**Revenue vs Cost Balance:**
- L4 completes ~360 small jobs/hour = $10,800 revenue, $0.015 cost = **99.9% profit margin**
- H100 completes ~1,500 small jobs/hour = $45,000 revenue, $0.134 cost = **99.9% profit margin**
- Power costs are real but small compared to job revenue (realistic for AI datacenters)

### GPU Selection Strategy

- **Early game (Phase 1-2):** Focus on quantity (more L4s) or upgrade to L40S/A100
- **Mid game (Phase 3):** Balance high-performance H100s with cost-effective A100s
- **Late game (Phase 4):** H200/B200 for maximum throughput, but watch power bills!
