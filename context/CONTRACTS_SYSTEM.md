# Contracts System - Implementation Summary

## Overview
Added a realistic enterprise contract system inspired by CoreWeave's business model (Meta, Microsoft, OpenAI deals). Players can now sign long-term contracts that **reserve GPU capacity** in exchange for **guaranteed passive income**.

## Core Mechanic: Capacity Management

### **The Trade-Off**
- **Spot Market** (Current jobs): Flexible, can process any job, variable income
- **Reserved Capacity** (Contracts): GPUs locked to contracts, guaranteed passive income, no flexibility

This mirrors real GPU cloud provider business models where companies like CoreWeave balance:
- Spot pricing for startups/researchers (flexible, on-demand)
- Reserved capacity for enterprise customers (Meta, Microsoft) with long-term commitments

---

## Features Implemented

### 1. **Capacity Tracking (Top of UI)**
```
🖥️ Capacity: 20 Available / 30 Reserved / 50 Total GPUs
[████████████████░░░░░░░░] (Green = Available, Purple = Reserved)
```

- **Visual bar** showing capacity allocation
- Real-time updates as contracts are signed
- Reserved GPUs cannot be used for spot jobs

### 2. **Contracts Tab in Shop**
New "🤝 Contracts" tab with three sections:

#### **Active Contracts** (Purple)
- Shows currently running contracts
- Displays passive income earned
- Shows remaining duration
- Lists reserved GPUs

#### **In Negotiation** (Orange)
- Contracts being pursued
- Progress bar showing negotiation completion
- Investment tracker (how much $ invested so far)
- "Invest $5K" buttons to advance progress

#### **Available Deals** (Green/Gray)
- Unlocked contracts player is eligible for
- Shows requirements (GPUs, networking, cooling, revenue)
- Red/green indicators for met/unmet requirements
- "Start Negotiation" button when eligible

### 3. **Four Enterprise Contracts**

#### **OpenAI - Spot Capacity Reserve**
- **Requires:** 20+ GPUs, 10+ H100s, $50K revenue
- **Reserves:** 20 GPUs
- **Income:** $8,000/month
- **Negotiation Cost:** $15,000
- **Duration:** 3 months
- **Unlocks:** Early game (when you hit 20 GPUs)

#### **Meta - LLaMa 4 Training Cluster**
- **Requires:** 50+ GPUs, 40+ H100s, InfiniBand, $200K revenue
- **Reserves:** 50 GPUs
- **Income:** $35,000/month
- **Negotiation Cost:** $40,000
- **Duration:** 6 months
- **Teaching:** "Big deals need serious infrastructure"

#### **Microsoft - Azure Overflow Capacity**
- **Requires:** 100+ GPUs, 80+ H100s, InfiniBand, Liquid Cooling, $500K revenue
- **Reserves:** 100 GPUs
- **Income:** $95,000/month
- **Negotiation Cost:** $100,000
- **Duration:** 12 months
- **Teaching:** "Enterprise contracts = whale deals"

#### **Anthropic - Claude Training Reserve**
- **Requires:** 150+ GPUs, 120+ H100s, NVLink Fabric, Liquid Cooling, $1M revenue
- **Reserves:** 150 GPUs
- **Income:** $180,000/month
- **Negotiation Cost:** $200,000
- **Duration:** 18 months
- **Endgame:** Massive infrastructure challenge

---

## Gameplay Flow

### **Phase 1: Early Game (1-20 GPUs)**
- Focus on spot market jobs
- Build up infrastructure
- OpenAI contract appears at 20 GPUs

### **Phase 2: First Contract (20-50 GPUs)**
- Decide: "Should I sign OpenAI deal?"
- If yes: Invest $15K, reserve 20 GPUs, get $8K/month passive
- Trade-off: Less flexibility but stable income
- **Teaching moment:** "Why is my queue backing up? Oh, 20 GPUs are reserved!"

### **Phase 3: Scaling (50-100 GPUs)**
- Meta deal unlocks
- Need InfiniBand to qualify
- Bigger decision: Lock 50 GPUs for $35K/month?
- Balancing act: Reserve vs. spot market

### **Phase 4: Enterprise Scale (100+ GPUs)**
- Microsoft and Anthropic deals unlock
- Strategic choices: "Can I afford to reserve 100 GPUs?"
- Passive income becomes significant portion of revenue
- **Real business model:** Mix of reserved and spot capacity

---

## Technical Implementation

### **Backend (Python)**

#### **`game/contracts.py`**
- `Contract` class: Individual contract state
- `ContractManager`: Manages all contracts
- Tracks negotiation progress, reserved GPUs, passive income
- Integration with game state

#### **`game/game_state.py`**
- Added `ContractManager` to game state
- Modified scheduler to exclude reserved GPUs from job allocation
- Added passive income calculations
- New methods: `start_contract_negotiation()`, `invest_in_contract()`
- Capacity tracking in `to_dict()` output

