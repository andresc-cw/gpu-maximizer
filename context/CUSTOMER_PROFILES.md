# Customer Profiles for GPU Tycoon
## Simplified to 2 Job Types: Inference & Training

---

## INFERENCE JOBS (Small - 1 GPU)
*Short, latency-sensitive workloads for real-time AI applications*

### 1. **QueryMind AI**
- **Company Type:** AI-powered search engine
- **Workload:** Real-time search query processing and answer generation
- **VRAM Needs:** 8-16 GB per query
- **SLA Requirements:** Extremely tight (sub-second response times)
- **Why GPU Tycoon:** Low-latency inference for millions of daily searches

### 2. **ChatBuddy Corp**
- **Company Type:** Conversational AI platform
- **Workload:** Real-time chatbot inference for personalized character interactions
- **VRAM Needs:** 12-16 GB per session
- **SLA Requirements:** Strict (users expect instant responses)
- **Why GPU Tycoon:** High-throughput inference for concurrent conversations

### 3. **PixelFlow Studio**
- **Company Type:** Creative AI tools (video, image generation)
- **Workload:** Real-time AI video editing and generation inference
- **VRAM Needs:** 12-16 GB per request
- **SLA Requirements:** Tight (creative tools need responsive feedback)
- **Why GPU Tycoon:** Burst capacity for viral product launches

### 4. **ModelHub Systems**
- **Company Type:** AI model hub and inference API
- **Workload:** On-demand model inference for thousands of deployed models
- **VRAM Needs:** 8-12 GB per inference call
- **SLA Requirements:** Moderate (API uptime SLAs)
- **Why GPU Tycoon:** Elastic scaling for unpredictable API traffic

### 5. **VoiceGen Labs**
- **Company Type:** AI voice synthesis platform
- **Workload:** Real-time text-to-speech generation
- **VRAM Needs:** 8-12 GB per audio generation
- **SLA Requirements:** Strict (voice cloning needs to be instant)
- **Why GPU Tycoon:** Low-latency inference for voice applications

### 6. **DreamRender AI** *(Inference side)*
- **Company Type:** Open-source AI image generation
- **Workload:** Image generation API inference
- **VRAM Needs:** 12-16 GB per image
- **SLA Requirements:** Moderate (users tolerate 3-5 second waits)
- **Why GPU Tycoon:** Cost-effective inference at scale

---

## TRAINING JOBS (Large - 4 GPUs)
*Long-running, high-VRAM workloads for AI model training*

### 1. **SafetyFirst AI**
- **Company Type:** AI safety research company
- **Workload:** Large language model training and RLHF fine-tuning
- **VRAM Needs:** 40-60 GB per GPU (160-240 GB total)
- **SLA Requirements:** Research timelines (weeks to months)
- **Why GPU Tycoon:** Reserved capacity for multi-month training runs

### 2. **EnterpriseNLP Corp**
- **Company Type:** Enterprise LLM platform
- **Workload:** Multi-billion parameter language model training
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Model release schedules
- **Why GPU Tycoon:** Kubernetes-native infrastructure for ML workflows

### 3. **AutoDrive Systems**
- **Company Type:** Autonomous vehicle technology
- **Workload:** Self-driving perception model training from petabytes of road data
- **VRAM Needs:** 40-60 GB per GPU (160-240 GB total)
- **SLA Requirements:** Fleet deployment schedules
- **Why GPU Tycoon:** Data-parallel training at massive scale

### 4. **ArtGen Studio** *(Training side)*
- **Company Type:** AI art generation platform
- **Workload:** Diffusion model training and fine-tuning for new art styles
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Monthly model updates
- **Why GPU Tycoon:** Elastic training capacity without long-term CapEx

### 5. **AgentFlow AI**
- **Company Type:** General intelligence company (AI agents)
- **Workload:** Action transformer model training
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Research milestones
- **Why GPU Tycoon:** Fast iteration on experimental architectures

### 6. **PersonalAI Labs**
- **Company Type:** Personal AI assistant company
- **Workload:** Large-scale LLM pretraining and alignment
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Product launch timelines
- **Why GPU Tycoon:** Massive GPU clusters for large-scale training

### 7. **NeuralCore Research**
- **Company Type:** AI research lab
- **Workload:** Foundation model training across language, vision, and video
- **VRAM Needs:** 48-80 GB per GPU (192-320 GB total)
- **SLA Requirements:** Product roadmap milestones
- **Why GPU Tycoon:** Supplemental capacity during peak research phases

### 8. **CogniTech Labs**
- **Company Type:** Multi-modal AI research lab
- **Workload:** Multi-modal model training and reinforcement learning
- **VRAM Needs:** 48-80 GB per GPU (192-320 GB total)
- **SLA Requirements:** Research publication cycles
- **Why GPU Tycoon:** Cloud bursting for large-scale experiments

---

## CUSTOMER DISTRIBUTION BY PHASE

### Phase 1 ($0-$30K)
**Available Customers:** Inference only
- All 6 inference customers available

### Phase 2 ($30K-$150K)
**New Customers:** Training jobs start appearing (25%)
- Training customers gradually unlock
- Mix of inference (75%) and training (25%)

### Phase 3 ($150K+)
**Endgame:** Balanced workload
- Inference (40%) and Training (60%)
- All customers available

---

## GAME INTEGRATION NOTES

### Job Generation
Only 2 job types now (simplified from 3):
```python
INFERENCE_CUSTOMERS = ['QueryMind AI', 'ChatBuddy Corp', 'PixelFlow Studio', 'ModelHub Systems', 'VoiceGen Labs', 'DreamRender AI']
TRAINING_CUSTOMERS = ['SafetyFirst AI', 'EnterpriseNLP Corp', 'AutoDrive Systems', 'ArtGen Studio', 'AgentFlow AI', 'PersonalAI Labs', 'NeuralCore Research', 'CogniTech Labs']
```

### Display Format
**Inference Job Card:**
```
[INFERENCE] QueryMind AI
Search Query Processing
1 GPU | 16 GB VRAM | $50
SLA: 20s | Progress: ████░░░░ 50%
```

**Training Job Card:**
```
[TRAINING] SafetyFirst AI
LLM Model Training
4 GPUs | 50 GB VRAM each | $250
SLA: 50s | Progress: ██░░░░░░ 25%
```

### Educational Value
- **Shows real-world use cases:** Players learn what GPU compute is actually used for
- **Industry patterns:** Fictional names represent realistic AI/ML company archetypes
- **Career pathway:** Introduces players to the AI/VFX/ML industry landscape
- **Customer diversity:** Demonstrates the breadth of cloud GPU compute markets

### SLA Personality
Different customers have different tolerance for delays:
- **Strict:** QueryMind AI, ChatBuddy Corp (user-facing inference) - 20s window
- **Flexible:** SafetyFirst AI, EnterpriseNLP Corp (research timelines can slip) - 50s window

---

## LEGAL & ACCURACY NOTE

These are **fictional company names** representing realistic examples of the types of workloads that GPU cloud providers serve. The customer profiles are designed for educational purposes to teach players about:
- Real inference vs. training workloads
- VRAM requirements for different AI applications
- SLA expectations across different use cases
- The diversity of GPU compute customers

All company names and details are fictional. Any resemblance to actual companies is coincidental.

