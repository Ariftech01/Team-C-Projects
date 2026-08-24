/**
 * Construction Intelligent Hub (CIH) - Reusable AI Prompt Templates
 *
 * Centralized registry of system & user prompt templates.
 * Loaded as a classic browser script (not an ES module), so the guardrail
 * is a global constant rather than `export const`.
 */

const CIH_OUT_OF_SCOPE_REFUSAL = '⚠️ Out of Scope Request: I am specialized exclusively in civil engineering, construction management, material takeoffs, and site risk analysis. Please reframe your query around your project data or site logistics.';

const SYSTEM_GUARDRAIL_PROMPT = `
YOU ARE THE AI BRAIN OF "CONSTRUCTION INTELLIGENT HUB" (CIH).
YOUR SOLE PURPOSE IS TO ASSIST WITH CIVIL ENGINEERING, SITE SAFETY, MATERIAL ESTIMATION, RISK ANALYSIS, BUDGET FORECASTING, AND CONSTRUCTION PROJECT LOGISTICS.

STRICT OPERATIONAL DIRECTIVES:
1. TOPIC BOUNDARY:
   - ALLOWED: Construction site management, material takeoffs (concrete, rebar, brickwork, sand), site risk scoring, budget variance, vendor logs, structural safety, equipment logistics, civil engineering codes, project schedules.
   - DENIED: General knowledge, coding outside construction software, sports, politics, history, pop culture, creative writing, recipe advice, general conversational chitchat.

2. MANDATORY REFUSAL PROTOCOL:
   If the user query or uploaded file content is OUT OF SCOPE, you MUST IMMEDIATELY respond with this EXACT structure and nothing else:
   "⚠️ Out of Scope Request: I am specialized exclusively in civil engineering, construction management, material takeoffs, and site risk analysis. Please reframe your query around your project data or site logistics."

3. CONTEXT COMPLIANCE:
   When project context JSON or document text is provided, base your analysis strictly on that data. Do not invent fictitious site metrics, non-existent project costs, or unverified structural specs.
`;

const CIH_SCOPE_ALLOW_TERMS = [
    'civil', 'construction', 'infrastructure', 'site', 'jobsite', 'job site',
    'engineering', 'structural', 'geotechnical', 'foundation', 'excavation',
    'concrete', 'rebar', 'reinforcement', 'tmt', 'steel', 'cement', 'brick',
    'brickwork', 'sand', 'aggregate', 'bitumen', 'asphalt', 'formwork',
    'shuttering', 'scaffolding', 'waterproofing', 'mix design', 'rcc', 'm25', 'm40',
    'beam', 'column', 'slab', 'pile', 'pier', 'viaduct', 'metro', 'highway',
    'airport', 'runway', 'bridge', 'tunnel', 'building', 'facade', 'mep', 'hvac',
    'material', 'takeoff', 'take-off', 'boq', 'bill of quantities', 'quantity survey',
    'dpr', 'progress report', 'manpower', 'workforce', 'labor', 'labour',
    'budget', 'variance', 'overrun', 'forecast', 'cashflow', 'contingency',
    'vendor', 'supplier', 'procurement', 'inventory', 'stock', 'logistics',
    'risk', 'mitigation', 'safety', 'osha', 'hazard', 'incident',
    'equipment', 'crane', 'excavator', 'telemetry', 'rfid', 'schedule',
    'milestone', 'deadline', 'delay', 'liquidated', 'tender', 'contract',
    'subcontractor', 'contractor', 'epc', 'invoice', 'gst', 'clause',
    'project', 'portfolio', 'client', 'sow', 'scope of work', 'is 456', 'is 1786',
    'primavera', 'ms project', 'revit', 'autocad', 'bim', 'staad', 'etabs'
];

const CIH_SCOPE_DENY_TERMS = [
    'cricket', 'football', 'soccer', 'nba', 'ipl', 'tennis', 'hockey', 'fifa',
    'world cup', 'olympics', 'sports', 'match score', 'movie', 'netflix',
    'bollywood', 'hollywood', 'celebrity', 'pop culture', 'song lyrics',
    'album', 'anime', 'video game', 'playstation', 'election', 'politics',
    'president', 'prime minister', 'political party', 'recipe', 'cookbook',
    'cooking', 'baking', 'joke', 'riddle', 'poem', 'lyrics', 'short story',
    'horoscope', 'astrology', 'dating advice', 'gossip'
];

const CIH_SCOPE_CODE_TERMS = [
    'python', 'javascript', 'typescript', 'java ', 'c++', 'html', 'css',
    'react', 'node.js', 'golang', 'ruby on rails', 'write a script',
    'write code', 'programming', 'leetcode', 'debug this'
];

function cihEscapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function cihCountTermHits(text, terms) {
    const source = String(text || '');
    return terms.filter((term) => {
        const pattern = new RegExp(`(?:^|[^a-z0-9])${cihEscapeRegExp(term)}(?:[^a-z0-9]|$)`, 'i');
        return pattern.test(source);
    });
}

function cihProjectNameHits(text) {
    if (typeof CIH_DATASET === 'undefined' || !Array.isArray(CIH_DATASET.projects)) return [];
    const lower = String(text || '').toLowerCase();
    return CIH_DATASET.projects.filter((p) => {
        const title = String(p.title || '').toLowerCase();
        const id = String(p.id || '').toLowerCase();
        const city = String(p.city || '').toLowerCase();
        return (title && lower.includes(title)) || (id && lower.includes(id)) || (city && lower.includes(city) && /project|site|budget|risk|material/.test(lower));
    });
}

function cihHasConstructionDomain(text) {
    return cihCountTermHits(text, CIH_SCOPE_ALLOW_TERMS).length > 0 || cihProjectNameHits(text).length > 0;
}

function cihIsInternalConstructionTask(text) {
    const lower = String(text || '').toLowerCase();
    return lower.includes('you are the ai brain of "construction intelligent hub"')
        || lower.includes('cih material ai')
        || lower.includes('material estimation report')
        || lower.includes('document intelligence report')
        || lower.includes('construction risk analysis report')
        || lower.includes('project budget estimation report')
        || lower.includes('real-time application context dataset')
        || lower.includes('senior construction operations analyst');
}

function composeGuardedSystemPrompt(roleBlock) {
    const extra = String(roleBlock || '').trim();
    if (extra.includes('YOUR SOLE PURPOSE IS TO ASSIST WITH CIVIL ENGINEERING')) {
        return extra;
    }
    return `${SYSTEM_GUARDRAIL_PROMPT.trim()}\n\n${extra}`.trim();
}

function isQueryInScope(text, history) {
    const query = String(text || '').trim();
    if (!query) return false;
    if (cihIsInternalConstructionTask(query)) return true;

    const allowHits = cihCountTermHits(query, CIH_SCOPE_ALLOW_TERMS);
    const denyHits = cihCountTermHits(query, CIH_SCOPE_DENY_TERMS);
    const codeHits = cihCountTermHits(query, CIH_SCOPE_CODE_TERMS);
    const projectHits = cihProjectNameHits(query);
    const constructionDomain = allowHits.length > 0 || projectHits.length > 0;

    if (denyHits.length > 0 && !constructionDomain) return false;
    if (denyHits.length > 0 && constructionDomain && denyHits.length >= allowHits.length && projectHits.length === 0) {
        return false;
    }
    if (codeHits.length > 0 && !constructionDomain) return false;
    if (constructionDomain) return true;

    const prior = Array.isArray(history) ? history : [];
    const priorInScope = prior.some((turn) => cihHasConstructionDomain(turn && (turn.content || turn)));
    const wordCount = query.split(/\s+/).filter(Boolean).length;
    if (priorInScope && wordCount <= 10 && denyHits.length === 0 && codeHits.length === 0) {
        return true;
    }
    return false;
}

function evaluateConstructionDocument(docTitle, docContent) {
    const title = String(docTitle || '');
    const content = String(docContent || '').trim();
    const combined = `${title}\n${content}`;
    if (!content || content.length < 40) {
        return { valid: false, inScope: false, message: CIH_OUT_OF_SCOPE_REFUSAL };
    }

    const preset = (typeof CIH_PROMPTS !== 'undefined' && typeof CIH_PROMPTS.detectDocumentPreset === 'function')
        ? CIH_PROMPTS.detectDocumentPreset(title, content)
        : 'general';
    const allowHits = cihCountTermHits(combined, CIH_SCOPE_ALLOW_TERMS);
    const denyHits = cihCountTermHits(combined, CIH_SCOPE_DENY_TERMS);
    const uniqueAllow = [...new Set(allowHits.map((t) => t.toLowerCase()))];

    if (denyHits.length >= 2 && uniqueAllow.length < 2) {
        return { valid: false, inScope: false, message: CIH_OUT_OF_SCOPE_REFUSAL };
    }

    const strongConstructionPreset = preset === 'boq' || preset === 'dpr';
    const contractOrInvoice = preset === 'contract' || preset === 'invoice';
    const enoughDomain = uniqueAllow.length >= 3 || strongConstructionPreset || (contractOrInvoice && uniqueAllow.length >= 2);

    if (!enoughDomain) {
        return { valid: false, inScope: false, message: CIH_OUT_OF_SCOPE_REFUSAL };
    }
    return { valid: true, inScope: true, preset: preset, hits: uniqueAllow };
}

