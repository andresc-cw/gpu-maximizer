TODO:
- Remove all the random emojis
- Incorporate capacity planning concepts? 
- Research pricing methods: spot, reserved, peak? see coreweave's current billing
    - Research button -> unlock new pricing methods, new datacenter technologies (Level 1 -> etc...)
    - Marketing button -> unlock newer supply (Level 1 -> etc...)
- Add stuff related to object storage? Maybe you can sell that too, and have the billing relate to itA
- Review the game mechanics, ensure it makes sense and it's fun
    - What's the manual version of "Make Paperclips"
    - What's the goal? First to open the final contract?
    - How do players beat other players?
    - Ensure the network and cooling actually relate to the gameplay
- see capacity dashboard:
    - add RI, Spot On Demand concepts
    - add installed vs. sellable concepts (some machines break very once in a while)
    - put GPUs in specific datacenter region

INFRA:
- Deploy it somewhere

LATER:
- Simplify the mechanic more

DONE:
- Fixed speed mechanic (1x/2x/5x) to work like Universal Paperclips - everything speeds up proportionally
- Added company logos to enterprise contracts (fictional companies)
- Marketing tab -> improve the job queue ✅
    - Created 15 marketing upgrades (Account Execs, CMO, DevRel, conferences, billboards, etc.)
    - Upgrades increase job spawn rate (+15% to +40%)
    - Upgrades increase job value (+8% to +40%)
    - Some upgrades add SLA buffer time
    - Integrated throughout game: backend (marketing.py, game_state.py, jobs.py) and frontend (HTML, UI.js)
    - Unlock progression based on revenue milestones ($20K to $800K)
    - Educational descriptions with real-world context (salaries, costs, ROI)
- Clean up the power ups, maybe remove them