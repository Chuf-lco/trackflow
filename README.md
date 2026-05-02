[![TrackFlow CI](https://github.com/Chuf-lco/trackflow/actions/workflows/ci.yml/badge.svg)](https://github.com/Chuf-lco/trackflow/actions/workflows/ci.yml)
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    KENYA LOGISTICS SHIPMENT TRACKING WORKFLOW                        ║
║                    (Tailored for Mombasa Port / KPA / KRA Ecosystem)                 ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────────┐
│  📍 STATUS 1: VESSEL ARRIVAL & MANIFEST                                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   Vessel ETA (Mombasa Port)                                                          │
│        │                                                                             │
│        ▼                                                                             │
│   Manifest Lodged → KWATOS + Simba Tradex                                            │
│        │                              ⚠️ FAILURE POINTS:                             │
│        ▼                              • Berthing delays up to 4 days                 │
│   Manifest vs B/L Reconciliation      • KWATOS/Tradex glitches (daily)               │
│        │                              • Timezone mismatches (UTC vs EAT)             │
│        ▼                                                                             │
│   ┌─────────────┐                                                                    │
│   │  Berthing   │──Yes──► Alert: Delay Predicted                                    │
│   │   Delay?    │                                                                    │
│   └─────────────┘──No───┐                                                            │
│                         ▼                                                            │
└──────────────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  📋 STATUS 2: CUSTOMS DECLARATION & ASSESSMENT                                       │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   Import Declaration Form (IDF) Submission                                           │
│        │                                                                             │
│        ▼                                                                             │
│   Duty Calculation: VAT 16% + RDL 2% + EAC CET                                       │
│        │                              ⚠️ FAILURE POINTS:                             │
│        ▼                              • M-Pesa / Bank payment failures               │
│   iTax Payment Confirmation           • Undervaluation penalties (post-clearance)    │
│        │                              • Document mismatches → physical inspection    │
│        ▼                                                                             │
│   ┌──────────────┐                                                                   │
│   │ Payment      │──No──► Demurrage Counter Starts ──► Retry Payment                │
│   │ Received?    │                                                                   │
│   └──────────────┘──Yes──► KRA Risk Assessment                                       │
│                              │                                                       │
│                              ▼                                                       │
│                        ┌─────────┬─────────┬─────────┐                               │
│                        │  GREEN  │ YELLOW  │   RED   │                               │
│                        │ No Insp │  Scan   │ Manual  │                               │
│                        └────┬────┴────┬────┴────┬────┘                               │
│                             └─────────┴─────────┘                                    │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  🔍 STATUS 3: PHYSICAL VERIFICATION & RELEASE                                        │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   Customs Release Order (CRO) Issued                                                 │
│        │                                                                             │
│        ▼                                                                             │
│   ┌─────────────────────────────────────────────────────────┐                        │
│   │              VERIFICATION TYPE                          │                        │
│   │  ┌─────────┐    ┌─────────┐    ┌─────────────────────┐  │                        │
│   │  │  GREEN  │    │  SCAN   │    │  MANUAL STRIPPING   │  │                        │
│   │  │Channel  │    │   NII   │    │      at CFS         │  │                        │
│   │  │         │    │         │    │                     │  │                        │
│   │  │ No Insp │    │ Scanner │    │ • Theft risk flag   │  │  ⚠️ FAILURE POINTS:   │
│   │  │         │    │ (often  │    │ • Photo doc req'd   │  │  • Scanner downtime   │
│   │  └────┬────┘    │ broken) │    │ • Small items stolen│  │  • CFS auto-alloc     │
│   │       └─────────┴────┬────┘    └──────────┬──────────┘  │  • Theft at stripping │
│   │                      └────────────────────┘             │                        │
│   └─────────────────────────────────────────────────────────┘                        │
│                              │                                                       │
│                              ▼                                                       │
│   CFS Nomination Check ──► Was CFS nominated at origin?                              │
│        │                              (Dec 2025 mandate: KPA ceased domestic clear)  │
│        ▼                                                                             │
│   ┌─────────────┐                                                                    │
│   │   Nominated │──Yes──► Known CFS, predictable timeline                            │
│   │   at Load?  │                                                                    │
│   └─────────────┘──No───► Auto-allocated by CFS Association ──► Unpredictable delay   │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  🚛 STATUS 4: CONTAINER EXIT & INLAND TRANSIT                                        │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   KPA Gate Pass & Exit                                                               │
│        │                              ⚠️ FAILURE POINTS:                             │
│        ▼                              • Gate congestion: 4-6 hour queues             │
│   Truck GPS / ECTS Seal Activation    • GPS dead zones (Northern Corridor)           │
│        │                              • Fuel theft overnight                         │
│        ▼                              • Unofficial roadblocks                        │
│   ┌─────────────┐                                                                    │
│   │ GPS Offline │──Yes──► Queue Events for Sync ──► Resume when online              │
│   │   Mode?     │                                                                    │
│   └─────────────┘──No───┐                                                            │
│                         ▼                                                            │
│   Route Monitoring: Mombasa ─────────────────────────────────────► Nairobi / Border  │
│        │                                                                             │
│        ├──► Checkpoint: Mariakani                                                    │
│        ├──► Checkpoint: Voi                                                          │
│        ├──► Weighbridge: Athi River                                                  │
│        │                                                                             │
│        ▼                                                                             │
│   ┌─────────────┐                                                                    │
│   │ Route Dev   │──Yes──► Geo-Fence Alert: Possible Diversion / Theft Risk          │
│   │ > 5km?      │                                                                    │
│   └─────────────┘──No────────────────────────────────────────────┐                   │
│                                                                  ▼                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                                                   │
                                                                   ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  ✅ STATUS 5: DELIVERY CONFIRMATION & POD                                            │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   Arrival at Consignee / CFS / ICD                                                   │
│        │                                                                             │
│        ▼                                                                             │
│   Container Offload & Inspection                                                     │
│        │                              ⚠️ FAILURE POINTS:                             │
│        ▼                              • POD disputes (paper gets lost)               │
│   Photo POD + Digital Signature       • Damage claims without evidence fail          │
│        │                              • KRA entry non-closure → audit liability       │
│        ▼                                                                             │
│   ┌─────────────┐                                                                    │
│   │ Damage or   │──Yes──► Damage Claim Workflow ──► Photo Evidence ──► Insurance     │
│   │ Discrepancy?│                                                                    │
│   └─────────────┘──No───┐                                                            │
│                         ▼                                                            │
│   KRA Entry Closure (Clearing Agent Responsibility)                                    │
│        │                                                                             │
│        ▼                                                                             │
│   ┌─────────────┐                                                                    │
│   │ Entry Open  │──Yes──► ALERT: Entry not closed > 7 days ──► Escalate to Agent    │
│   │ > 7 Days?   │                                                                    │
│   └─────────────┘──No───► FINAL STATUS: DELIVERED ✅                                 │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                         CROSS-CUTTING DATA MODEL FIELDS                              ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  Every status transition MUST capture:                                               ║
║  • timestamp (EAT - Nairobi time, UTC+3)                                             ║
║  • geo_location (lat/long, even if approximate)                                      ║
║  • actor (driver_pin / agent_kra_pin / officer_id / system)                          ║
║  • source_system (KWATOS / Tradex / GPS / Manual / ECTS)                             ║
║  • evidence_urls (photo / document / signature)                                      ║
║  • offline_synced (boolean - CRITICAL for Kenyan connectivity)                       ║
║  • exception_reason (nullable, required if transition time > threshold)              ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                         KENYA-SPECIFIC UI REQUIREMENTS                               ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  ☑ Low-bandwidth mode (<100KB loads) for 2G/expensive data                           ║
║  ☑ M-Pesa payment status as first-class citizen (not just a note)                    ║
║  ☑ Swahili/English bilingual labels for driver-facing interfaces                     ║
║  ☑ WhatsApp Business API for status alerts (Kenya's B2B default)                     ║
║  ☑ Print-friendly views (paper still rules in Kenyan logistics)                      ║
║  ☑ Demurrage calculator with daily countdown and cost projection                     ║
║  ☑ KRA compliance dashboard: open entries, deadlines, audit flags                    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