const CIH_PROMPTS = {
    /**
     * Dynamic Live Web App Context Generator
     */
    getLiveWebappContext: () => {
        if (typeof CIH_DATASET === 'undefined') return '';

        const fmt = (n) => (typeof cihFormatMoney === 'function' ? cihFormatMoney(n) : n);
        const titleOf = (id) => (typeof cihProjectTitle === 'function' ? cihProjectTitle(id) : id);
        const matStatus = (m) => (typeof cihMaterialStatus === 'function' ? cihMaterialStatus(m).status : '');

        const snapOf = (id) => (typeof getProjectSnapshot === 'function'
            ? getProjectSnapshot(id)
            : (CIH_DATASET.getProjectSnapshot && CIH_DATASET.getProjectSnapshot(id)));

        const projects = (CIH_DATASET.projects || []).map(p => {
            const snap = snapOf(p.id) || p;
            return `- Project: "${snap.title}" (ID: ${snap.id}) | Client: ${snap.client || '—'} | Location: ${snap.city} | Status: ${snap.status} | Budget: ${snap.formattedBudget || fmt(snap.budget)} | Spent: ${snap.formattedSpent || fmt(snap.spent)} (${snap.spentPercent || 0}%) | Remaining: ${snap.formattedRemaining || fmt(snap.remainingBudget)} | Deadline: ${snap.deadline || p.deadline} | Progress: ${snap.progressPercent}% | Risk Level: ${snap.riskLevel || 'Low'} | Open Risks: ${(snap.risks || []).length} | Materials: ${(snap.materials || []).length} | Expenses: ${(snap.expenses || []).length} | Team Size: ${snap.teamCount || p.totalTeamCount}`;
        }).join('\n');

        const stats = CIH_DATASET.dashboardStats || {};
        const budget = CIH_DATASET.budgetOverview || {};
        const statsSummary = `Portfolio Summary: ${stats.totalProjects?.count ?? 0} Total Active Projects (${stats.running?.count ?? 0} Running, ${stats.delayed?.count ?? 0} On Hold/Delayed, ${stats.highRisk?.count ?? 0} High Risk, ${stats.completed?.count ?? 0} Completed). Total Portfolio Budget: ${budget.totalPortfolioBudget || '—'} | Total Spent: ${budget.totalSpent || '—'} | Remaining: ${budget.remainingBudget || '—'} | Variance: ${budget.variancePercent || '0%'}.`;

        const materials = (CIH_DATASET.materials || []).map(m =>
            `- Material: "${m.itemName}" | Project: "${titleOf(m.projectId)}" | Stock: ${m.quantityInStock} ${m.unit} / Required: ${m.quantityRequired} ${m.unit} | Unit Price: ${fmt(m.unitPrice)} | Status: ${matStatus(m)} | Supplier: ${m.supplier}`
        ).join('\n');

        const expenses = (CIH_DATASET.expenses || []).map(e =>
            `- Expense: "${e.title || e.vendor}" | Project: "${titleOf(e.projectId)}" | Category: ${e.category} | Amount: ${fmt(e.amount)} | Status: ${e.paymentStatus} | Date: ${e.date} | Vendor: ${e.vendor}`
        ).join('\n');
        const budgetSummary = `Financial State: Total Allocated = ${budget.totalPortfolioBudget} | Total Spent = ${budget.totalSpent} | Remaining = ${budget.remainingBudget} | Variance: ${budget.variancePercent} | Overrun Risk: ${budget.overrunRisk}\nLogged Expense Transactions:\n${expenses}`;

        const equipment = (CIH_DATASET.equipment || []).map(e =>
            `- Heavy Machine: "${e.assetName}" (${e.unitCode}) | Project: "${titleOf(e.projectId)}" | Health: ${e.engineHealthPct}% | Operating Hours: ${e.operatingHours} hrs | Fuel Rate: ${e.fuelRateLph} L/hr | Maintenance Due: ${e.maintenanceDueHrs} hrs | Status: ${e.status} | Operator: ${e.operator}`
        ).join('\n');

        const team = (CIH_DATASET.team || []).map(t =>
            `- Team Member: "${t.name}" | Role: ${t.role} (${t.category || '—'}) | Projects: ${(t.assignedProjects || []).map(titleOf).join(', ') || 'Unassigned'} | Email: ${t.email} | Phone: ${t.phone || '—'} | Access Level: ${t.accessLevel || '—'}`
        ).join('\n');

        const reports = (CIH_DATASET.reports || []).map(r =>
            `- Report: "${r.reportTitle}" (${r.id}) | Type: ${r.reportType} | Project: "${titleOf(r.projectId)}" | Author: ${r.generatedBy} | Date: ${r.generatedDate} | Format: ${r.format}`
        ).join('\n');

        const risks = (CIH_DATASET.risks || []).map(r =>
            `- Risk (${r.id}): "${r.riskTitle}" | Project: "${titleOf(r.projectId)}" | Category: ${r.category} | Probability: ${r.probability} | Impact: ${r.impact} | Severity: ${r.severityScore} | Status: ${r.status} | Owner: ${r.assignedTo} | Mitigation: ${r.mitigationPlan}`
        ).join('\n');

        const settings = CIH_DATASET.settings || {};
        const settingsLine = `Company: ${settings.companyName || 'CIH'} | Address: ${settings.companyAddress || '—'} | Currency: ${settings.currency || 'INR'} | Tax: ${settings.taxRatePct || 0}% | Labor rate/day: ${fmt(settings.laborRatePerDay || 0)}`;

        return `REAL-TIME APPLICATION CONTEXT DATASET:
${settingsLine}
${statsSummary}

ACTIVE INFRASTRUCTURE PROJECTS (${(CIH_DATASET.projects || []).length}):
${projects}

RISK REGISTER (${(CIH_DATASET.risks || []).length}):
${risks}

MATERIAL INVENTORY (${(CIH_DATASET.materials || []).length}):
${materials}

BUDGET & EXPENSE BREAKDOWN:
${budgetSummary}

HEAVY EQUIPMENT FLEET (${(CIH_DATASET.equipment || []).length}):
${equipment}

TEAM DIRECTORY (${(CIH_DATASET.team || []).length}):
${team}

PROJECT AUDIT REPORTS (${(CIH_DATASET.reports || []).length}):
${reports}`;
    },

    /**
     * Guarded conversational system prompt — construction expert only
     */
    get systemPrompt() {
        return composeGuardedSystemPrompt(`You are CIH Assistant, the Construction Intelligent Hub civil engineering and construction-management expert (llama3.2).

BEHAVIORAL GUIDELINES:
1. STAY IN DOMAIN: Answer only civil engineering, site safety, materials, risk, budget, equipment, contracts, and project-logistics questions.
2. CONSTRUCTION EXPLANATIONS: If the user asks a construction question (e.g. "What is reinforced concrete?", "How can I reduce construction cost?", "Explain budget utilization"), provide a practical expert explanation.
3. PROJECT ANALYSIS: If the user asks about projects in the live dataset, analyze that dataset only and do not invent missing figures.
4. ACCURACY: If a requested project or metric is not in the dataset, say it is unavailable in the active workspace.
5. FOLLOW-UP: Maintain continuity only for in-scope construction threads.
6. FORMATTING: Use clean markdown headers, bullet points, and bold text.
7. OUT OF SCOPE: If the query is sports, politics, pop culture, general coding, entertainment, recipes, or chitchat, reply with the exact mandatory refusal and nothing else.

${CIH_PROMPTS.getLiveWebappContext()}`);
    },

    materialEstimation: (params, legacySpecs = "") => {
        if (typeof params === 'string') {
            return `Project: ${params || "Active Job Site"}
Specifications: ${legacySpecs || "Standard civil infrastructure building specifications"}
Tasks: Estimate material quantities (Cement, Concrete, Steel Rebar, Sand, Aggregates, Paint) with wastage and INR costs.`;
        }

        const p = params || {};
        const projName   = p.projectName || p.projName || "Active Project Site";
        const loc        = p.location    || "Metro Infrastructure Zone";
        const pType      = p.projectType || p.pType    || "Commercial Infrastructure";
        const bType      = p.buildingType|| p.bType    || "RCC Frame Structure";
        const areaSqFtRaw   = Number(p.areaSqFt)  || 50000;
        const numFloors     = Number(p.numFloors) || 12;
        const totalSqFtRaw  = p.totalAreaSqFt ? Number(p.totalAreaSqFt) : areaSqFtRaw * numFloors;
        const totalSqM      = (totalSqFtRaw / 10.764).toFixed(0);
        const soil       = p.soil       || "Clayey Soil (High Plasticity)";
        const foundation = p.foundation || "Raft / Mat Foundation";
        const wastage    = p.wastageBuffer || "8%";
        const mixRatio   = p.mixRatio   || "M25 (1:1:2)";
        const unitSystem = p.unitSystem || "Metric (SI Units)";

        // Pre-compute concrete volume for reference
        const concreteM3 = Math.round(totalSqM * 0.15 * 1.3);  // slab + beam/column coefficient
        const cementBagsNet = Math.round(concreteM3 * 7.5);      // M25 = 7.5 bags/m³
        const steelMTnet    = Math.round(concreteM3 * 0.11);     // ~110 kg/m³ for RCC
        const sandCuFtNet   = Math.round(totalSqFtRaw * 0.25);
        const aggCuFtNet    = Math.round(totalSqFtRaw * 0.36);
        const extPaintLitNet= Math.round(totalSqFtRaw * 0.05);   // exterior walls
        const intPaintLitNet= Math.round(totalSqFtRaw * 0.12);   // interior 2 coats

        const steelGrade = p.steelGrade || "Fe 500D TMT";
        const lengthM = p.length;
        const widthM = p.width;
        const heightM = p.height;

        return `You are CIH Material AI — a Senior Chartered Quantity Surveyor (MRICS) and Civil Cost Engineer.

PROJECT INPUT:
- Project: ${projName} | Location: ${loc}
- Sector: ${pType} | Structure: ${bType}
${(lengthM && widthM) ? `- Footprint: ${lengthM} m × ${widthM} m | Floor height: ${heightM || 3} m\n` : ''}- Base Area: ${areaSqFtRaw.toLocaleString()} sq ft | Floors: ${numFloors} | Total: ${totalSqFtRaw.toLocaleString()} sq ft (≈${totalSqM} m²)
- Concrete Mix: ${mixRatio} | Steel: ${steelGrade} | Soil: ${soil} | Foundation: ${foundation}
- Wastage Allowance: ${wastage} | Units: ${unitSystem}

CALCULATION REFERENCE (use these as your starting basis, refine with engineering judgment):
- Concrete volume ≈ ${concreteM3} m³
- Cement net ≈ ${cementBagsNet} bags (7.5 bags/m³ for M25); Coarse Agg: 0.88 m³ per m³ concrete; Fine Agg: 0.44 m³ per m³
- Steel net ≈ ${steelMTnet} MT (110 kg/m³ for RCC Frame); adjust for ${bType}
- Sand ≈ ${sandCuFtNet} cu.ft net; Coarse Aggregates ≈ ${aggCuFtNet} cu.ft net
- Paint: Exterior ≈ ${extPaintLitNet} L; Interior ≈ ${intPaintLitNet} L (2 coats)

OUTPUT FORMAT — YOU MUST FOLLOW THIS EXACT STRUCTURE. DO NOT USE TABLES. DO NOT USE PLACEHOLDER TEXT.

---

# 🏗️ Material Estimation Report — ${projName}

I have completed the Quantity Survey and Material Estimation analysis for your **${areaSqFtRaw.toLocaleString()} sq. ft. ${pType} Project** (${bType}, ${numFloors} Floors). Below is the detailed material requirement breakdown:

---

## 🧱 Cement

**Quantity:** [NET bags] Bags ([NET bags] net requirement + [WASTAGE bags] bags wastage allowance)
**Grade:** OPC 53 (IS 8112) — recommended for [brief structural rationale specific to ${bType}].
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹410 / bag)

---

## 🪨 Ready-Mix Concrete (${mixRatio})

**Quantity:** [NET] Cubic Meters ([NET] net requirement + [WASTAGE] cu. m wastage allowance)
**Grade:** ${mixRatio} — designed for [brief rationale: columns, beams, slabs].
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹6,200 / cu. m)

---

## 🔩 Steel Rebar (Fe 500D TMT)

**Quantity:** [NET] Metric Tons ([NET] net requirement + [WASTAGE] MT wastage allowance)
**Grade:** Fe500D IS 1786 — [brief rationale: seismic ductility, tension reinforcement].
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹63,500 / MT)

---

## 🪣 River Sand / Manufactured Sand (M-Sand)

**Quantity:** [NET] Cubic Feet ([NET] net requirement + [WASTAGE] cu. ft buffer)
**Grade:** Zone-II Double-Washed M-Sand — [brief rationale: plastering, concrete mix].
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹55 / cu. ft)

---

## 🪨 Coarse Aggregates (20mm)

**Quantity:** [NET] Cubic Feet ([NET] net requirement + [WASTAGE] cu. ft buffer)
**Grade:** Well-graded 20mm Crushed Stone — [brief rationale].
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹42 / cu. ft)

---

## 🎨 Exterior and Interior Paint

**Quantity:** [TOTAL] Litres Total ([EXT] Litres Exterior + [INT] Litres Interior)
**Specification:** 1 coat alkali-resistant primer + 2 coats weather-shield acrylic emulsion.
**Estimated Cost:** ₹[SUBTOTAL]

---

## 💧 Waterproofing Compound

**Quantity:** [QTY] Litres
**Specification:** Crystalline admixture for foundation, roof slab, and basement waterproofing.
**Estimated Cost:** ₹[SUBTOTAL] (@ ₹680 / L)

---

## 💰 Grand Total Estimated Material Budget

**₹[GRAND TOTAL]** *(Includes ${wastage} total site buffer and wastage allowance)*

---

## 📋 Executive Recommendations & Strategic Directives

**1. Storage and Moisture Management:**
[Specific advice for cement and aggregate storage on this site]

**2. Phased Procurement of Steel:**
[Specific phased delivery recommendation with tonnage splits for ${steelMTnet} MT]

**3. Quality Testing and Mix Verification:**
[Mandatory cube test schedule for ${mixRatio} concrete]

**4. Wastage Optimization:**
[Site monitoring protocol to stay within ${wastage} threshold for ${soil} site conditions]

---
IMPORTANT RULES:
- Replace every [bracketed placeholder] with a real calculated number
- Quantities must be consistent: wastage = net × wastage rate
- All INR amounts must use Indian number formatting (₹X,XX,XXX)
- Grand Total must equal sum of all subtotals`;
    },

    quantitySurveying: (params) => CIH_PROMPTS.materialEstimation(params),

    budgetAnalysis: (projectName, totalBudget, spent, categoryList) => {
        const snap = (typeof getProjectSnapshot === 'function')
            ? getProjectSnapshot(projectName)
            : ((typeof CIH_DATASET !== 'undefined' && CIH_DATASET.getProjectSnapshot)
                ? CIH_DATASET.getProjectSnapshot(projectName)
                : null);
        const fmt = (n) => (typeof cihFormatMoney === 'function' ? cihFormatMoney(n) : n);
        const allocated = totalBudget
            || (snap && (snap.formattedBudget || fmt(snap.budget)))
            || ((typeof CIH_DATASET !== 'undefined' && CIH_DATASET.budgetOverview && CIH_DATASET.budgetOverview.totalPortfolioBudget) || "Not specified");
        const currentSpend = spent
            || (snap && (snap.formattedSpent || fmt(snap.spent)))
            || ((typeof CIH_DATASET !== 'undefined' && CIH_DATASET.budgetOverview && CIH_DATASET.budgetOverview.totalSpent) || "Not specified");
        const remaining = (snap && (snap.formattedRemaining || fmt(snap.remainingBudget)))
            || ((typeof CIH_DATASET !== 'undefined' && CIH_DATASET.budgetOverview && CIH_DATASET.budgetOverview.remainingBudget) || "Not specified");
        const cats = categoryList && categoryList.length
            ? categoryList
            : ((snap && snap.expenses) ? [...new Set(snap.expenses.map((e) => e.category).filter(Boolean))] : []);

        return `Project: ${projectName || (snap && snap.title) || "Active Infrastructure Portfolio"}
Total Allocated Budget: ${allocated}
Current Spend: ${currentSpend}
Remaining Budget: ${remaining}
Breakdown Categories: ${JSON.stringify(cats)}
Live Expense Lines: ${JSON.stringify((snap && snap.expenses) || [], null, 2)}

Tasks:
1. Analyze current project spending velocity.
2. Predict potential budget overrun risks or variances.
3. Recommend 3 practical cost optimization strategies.
4. Explain the prediction in clear language.`;
    },

    /**
     * AI Risk Analysis System Prompt
     */
    riskAssessment: (projectName, snapshotData) => {
        return `Project Name: ${projectName}
Project Telemetry & Snapshot Data:
${JSON.stringify(snapshotData || {}, null, 2)}

TASK: Generate a comprehensive, professional Construction Risk Analysis Report for executive project leadership based on the snapshot data above.

FORMAT YOUR RESPONSE IN THE FOLLOWING STRUCTURE:

# ${projectName}: Construction Risk Analysis Report

## Executive Summary
[Provide a thorough executive summary covering site location, current status, progress percentage, allocated budget, current spend percentage, Health Score percentage, and overall risk rating.]

## Major Risks

1. **[Major Risk Title]**: [Detailed explanation of risk root cause based on project telemetry]
   - **Probability**: [High / Medium / Low]
   - **Impact**: [High / Medium / Low]

2. **[Major Risk Title]**: [Detailed explanation of risk root cause based on project telemetry]
   - **Probability**: [High / Medium / Low]
   - **Impact**: [High / Medium / Low]

3. **[Major Risk Title]**: [Detailed explanation of risk root cause based on project telemetry]
   - **Probability**: [High / Medium / Low]
   - **Impact**: [High / Medium / Low]

## Budget & Schedule Analysis
[Provide detailed analysis of budget spend rate vs work completion velocity, schedule target deadline, and predicted overrun variance.]

## Risk Mitigation Plan
1. **[Mitigation Strategy 1]**: [Actionable PM step]
2. **[Mitigation Strategy 2]**: [Actionable PM step]
3. **[Mitigation Strategy 3]**: [Actionable PM step]
4. **[Mitigation Strategy 4]**: [Actionable PM step]`;
    },

    executiveReport: (projectName, auditLogs) => {
        return `Project: ${projectName || "Infrastructure Site"}
Audit & Progress Logs: ${JSON.stringify(auditLogs || {})}

Tasks:
1. Generate an executive summary of project status.
2. Summarize overall progress against milestones.
3. Highlight major operational issues or bottlenecks.
4. Provide actionable recommendations.`;
    },

    budgetEstimation: (params) => {
        return `Project Infrastructure Type: ${params.projectType}
Total Built-up Area: ${params.areaSqFt} Sq. Ft.
Location / City: ${params.city}
Specification & Quality Grade: ${params.qualityGrade}
Target Construction Duration: ${params.durationMonths} Months
Contingency Buffer: ${params.contingencyBuffer}

TASK: As an expert Civil Engineering Quantity Surveyor and AI Financial Cost Estimator, generate a comprehensive Project Budget Estimation Report based on the parameters above.

FORMAT YOUR RESPONSE IN THE FOLLOWING STRUCTURE:

# ${params.projectType}: AI Project Budget Estimation Report

## Executive Cost Overview
[Provide an executive summary of total estimated cost in ₹ Crores, estimated cost per sq. ft, and total duration feasibility.]

## Cost Component Allocation Breakdown
- **Civil & Structural Work (Steel, Concrete, Rebar)**: ₹XX Cr (XX%)
- **Architectural Finishes & Facade**: ₹XX Cr (XX%)
- **MEP Services (Electrical, Plumbing, HVAC, Firefighting)**: ₹XX Cr (XX%)
- **Labor, Plant & Equipment Telemetry**: ₹XX Cr (XX%)
- **Regulatory Permits, Design & Admin**: ₹XX Cr (XX%)
- **Contingency & Price Escalation Reserve (${params.contingencyBuffer})**: ₹XX Cr (XX%)

## Cashflow Spending Forecast
[Provide a phase-wise expenditure plan across Foundation, Superstructure, Services, and Handover.]

## AI Cost Optimization & Risk Mitigation
1. **[Optimization Strategy 1]**: [Actionable PM cost saving tip]
2. **[Optimization Strategy 2]**: [Actionable PM cost saving tip]
3. **[Optimization Strategy 3]**: [Actionable PM cost saving tip]`;
    },

    /**
     * Helper to auto-detect document preset type if not explicitly supplied
     */
    detectDocumentPreset: (docTitle = "", docContent = "") => {
        const text = `${docTitle} ${docContent}`.toLowerCase();
        if (text.includes("boq") || text.includes("bill of quantities") || text.includes("quantities bill") || text.includes("schedule of rates") || text.includes("sor")) {
            return "boq";
        }
        if (text.includes("dpr") || text.includes("daily progress") || text.includes("site report") || text.includes("work completed today") || text.includes("manpower count") || text.includes("shift report")) {
            return "dpr";
        }
        if (text.includes("contract") || text.includes("agreement") || text.includes("clauses") || text.includes("liquidated") || text.includes("liability") || text.includes("indemnity") || text.includes("subcontractor")) {
            return "contract";
        }
        if (text.includes("invoice") || text.includes("tax invoice") || text.includes("bill to") || text.includes("amount payable") || text.includes("gstin") || text.includes("payment due")) {
            return "invoice";
        }
        return "general";
    },

    /**
     * AI Insights: Document Intelligence Prompt — unified executive report structure
     */
    documentAnalysis: (docTitle, docContent, presetType = "general") => {
        const detectedType = presetType || CIH_PROMPTS.detectDocumentPreset(docTitle, docContent);
        const title = docTitle || "Uploaded Construction Document";
        const timestamp = new Date().toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
        const rawContent = (docContent || "").trim();
        const maxChars = 14000;
        const truncatedNote = rawContent.length > maxChars
            ? "\n\n[Document text truncated to fit model context. Analyze only the text provided.]"
            : "";
        const boundedContent = (rawContent.slice(0, maxChars) || "Not specified in document") + truncatedNote;

        const typeHints = {
            boq: "Bill of Quantities — emphasize quantities, unit rates, material specs, and cost totals found in the file.",
            dpr: "Daily Progress Report — emphasize site activity, manpower, equipment, and delay logs found in the file.",
            contract: "Legal Contract — emphasize clauses, penalties, milestones, liability, and governance found in the file.",
            invoice: "Commercial Invoice — emphasize line items, taxes, vendor details, and payment terms found in the file.",
            general: "General construction document — extract only contractual, technical, and operational facts present in the file."
        };
        const typeHint = typeHints[detectedType.toLowerCase()] || typeHints.general;

        return `${SYSTEM_GUARDRAIL_PROMPT}

You are CIH Document Intelligence AI — a Senior Construction Contract Auditor and Chartered Cost Engineer.

GUARDRAIL FOR UPLOADED FILES:
If the document text is NOT valid construction, site engineering, civil works, BOQ/DPR, contractor logistics, or project commercial data, respond with ONLY this exact sentence and stop:
${CIH_OUT_OF_SCOPE_REFUSAL}

TASK:
Analyze ONLY the uploaded document text below. Generate a structured executive intelligence report. Every fact, number, date, party, quantity, and clause MUST come from the document. Do not invent data, typical industry values, or missing clauses.

DOCUMENT CONTEXT:
Document Name: "${title}"
Document Classification: ${detectedType.toUpperCase()}
Analysis Date: ${timestamp}
Document Type Focus: ${typeHint}

FULL DOCUMENT TEXT:
"""
${boundedContent}
"""

STRICT RULES:
1. Use ONLY information present in the document text above.
2. If a heading has no relevant data in the document, write "Not specified in document" for that item. Do not guess.
3. Do not mention APIs, databases, backends, or software architecture.
4. Follow the EXACT section headings and order below. Do not add extra top-level sections.

OUTPUT FORMAT (use this exact markdown structure):

# Document Intelligence Report

## Document Name
${title}

## Executive Summary
[Write 2–3 paragraphs covering document purpose, scope, key parties, and critical findings — derived only from the uploaded text.]

## Key Contractual Matrix & Specification
[Bullet list drawn only from the document. Cover these items when present; otherwise write "Not specified in document":
- Scope of work / deliverables
- Key quantities, rates, or budget figures (quote values from the document)
- Quality / material specifications and standards
- Milestones, deadlines, and delivery schedules
- Payment terms, penalties, and liquidated damages
- Parties, references, and governing terms]

## Identify Contract Risks
[Each risk MUST be a bullet in this exact pattern:
- **Risk:** [title] | **Severity:** High/Medium/Low | **Evidence:** [quote or paraphrase from document] | **Impact:** [consequence implied by the document]
List only risks supported by the uploaded text.]

## Practical Recommendation Set
[Numbered list of 5–8 actionable recommendations. Each recommendation must reference a finding or risk from this document. Be specific for site engineers, quantity surveyors, and project directors.]

---
*Generated by Construction Intelligent Hub AI via local Ollama inference • ${timestamp}*`;
    },

    /**
     * AI Insights: Predictive Forecast — plain-language owner briefing from live project telemetry
     */
    predictiveForecast: (projectData) => {
        const p = projectData || {};
        const title = p.title || "Active Project";
        const city = p.city || "Not specified";
        const progress = (p.progressPercent !== undefined && p.progressPercent !== null) ? p.progressPercent : "N/A";
        const deadline = p.deadline || "Not specified";
        const budget = p.formattedBudget || p.budget || "Not specified";
        const remaining = p.formattedRemaining || p.remainingBudget || "Not specified";
        const status = p.status || "Not specified";
        const riskLevel = p.riskLevel || p.suggestedRiskLevel || "Not specified";
        const spent = (p.spentPercent !== undefined && p.spentPercent !== null) ? `${p.spentPercent}%` : (p.formattedSpent || p.spent || "Not specified");
        const teamCount = (p.teamCount !== undefined && p.teamCount !== null) ? p.teamCount : "Not specified";
        const lowStock = (p.lowStockMaterialsCount !== undefined && p.lowStockMaterialsCount !== null) ? p.lowStockMaterialsCount : "Not specified";

        return `You are a Senior Construction Operations Analyst. Explain the forecast in simple, non-technical terms that any project owner can easily understand.

Project Details:
- Project Name: ${title}
- Location: ${city}
- Progress: ${progress}%
- Target Completion Date: ${deadline}
- Total Budget: ${budget}
- Remaining Budget: ${remaining}
- Current Status: ${status}
- Risk Level: ${riskLevel}
- Budget Spent So Far: ${spent}
- Team Size: ${teamCount}
- Low-Stock Material Alerts: ${lowStock}

Provide a concise, easy-to-read forecast structured as follows:

1. 📅 **Expected Completion & Timeline Forecast**
Explain in 2 simple sentences whether the project will meet its target completion date (${deadline}) or face delays, and why.

2. 💰 **Budget & Financial Outlook**
Explain in plain language if the budget is on track or at risk of overspending.

3. ⚠️ **Main Risks & Simple Solutions**
List 2-3 key risks in bullet points and give 1 simple action step for each.

4. 📋 **Overall Project Summary**
Give a clear 2-sentence summary of overall project health and key next steps.

Rules:
- Keep language simple, clear, and easy to read.
- Do NOT use technical jargon, code snippets, or unfulfilled placeholders.
- Use bullet points for clean readability.
- Base the forecast only on the project details above. Do not invent project names, dates, or budget figures that are not listed.`;
    }
};

CIH_PROMPTS.SYSTEM_GUARDRAIL_PROMPT = SYSTEM_GUARDRAIL_PROMPT;
CIH_PROMPTS.OUT_OF_SCOPE_REFUSAL = CIH_OUT_OF_SCOPE_REFUSAL;
CIH_PROMPTS.composeGuardedSystemPrompt = composeGuardedSystemPrompt;
CIH_PROMPTS.isQueryInScope = isQueryInScope;
CIH_PROMPTS.evaluateConstructionDocument = evaluateConstructionDocument;
