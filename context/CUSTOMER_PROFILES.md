# Customer Profiles for GPU Tycoon
## Simplified to 2 Job Types: Inference & Training

---

## INFERENCE JOBS (Small - 1 GPU)
*Short, latency-sensitive workloads for real-time AI applications*

### 1. **Perplexity AI**
- **Company Type:** AI-powered search engine
- **Workload:** Real-time search query processing and answer generation
- **VRAM Needs:** 8-16 GB per query
- **SLA Requirements:** Extremely tight (sub-second response times)
- **Why CoreWeave:** Low-latency inference for millions of daily searches

### 2. **Character.AI**
- **Company Type:** Conversational AI platform
- **Workload:** Real-time chatbot inference for personalized character interactions
- **VRAM Needs:** 12-16 GB per session
- **SLA Requirements:** Strict (users expect instant responses)
- **Why CoreWeave:** High-throughput inference for concurrent conversations

### 3. **Runway ML**
- **Company Type:** Creative AI tools (video, image generation)
- **Workload:** Real-time AI video editing and generation inference
- **VRAM Needs:** 12-16 GB per request
- **SLA Requirements:** Tight (creative tools need responsive feedback)
- **Why CoreWeave:** Burst capacity for viral product launches

### 4. **Hugging Face**
- **Company Type:** AI model hub and inference API
- **Workload:** On-demand model inference for thousands of deployed models
- **VRAM Needs:** 8-12 GB per inference call
- **SLA Requirements:** Moderate (API uptime SLAs)
- **Why CoreWeave:** Elastic scaling for unpredictable API traffic

### 5. **ElevenLabs**
- **Company Type:** AI voice synthesis platform
- **Workload:** Real-time text-to-speech generation
- **VRAM Needs:** 8-12 GB per audio generation
- **SLA Requirements:** Strict (voice cloning needs to be instant)
- **Why CoreWeave:** Low-latency inference for voice applications

### 6. **Stability AI** *(Inference side)*
- **Company Type:** Open-source AI image generation (Stable Diffusion)
- **Workload:** Image generation API inference
- **VRAM Needs:** 12-16 GB per image
- **SLA Requirements:** Moderate (users tolerate 3-5 second waits)
- **Why CoreWeave:** Cost-effective inference at scale

---

## TRAINING JOBS (Large - 4 GPUs)
*Long-running, high-VRAM workloads for AI model training*

### 1. **Anthropic**
- **Company Type:** AI safety company (Claude AI)
- **Workload:** Large language model training and RLHF fine-tuning
- **VRAM Needs:** 40-60 GB per GPU (160-240 GB total)
- **SLA Requirements:** Research timelines (weeks to months)
- **Why CoreWeave:** Reserved capacity for multi-month training runs

### 2. **Cohere**
- **Company Type:** Enterprise LLM platform
- **Workload:** Multi-billion parameter language model training
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Model release schedules
- **Why CoreWeave:** Kubernetes-native infrastructure for ML workflows

### 3. **Waymo**
- **Company Type:** Autonomous vehicle technology (Alphabet subsidiary)
- **Workload:** Self-driving perception model training from petabytes of road data
- **VRAM Needs:** 40-60 GB per GPU (160-240 GB total)
- **SLA Requirements:** Fleet deployment schedules
- **Why CoreWeave:** Data-parallel training at massive scale

### 4. **Midjourney** *(Training side)*
- **Company Type:** AI art generation platform
- **Workload:** Diffusion model training and fine-tuning for new art styles
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Monthly model updates
- **Why CoreWeave:** Elastic training capacity without long-term CapEx

### 5. **Adept AI**
- **Company Type:** General intelligence company (AI agents)
- **Workload:** Action transformer model training (ACT-1)
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Research milestones
- **Why CoreWeave:** Fast iteration on experimental architectures

### 6. **Inflection AI**
- **Company Type:** Personal AI company (Pi assistant)
- **Workload:** Large-scale LLM pretraining and alignment
- **VRAM Needs:** 48-60 GB per GPU (192-240 GB total)
- **SLA Requirements:** Product launch timelines
- **Why CoreWeave:** Massive GPU clusters (22,000+ H100 scale)

### 7. **OpenAI** *(Hypothetical customer)*
- **Company Type:** AI research lab (GPT, DALL-E, Sora)
- **Workload:** Foundation model training across language, vision, and video
- **VRAM Needs:** 48-80 GB per GPU (192-320 GB total)
- **SLA Requirements:** Product roadmap milestones
- **Why CoreWeave:** Supplemental capacity during peak research phases

### 8. **DeepMind** *(Hypothetical customer)*
- **Company Type:** AI research lab (AlphaFold, Gemini)
- **Workload:** Multi-modal model training and reinforcement learning
- **VRAM Needs:** 48-80 GB per GPU (192-320 GB total)
- **SLA Requirements:** Research publication cycles
- **Why CoreWeave:** Cloud bursting for large-scale experiments

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
INFERENCE_CUSTOMERS = ['Perplexity AI', 'Character.AI', 'Runway ML', 'Hugging Face', 'ElevenLabs', 'Stability AI']
TRAINING_CUSTOMERS = ['Anthropic', 'Cohere', 'Waymo', 'Midjourney', 'Adept AI', 'Inflection AI', 'OpenAI', 'DeepMind']
```

### Display Format
**Inference Job Card:**
```
[INFERENCE] Perplexity AI
Search Query Processing
1 GPU | 16 GB VRAM | $50
SLA: 20s | Progress: ████░░░░ 50%
```

**Training Job Card:**
```
[TRAINING] Anthropic
Claude Model Training
4 GPUs | 50 GB VRAM each | $250
SLA: 50s | Progress: ██░░░░░░ 25%
```

### Educational Value
- **Shows real-world use cases:** Players learn what GPU compute is actually used for
- **Brand recognition:** Familiar company names make the game more relatable
- **Career pathway:** Introduces players to the AI/VFX/ML industry landscape
- **Customer diversity:** Demonstrates the breadth of CoreWeave's market

### SLA Personality
Different customers have different tolerance for delays:
- **Strict:** Perplexity, Character.AI (user-facing inference) - 20s window
- **Flexible:** Anthropic, Cohere (research timelines can slip) - 50s window

---

## LEGAL & ACCURACY NOTE

These are **realistic examples** of the types of customers CoreWeave serves or could serve. Some are confirmed CoreWeave customers (e.g., Inflection AI's 22,000 H100 cluster), while others are representative examples for educational purposes.

For a public release, consider:
- Using fictional company names with obvious parodies ("Perplexify", "Anthropix")
- Adding a disclaimer: "Inspired by real AI/VFX companies. No affiliation or endorsement implied."
- Keeping real names for educational demos/hackathons where fair use applies

