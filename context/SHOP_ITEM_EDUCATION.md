# Shop Item Educational Blurbs
## For CoreWeave Employees: GPU Tycoon Edition

This document contains detailed educational content for every shop item, designed to teach CoreWeave employees about GPU infrastructure, cooling, and networking technologies.

---

## GPU CATALOG

### 1. NVIDIA L4 (Starter GPU)
**Architecture:** Ada Lovelace (4nm process)  
**Launch:** March 2023  
**Specs:** 24GB GDDR6, 72W TDP, 7,680 CUDA cores

**Educational Blurb:**
"The humble L4 is your entry point into AI infrastructure! Don't let the 72W TDP fool you—Ada Lovelace's efficiency makes this GPU punch way above its weight class. Built on a 4nm process, it's perfect for inference workloads like Stable Diffusion or small LLM serving. Fun fact: You can fit 10 L4s in a standard 1U server while consuming less power than two H100s!"

**What Makes It Special:**
- **Energy Champion:** 72W TDP means you can run dozens without melting your datacenter
- **Ada Architecture:** First gen with 4th-gen Tensor Cores supporting FP8 precision
- **Inference King:** Optimized for real-time inference (think Perplexity's search queries)
- **PCIe Only:** No NVLink, but at this price point, who cares?

**Real-World Use:**
CoreWeave customers use L4s for burst inference capacity—when Character.AI goes viral, they spin up hundreds of L4 instances instantly.

**Technical Tidbit:**
The L4's NVENC engine can transcode 140 streams of 1080p30 video simultaneously, making it secretly amazing for video analytics pipelines!

---

### 2. NVIDIA L40S (Early Workhorse)
**Architecture:** Ada Lovelace (4nm)  
**Launch:** October 2023  
**Specs:** 48GB GDDR6, 350W TDP, 18,176 CUDA cores

**Educational Blurb:**
"The L40S is the 'Swiss Army Knife' of GPUs—graphics pros love it for rendering, ML engineers love it for training, and finance bros love it for quant modeling. With 48GB of VRAM, you can actually fit some decent models in memory without resorting to model sharding trickery."

**What Makes It Special:**
- **Dual Personality:** Ada's RT cores + Tensor cores = graphics AND AI
- **VRAM Sweet Spot:** 48GB is the magic number for many 13B-30B parameter models
- **Last Air-Cooled Beast:** Max 350W means standard datacenter air cooling works
- **Studio Darling:** Framestore uses these for real-time Unreal Engine VFX previews

**Real-World Use:**
DNEG (VFX studio) uses L40S clusters to render "Dune" VFX during the day, then switches to fine-tuning Stable Diffusion models at night. GPU utilization: 💯

**Technical Tidbit:**
The L40S has 18,176 CUDA cores—exactly 2.37x more than the L4. NVIDIA's die binning process is *chef's kiss*.

---

### 3. NVIDIA A100 (OG Datacenter King)
**Architecture:** Ampere (7nm)  
**Launch:** May 2020  
**Specs:** 80GB HBM2e, 300W TDP, 6,912 CUDA cores

**Educational Blurb:**
"The A100 is the GPU that made AI go mainstream. Released in 2020, it powered GPT-3's training and every major LLM since. HBM2e memory at 2TB/s bandwidth means this thing feeds data to tensor cores faster than you can say 'attention is all you need.' Multi-Instance GPU (MIG) lets you slice one A100 into 7 isolated GPUs—perfect for multi-tenant cloud environments (hi, CoreWeave!)."

**What Makes It Special:**
- **MIG Technology:** Partition into 7 independent GPU instances (game-changer for cloud)
- **HBM2e Memory:** 2TB/s bandwidth crushes GDDR6's 900GB/s
- **Structural Sparsity:** 2:4 sparsity support doubles throughput for pruned models
- **NVLink Gen 3:** 600GB/s bidirectional between GPUs—build giant model clusters

**Real-World Use:**
Anthropic trained Claude 1.0 on A100 clusters. Cohere's production inference still runs on A100s because "if it ain't broke..."

**Technical Tidbit:**
The A100's Tensor Cores can perform 312 TFLOPS of FP16 compute—that's 312 TRILLION floating-point operations per second. Your calculator does ~0.00001 TFLOPS. 🤯

---

### 4. NVIDIA H100 (Hopper Revolution)
**Architecture:** Hopper (4nm TSMC)  
**Launch:** September 2022  
**Specs:** 80GB HBM3, 700W TDP, 16,896 CUDA cores

**Educational Blurb:**
"Jensen Huang's leather jacket special. The H100 brought Transformer Engine with FP8 precision—specifically designed for modern LLM architectures. It's not just 'faster,' it's fundamentally *different*. Hopper introduced the DPX instruction set for dynamic programming (genomics nerds rejoice!) and boosted NVLink to 900GB/s. Training LLaMA 2? You need H100s. Running GPT-4-scale inference? H100s. Building AGI? ...probably H100s."

**What Makes It Special:**
- **Transformer Engine:** FP8 precision with automatic loss scaling = 2x throughput for LLMs
- **NVLink Gen 4:** 900GB/s per GPU = 7.2TB/s in an 8-GPU node
- **HBM3 Memory:** 3.35TB/s bandwidth (1.6x faster than A100's HBM2e)
- **DPX Instructions:** Hardware acceleration for dynamic programming algorithms

**Real-World Use:**
Meta trained LLaMA 2 70B on H100 clusters. OpenAI's GPT-4 inference runs on H100s. CoreWeave's H100 pods power Inflection AI's Pi assistant.

**Technical Tidbit:**
One H100 can perform 2 PETAFLOPS of FP8 tensor operations. That's 2,000 TERAFLOPS. That's 2,000,000 GIGAFLOPS. Absolute unit.

**The 700W Story:**
At 700W, you can fry 7 eggs simultaneously on an H100's heatsink. Don't try this at home (or in the datacenter).

---

### 5. NVIDIA H200 (Memory Monster)
**Architecture:** Hopper (4nm, HBM3e refresh)  
**Launch:** December 2023  
**Specs:** 141GB HBM3e, 700W TDP, 16,896 CUDA cores

**Educational Blurb:**
"The H200 is what happens when NVIDIA says 'more memory = more better.' Same Hopper architecture as H100, but with a memory glow-up: 141GB of HBM3e (vs 80GB) and 4.8TB/s bandwidth (vs 3.35TB/s). That 141GB is the magic number—it can fit LLaMA 2 70B in FP16 with room to spare. No tensor parallelism required!"

**What Makes It Special:**
- **HBM3e Revolution:** 4.8TB/s memory bandwidth = 43% faster than H100
- **141GB Capacity:** The sweet spot for 70B parameter models without sharding
- **Same Power:** Still 700W, so drop-in replacement for H100 infrastructure
- **Inference Beast:** 1.9x faster inference on GPT-3 compared to H100

**Real-World Use:**
CoreWeave was FIRST to market with H200 instances (Dec 2023). Customers use them for serving 70B models that previously required multi-GPU setups.

**Technical Tidbit:**
HBM3e's "e" stands for "extreme"—SK Hynix engineers achieved 1.15Tb/s per stack, a 50% improvement over base HBM3. Materials science wizardry!

---

### 6. NVIDIA B200 (Blackwell Arrives)
**Architecture:** Blackwell (4nm, multi-chiplet)  
**Launch:** March 2024 (announced), 2025 (volume shipping)  
**Specs:** 192GB HBM3e, 1000W TDP, dual-die design

**Educational Blurb:**
"Welcome to the future. Blackwell isn't just a new architecture—it's two GPUs in a trench coat. NVIDIA fused two dies with 10TB/s interconnect bandwidth, creating the world's largest chip (208 billion transistors). The B200's second-gen Transformer Engine supports FP4 precision for inference, doubling throughput again. At 1000W, you MUST have liquid cooling. No exceptions."

**What Makes It Special:**
- **Dual-Die Design:** Two chips act as one via ultra-high-bandwidth interconnect
- **208B Transistors:** 2.5x the transistor count of H100 (80B transistors)
- **FP4 Precision:** Inference at 4-bit floating point = 2x H100 throughput
- **192GB HBM3e:** Enough memory for 100B+ parameter models in FP8

**Real-World Use:**
OpenAI reportedly ordered 100,000+ B200 GPUs for GPT-5 training. Meta's future LLaMA models will train on Blackwell clusters.

**Technical Tidbit:**
Blackwell's dies communicate via 10TB/s—that's faster than NVLink between separate GPUs. It's not "multi-GPU," it's "one really thicc GPU."

**The 1000W Problem:**
1000W per GPU means an 8-GPU node consumes 8kW under load. Add networking and CPU: 10kW per node. A 42U rack with 5 nodes? 50kW. That's why liquid cooling isn't optional—it's mandatory.

---

### 7. NVIDIA GB200 (Grace Blackwell Superchip)
**Architecture:** Grace CPU (72-core ARM) + Blackwell GPU  
**Launch:** 2025 (volume production)  
**Specs:** 192GB GPU HBM3e + 480GB CPU LPDDR5X = 672GB unified memory

**Educational Blurb:**
"This is NVIDIA's 'screw it, we're making the whole server' moment. The GB200 fuses a 72-core ARM CPU (Grace) with a Blackwell GPU via 900GB/s NVLink-C2C. The CPU can access all 192GB of GPU HBM3e directly—no PCIe bottleneck. It's not a GPU, it's a compute platform. Designed for trillion-parameter models that don't fit anywhere else."

**What Makes It Special:**
- **Unified Memory:** 672GB total (GPU + CPU) accessible by both processors
- **No PCIe:** CPU-GPU connected via 900GB/s NVLink-C2C—50x faster than PCIe 5.0
- **ARM Architecture:** Grace uses ARMv9 with SVE2 vector extensions
- **Liquid Cooling Only:** 1200W TDP—this is a space heater masquerading as a computer

**Real-World Use:**
The GB200 NVL72 rack (72 GB200s) offers 720 petaFLOPS—enough to train foundation models in record time. CoreWeave is deploying these for frontier AI workloads.

**Technical Tidbit:**
Grace CPU's 72 cores might sound modest, but each core has 4MB of L2 cache (288MB total). That's more cache than most desktop CPUs have L3!

**Cooling Reality:**
At 1200W, one GB200 consumes more power than 16 L4 GPUs. The NVL72 rack needs liquid cooling loops rated for 120kW heat dissipation. 🔥

---

## COOLING SYSTEMS

### 1. Air Cooling (Base)
**PUE:** 1.45  
**Max TDP:** 350W per GPU  
**Cost:** $0 (base infrastructure)

**Educational Blurb:**
"The OG datacenter cooling. Giant CRAC (Computer Room Air Conditioning) units blow cold air through raised floors, up through server racks, and back to the cooling units. Simple, proven, and... inefficient. At PUE 1.45, for every 1kW powering your GPUs, you're spending 0.45kW cooling them. Hot/cold aisle containment helps, but physics is physics—air has terrible heat capacity."

**How It Works:**
- Cold air enters through perforated floor tiles at the front of racks
- Server fans pull air through heatsinks, warming it up
- Hot air rises and returns to CRAC units via ceiling plenum
- CRAC units cool the air and recirculate

**Why It's Limiting:**
- Air can only cool ~350W effectively before heatsinks become too large
- Hot spots form when airflow is blocked
- Fans consume 10-15% of total system power
- Ambient temperature limits: can't cool below room temp + margin

**CoreWeave Reality:**
Our Phase 1 deployments (L4, L40S) use air cooling because it's cost-effective. But once you hit H100-scale power density, air cooling becomes physically impossible.

**Fun Fact:**
Google's early datacenters used evaporative cooling (swamp coolers) before switching to liquid. Larry Page reportedly said air cooling was "like trying to cool a bonfire with a desk fan."

---

### 2. Liquid Cooling ($15K)
**PUE:** 1.28  
**Max TDP:** 700W per GPU  
**Cooling Method:** Direct-to-chip cold plates

**Educational Blurb:**
"Water (or coolant) has 4x the heat capacity of air. Liquid cooling puts cold plates directly on GPU dies, with fluid flowing through microchannels at 3-5 gallons per minute. This handles 700W GPUs (H100, H200) that would melt under air cooling. PUE drops to 1.28 because pumps use less energy than hundreds of fans, and you can reject heat more efficiently via outdoor cooling towers."

**How It Works:**
- Cold plates bolt directly to GPU die (via thermal interface material)
- Facility-chilled water (15-20°C) flows through cold plates
- Water absorbs heat (up to 40°C outlet temperature)
- Hot water flows to heat exchangers or cooling towers
- Chilled water returns to GPUs in a closed loop

**Why It's Better:**
- Handles 700W+ power densities impossible with air
- Lower PUE (1.28 vs 1.45) = 12% energy savings
- Quieter operation (fewer fans)
- More predictable cooling (no hot spots)

**CoreWeave Implementation:**
Our H100/H200 clusters use CoolIT or Asetek direct-to-chip cooling systems. Each rack has inlet/outlet manifolds connecting to facility chilled water plants.

**The $15K Cost:**
- Cold plates: $500-800 per GPU
- Rack manifolds and quick-disconnects: $5K
- Facility chilled water plant upgrades: $10-20K per rack

**Fun Fact:**
Meta's RSC (Research SuperCluster) uses liquid cooling for 16,000 A100s. The chilled water plant processes 5,000 gallons per minute—enough to fill an Olympic pool in 132 minutes!

---

### 3. Advanced Liquid Cooling ($30K)
**PUE:** 1.22  
**Max TDP:** 1200W per GPU  
**Cooling Method:** Immersion or hybrid liquid + facility upgrades

**Educational Blurb:**
"When GPUs hit 1000W+ (B200, GB200), even direct-to-chip liquid cooling struggles. Advanced liquid takes two forms: (1) Immersion cooling—submerge entire servers in dielectric fluid (3M Novec or similar), or (2) High-flow cold plates with facility-scale chiller upgrades. PUE drops to 1.22 because waste heat can power building heating or generate electricity via ORC (Organic Rankine Cycle) systems."

**Immersion Cooling Details:**
- Servers submerged in non-conductive fluid (dielectric coolant)
- Fluid has higher heat capacity than water
- No cold plates needed—fluid contacts components directly
- Cooling density: 100kW+ per rack

**Hybrid Advanced Liquid:**
- Enhanced cold plates with 5-10 GPM flow rates
- Facility-scale chillers with 5-10°C coolant (colder than standard)
- Heat rejection via cooling towers + dry coolers
- Optional waste heat recovery for building HVAC

**Why It's Necessary:**
- B200 (1000W) and GB200 (1200W) exceed standard liquid cooling capacity
- Rack-level power density: 50-120kW requires advanced infrastructure
- PUE 1.22 means only 22% overhead—best-in-class efficiency

**CoreWeave's Strategy:**
For Blackwell deployments, we're installing both immersion tanks (for research clusters) and advanced cold plate systems (for production inference).

**The $30K Investment:**
- Immersion tanks: $50K per rack (amortized to ~$6K per GPU)
- High-flow cold plates: $1,200 per GPU
- Facility chiller upgrades: $100K+ per building
- Waste heat recovery systems: Optional $200K+

**Fun Fact:**
Microsoft's Project Natick (underwater datacenter) achieved PUE 1.15 by using ocean water for cooling. They found servers underwater had 1/8th the failure rate of land-based servers—possibly due to stable temps and oxygen-free environment!

**Real-World Example:**
Frontier supercomputer (Oak Ridge National Lab) uses advanced liquid cooling for 9,408 AMD MI250X GPUs (560W each). Total facility power: 29MW. PUE: 1.23. Without liquid cooling, it would require 40MW+ and wouldn't physically fit in the building!

---

## NETWORKING TECHNOLOGIES

### 1. Basic Ethernet (Free)
**Bandwidth:** 1-10 Gbps  
**Cross-Node Penalty:** -25%  
**Latency:** ~10-50 microseconds

**Educational Blurb:**
"Your standard datacenter networking—ubiquitous, cheap, and... slow (for AI workloads). At 10 Gbps, transferring model weights between GPUs takes forever. That -25% penalty? It's from GPUs waiting on network transfers during distributed training. AllReduce operations (syncing gradients across GPUs) become the bottleneck. Fine for web services, terrible for multi-node training."

**Technical Details:**
- Standard TCP/IP protocol stack
- Switch-based networking (usually TOR: Top of Rack switches)
- RDMA optional but rarely enabled
- Max effective throughput: ~7-8 Gbps (after TCP overhead)

**Why It's Limiting for AI:**
- LLaMA 2 70B has 140GB of weights—takes 18 seconds to transfer over 10GbE
- During training, gradients sync every forward/backward pass (~50-100ms)
- Network becomes bottleneck when GPU compute finishes faster than transfer

**CoreWeave Baseline:**
Every instance includes at least 10GbE connectivity. It's the minimum viable networking for single-node workloads.

---

### 2. 10 Gigabit Ethernet ($5K)
**Bandwidth:** 10-25 Gbps  
**Cross-Node Penalty:** -15%  
**Latency:** ~5-10 microseconds

**Educational Blurb:**
"Stepping up to 25GbE with RDMA (Remote Direct Memory Access) makes things snappier. RDMA bypasses the CPU and OS kernel, letting NICs read/write directly to GPU memory. That cuts latency in half and makes gradient synchronization tolerable. The -15% penalty is still noticeable but not crushing."

**Technical Upgrades:**
- 25 Gbps per link (2.5x faster than standard)
- RoCE (RDMA over Converged Ethernet) enabled
- Lower latency via kernel bypass
- Better for 2-4 node training jobs

**Why It's Better:**
- LLaMA 2 70B transfer time: ~7 seconds (vs 18 seconds)
- Gradient sync during training: ~20-40ms per step
- Cost-effective for small-scale distributed training

---

### 3. NVLink ($20K)
**Bandwidth:** 900 GB/s bidirectional (per GPU in 8-GPU node)  
**Cross-Node Penalty:** -5% (same node only)  
**Latency:** <1 microsecond

**Educational Blurb:**
"NVLink isn't networking—it's a GPU interconnect. Think of it as PCIe on steroids: 900GB/s vs PCIe 5.0's 128GB/s. In an 8-GPU node, NVLink forms a mesh topology where every GPU can talk to every other GPU at insane speeds. That -5% penalty is basically measurement error. The catch? Only works within one node (up to 8 GPUs)."

**Technical Deep Dive:**
- 18 NVLink lanes per H100 (50GB/s per lane)
- Full mesh topology in DGX H100 (8 GPUs)
- Peer-to-peer GPU memory access (no CPU involvement)
- NVSwitch fabric enables any-to-any communication

**Why It's Magical:**
- Model parallelism: Split 175B GPT-3 across 8 GPUs seamlessly
- No network stack overhead—direct GPU-to-GPU memory transfers
- AllReduce operations: ~1ms vs 20-40ms on Ethernet

**CoreWeave's NVLink Config:**
H100 instances include NVLink by default within 8-GPU nodes. It's not optional—it's fundamental to modern AI infrastructure.

**Fun Fact:**
NVLink Gen 4 (Hopper) has 18 lanes × 50GB/s = 900GB/s total bidirectional bandwidth. That's 7.2 TB/s in an 8-GPU fully connected mesh. You could transfer the entire Wikipedia text database (20GB compressed) in 2.7 milliseconds!

---

### 4. InfiniBand ($40K)
**Bandwidth:** 400 Gbps (NDR) or 200 Gbps (HDR)  
**Cross-Node Penalty:** -8%  
**Latency:** ~500 nanoseconds

**Educational Blurb:**
"InfiniBand is the 'datacenter LAN party' solution for HPC and AI. It's designed for one thing: moving data between servers faster than anything else. RDMA is built-in (not an afterthought like Ethernet), latency is sub-microsecond, and 400 Gbps links mean multi-node training doesn't suck. That -8% penalty? It's from CPU overhead unpacking messages—the network itself is blazing fast."

**Technical Specifications:**
- NDR (Next Data Rate): 400 Gbps per port
- HDR (High Data Rate): 200 Gbps per port
- Full RDMA support via IB Verbs API
- Adaptive routing avoids congestion
- Credit-based flow control (lossless fabric)

**Why HPC Loves It:**
- Frontier supercomputer uses InfiniBand (9,408 nodes interconnected)
- MPI (Message Passing Interface) optimized for IB
- ScaleIO storage networks run on InfiniBand

**CoreWeave's IB Fabric:**
H100 clusters use NVIDIA Quantum-2 InfiniBand switches (400 Gbps NDR). Multi-node training jobs (8+ nodes, 64+ GPUs) require IB to maintain training efficiency above 85%.

**The $40K Price:**
- InfiniBand HCA (Host Channel Adapter): $2-3K per server
- NDR switches: $50-100K each (48-port)
- Cables: $300-800 each (copper vs optical)
- Amortized cost: ~$5K per GPU in a 64-GPU cluster

---

### 5. NVLink Fabric ($100K)
**Bandwidth:** Up to 1.8 TB/s per GPU (Blackwell NVLink 5.0)  
**Cross-Node Penalty:** -2% (up to 256 GPUs)  
**Latency:** <1 microsecond (intra-rack)

**Educational Blurb:**
"This is NVIDIA's endgame: turn 72 servers into ONE GIANT GPU. NVLink Fabric uses NVSwitch spine switches to interconnect 72× GB200 nodes (144 GPUs) with 130 TB/s of total bisection bandwidth. Every GPU can talk to every other GPU as if they're in the same server. The -2% penalty is from packet routing latency—the bandwidth itself is INSANE."

**GB200 NVL72 Architecture:**
- 72× GB200 Superchips (144 GPUs total)
- 5th-gen NVLink: 1.8 TB/s per GPU
- NVSwitch spine: 14.4 TB/s per switch
- Total fabric bandwidth: 130 TB/s bisection

**Why It's Revolutionary:**
- Train trillion-parameter models without sharding across nodes
- Gradient AllReduce across 144 GPUs: ~2-3ms (vs 20-50ms on InfiniBand)
- Memory coherence: Treat 27TB of HBM (144× 192GB) as unified pool

**Real-World Deployment:**
The NVL72 rack is a liquid-cooled 10U unit consuming 120kW under full load. CoreWeave is deploying dozens of these for frontier AI workloads (GPT-5 training, etc.).

**The $100K Reality:**
- NVSwitch spine: $30-40K
- NVLink cables and adapters: $20-30K
- Liquid cooling infrastructure: $40-50K
- Power delivery (120kW capable): $10K

**Fun Fact:**
One GB200 NVL72 rack provides 720 petaFLOPS of FP4 compute. That's more than the entire TOP500 supercomputer list from 2017 (combined)—in a single rack!

**Technical Marvel:**
NVLink 5.0 runs at 112.5 GBaud signaling (PAM4 encoding) over copper twinax cables. That's pushing the physical limits of electrical signaling—any faster requires optics.

---

## EDUCATIONAL NOTES FOR COREWEAVE EMPLOYEES

### Why This Matters
Understanding these technologies isn't just trivia—it's how we sell, deploy, and optimize infrastructure for customers:

1. **GPUs:** Know which GPU fits which workload (L4 for inference, H100 for training)
2. **Cooling:** Understand PUE impact on customer bills and datacenter capacity
3. **Networking:** Explain why multi-node training costs more (IB/NVLink fabric)

### Customer Conversations
- "Why is H100 instance more expensive?" → Liquid cooling + NVLink + HBM3
- "Can I train 70B model on 4× L40S?" → No, need 4× H200 or tensor parallelism
- "What's the ROI on InfiniBand?" → If you're doing multi-node training, it pays for itself in week 1

### Competitive Edge
CoreWeave's advantage:
1. First to market with H200 (Dec 2023)
2. Deploying GB200 NVL72 in 2025
3. Kubernetes-native orchestration (vs AWS/Azure's clunky VM model)
4. PUE 1.22-1.28 (vs industry average 1.6-1.8)

---

*Last Updated: October 2025*  
*Document Version: 1.0*  
*Prepared for: GPU Tycoon Game Development*