#### **`app.py`**
- New API endpoints:
  - `POST /api/action` with `start_contract_negotiation`
  - `POST /api/action` with `invest_in_contract`

### **Frontend (JavaScript)**

#### **`templates/index.html`**
- Capacity bar UI at top
- "🤝 Contracts" tab in shop

#### **`static/css/style.css`**
- Capacity bar styling (green for available, purple for reserved)
- Contract card styles (different colors for active/negotiating/locked)
- Progress bars for negotiation
- Responsive design

#### **`static/js/ui.js`**
- `updateCapacity()`: Updates capacity bar
- `renderContractsShop()`: Renders contract cards
- `createContractCard()`: Dynamic contract UI based on state
- Real-time progress updates

#### **`static/js/game.js`**
- `startContractNegotiation()`: Start negotiating a deal
- `investInContract()`: Invest money to advance negotiation
- Auto-updates UI after contract actions

---

## Key Teaching Moments

### **1. Capacity vs. Revenue Trade-Off**
"Do I reserve GPUs for guaranteed income or keep them flexible for spot market?"

### **2. Infrastructure Requirements**
"I can't land the Meta deal without 50 H100s and InfiniBand!"

### **3. Long-term Planning**
"Contracts last 3-18 months. This is a strategic commitment."

### **4. Real Business Model**
"CoreWeave's actual business is balancing spot pricing vs. reserved capacity for customers like Microsoft and Meta."

### **5. Growth Pressure**
"My contract expires in 1 month. Do I renew or go back to spot market?"

---

## Visual Design

### **Capacity Bar**
```
🖥️ Capacity: 30 Available / 20 Reserved / 50 Total GPUs
[████████████░░░░░░░░]
 Green     Purple
```

### **Contract Card (Active)**
```
┌─────────────────────────────────────┐
│ 🔷 Meta                    [ACTIVE] │
│ LLaMa 4 Training Cluster            │
│                                      │
│ Reserves: 50 GPUs  | Income: $35K/mo│
│ Duration: 6 months | Investment: $40K│
│                                      │
│ 💰 Passive Income                   │
│    $35,000/month                    │
│    5 months remaining                │
└─────────────────────────────────────┘
```

### **Contract Card (Negotiating)**
```
┌─────────────────────────────────────┐
│ 🔷 Meta              [NEGOTIATING]  │
│ LLaMa 4 Training Cluster            │
│                                      │
│ Progress: 60%    $24K / $40K        │
│ [████████░░░░░░]                    │
│                                      │
│ [Invest $5,000]                     │
└─────────────────────────────────────┘
```

---

## Balancing Notes

### **Contract Income vs. Spot Market**
- **Spot market job:** ~$45/job, 8 seconds = ~$20,250/hour per GPU (100% utilization)
- **Contract income:** $8,000/month = ~$11/hour per reserved GPU
- **Why contracts are valuable:**
  - Guaranteed income (no SLA risk)
  - Frees up mental load (passive)
  - Demonstrates real business model
  - Strategic depth (long-term commitment)

### **Negotiation Costs**
- OpenAI: $15K (5-10 jobs worth)
- Meta: $40K (20-30 jobs worth)
- Microsoft: $100K (serious investment)
- Anthropic: $200K (endgame)

Player must **invest upfront** to unlock passive income stream.

---

## Future Enhancements (Optional)

### **Contract Renewals**
- "Your Meta contract expires in 30 seconds. Renew for $10K?"

### **SLA Penalties**
- Miss uptime requirements → lose contract income

### **Dynamic Pricing**
- Contract income increases if you have rare GPUs (B200, GB200)

### **Multiple Active Contracts**
- Sign OpenAI + Meta simultaneously
- Complex capacity juggling

### **Contract Events**
- "Meta wants to extend contract for 3 more months at +20% income"
- "Microsoft is unhappy with uptime, -10% income penalty"

---

## Testing the Feature

1. **Start game** - Navigate to http://localhost:5000
2. **Buy GPUs** - Get 20+ GPUs to unlock OpenAI contract
3. **Open Contracts tab** - Click "🤝 Contracts" in shop
4. **Start negotiation** - Click "Start Negotiation" on OpenAI
5. **Invest money** - Click "Invest $5K" 3 times (total $15K)
6. **Contract activates** - See 20 GPUs reserved, capacity bar updates
7. **Passive income** - Watch cash increase from contract income
8. **Queue impact** - Notice fewer GPUs available for spot jobs

---

## Summary

✅ **Hyper-realistic:** Based on actual CoreWeave business model
✅ **Simple mechanic:** Reserve GPUs = passive income
✅ **Strategic depth:** Flexibility vs. guaranteed revenue
✅ **Educational:** Teaches enterprise GPU cloud economics
✅ **Fun trade-offs:** "Do I sign the Meta deal or stay flexible?"

The contracts system adds a **second revenue stream** and forces players to make **strategic capacity decisions** just like real GPU cloud providers!

