# NETWORKING & SCHEDULING SPECS
## For GPU Tycoon / GPU Maximizer

---

## NETWORKING OPTIONS

### 1. **Basic Ethernet (Starting)**
- **Cost:** $0 (default)
- **Cross-node penalty:** -25% job performance
- **Description:** Standard networking. Multi-node jobs are slow.
- **Teaching:** Shows why networking matters.

### 2. **10 Gigabit Ethernet**
- **Cost:** $5,000
- **Cross-node penalty:** -15% job performance
- **Description:** Faster networking for small clusters.
- **Teaching:** First major upgrade; noticeable improvement.

### 3. **NVLink (Intra-Server)**
- **Cost:** $20,000
- **Cross-node penalty:** -5% (same server only, up to 8 GPUs)
- **Description:** Direct GPU-to-GPU connection within a single server. Fast!
- **Teaching:** Difference between intra-server vs inter-server communication.

### 4. **InfiniBand (Inter-Server)**
- **Cost:** $40,000
- **Cross-node penalty:** -8% job performance (any server)
- **Description:** Low-latency fabric for multi-server clusters.
- **Teaching:** Professional datacenter networking; enables large-scale training.

### 5. **NVLink Fabric (Endgame)**
- **Cost:** $100,000
- **Cross-node penalty:** -2% (up to 256 GPUs)
- **Description:** Turns entire datacenter into single compute fabric.
- **Teaching:** Ultimate interconnect; nearly eliminates network bottlenecks.

---

## SCHEDULING OPTIONS

### 1. **FIFO (First In, First Out)**
- **Cost:** $0 (default)
- **Effect:** Jobs run in arrival order
- **Teaching:** Simple but inefficient; large jobs block small ones.

### 2. **SJF (Shortest Job First)**
- **Cost:** $3,000
- **Effect:** +15% SLA compliance for small jobs
- **Teaching:** Minimizes average wait time but can starve large jobs.

### 3. **Priority Queue (SLA-Weighted)**
- **Cost:** $8,000
- **Effect:** +25% SLA compliance
- **Teaching:** Prioritizes urgent jobs based on deadline proximity.

### 4. **Backfill**
- **Cost:** $15,000
- **Effect:** +20% utilization
- **Teaching:** Fills idle GPUs with small jobs while reserving space for large ones.

### 5. **Preemptive Priority**
- **Cost:** $30,000
- **Effect:** +35% SLA compliance, -5% penalty on interrupted jobs
- **Teaching:** Can pause jobs for urgent work; handles traffic spikes.

---

## GAME DESIGN NOTES

### Progression Pacing
- **Early:** FIFO + Basic Ethernet → Feel the pain
- **Mid:** SJF/Priority + 10GbE → Learn optimization
- **Late:** Backfill/Preemptive + InfiniBand/NVLink → Mastery

### Key Teaching Moments
- **FIFO → SJF:** "Why is that small job waiting behind a 30-second training run?"
- **Basic → 10GbE:** "Multi-node jobs are way faster now!"
- **NVLink vs InfiniBand:** "NVLink is amazing within a server, but I need InfiniBand to scale across servers."
- **Backfill:** "I'm using idle GPUs while big jobs are reserved!"
- **Preemption:** "Inference rush? No problem—pause those batch jobs."

### Balancing
- Unlock scheduling upgrades after experiencing pain (queue depth > 5, SLA misses > 3)
- Unlock networking upgrades at revenue milestones ($50K, $150K, $500K)
- Cross-node penalties create natural pressure to upgrade

