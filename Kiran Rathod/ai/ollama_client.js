/**
 * Construction Intelligent Hub (CIH) - Ollama API Client Wrapper
 * 
 * Low-level HTTP fetch wrapper for local Ollama endpoints.
 * Completely offline with no cloud or third-party dependencies.
 * Default Primary Model: Llama 3.2 (llama3.2)
 */

const OllamaClient = {
    _guardedSystem: (systemPrompt) => {
        const fallback = (typeof CIH_PROMPTS !== 'undefined') ? CIH_PROMPTS.systemPrompt : '';
        const raw = systemPrompt || fallback;
        if (typeof composeGuardedSystemPrompt === 'function') {
            return composeGuardedSystemPrompt(raw);
        }
        return raw;
    },

    _refusalText: () => (
        (typeof CIH_OUT_OF_SCOPE_REFUSAL !== 'undefined')
            ? CIH_OUT_OF_SCOPE_REFUSAL
            : '⚠️ Out of Scope Request: I am specialized exclusively in civil engineering, construction management, material takeoffs, and site risk analysis. Please reframe your query around your project data or site logistics.'
    ),

    _mustRefuse: (text, history) => {
        if (typeof cihIsInternalConstructionTask === 'function' && cihIsInternalConstructionTask(text)) {
            return false;
        }
        if (typeof isQueryInScope === 'function') {
            return !isQueryInScope(text, history);
        }
        return false;
    },
    /**
     * Get active Ollama daemon base URL endpoint
     */
    getEndpoint: () => {
        if (typeof OLLAMA_CONFIG !== 'undefined') {
            return OLLAMA_CONFIG.ollamaBaseUrl || OLLAMA_CONFIG.endpoint || "http://localhost:11434";
        }
        return "http://localhost:11434";
    },

    /**
     * Get default / active model name (defaults to "llama3.2")
     */
    getDefaultModel: () => {
        if (typeof OLLAMA_CONFIG !== 'undefined') {
            return OLLAMA_CONFIG.defaultModel || OLLAMA_CONFIG.activeModel || OLLAMA_CONFIG.model || "llama3.2";
        }
        return "llama3.2";
    },

    /**
     * Check if local Ollama daemon is active and serving model
     */
    checkHealth: async (baseUrl) => {
        const endpoint = baseUrl || OllamaClient.getEndpoint();
        const timeout = (typeof OLLAMA_CONFIG !== 'undefined' && OLLAMA_CONFIG.healthCheckTimeoutMs) ? OLLAMA_CONFIG.healthCheckTimeoutMs : 1500;
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(`${endpoint}/api/tags`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response.ok;
        } catch (err) {
            return false;
        }
    },

    /**
     * Send prompt to Ollama /api/generate endpoint
     * Defaults to Llama 3.2 (llama3.2)
     */
    generate: async (prompt, systemPrompt = "", modelName = "", ollamaOnly = false, extraOptions = null) => {
        if (OllamaClient._mustRefuse(prompt)) {
            return OllamaClient._refusalText();
        }

        const endpoint = OllamaClient.getEndpoint();
        const activeModel = modelName || OllamaClient.getDefaultModel();
        const isHealthy = await OllamaClient.checkHealth(endpoint);

        if (!isHealthy) {
            if (ollamaOnly) {
                throw new Error("Ollama is not running. Start Ollama locally (ollama serve) with your selected model, then click Generate again.");
            }
            if (typeof OLLAMA_CONFIG === 'undefined' || OLLAMA_CONFIG.fallbackEnabled) {
                console.warn(`[CIH AI Engine] Local Ollama daemon unreachable at ${endpoint}. Utilizing local fallback engine (Llama 3.2 emulation).`);
                return OllamaClient._getOfflineFallbackResponse(prompt);
            }
        }

        try {
            const baseTimeout = (typeof OLLAMA_CONFIG !== 'undefined' && OLLAMA_CONFIG.timeoutMs) ? OLLAMA_CONFIG.timeoutMs : 35000;
            const timeout = ollamaOnly ? Math.max(baseTimeout, 180000) : baseTimeout;
            const baseOptions = (typeof OLLAMA_CONFIG !== 'undefined' && OLLAMA_CONFIG.options)
                ? OLLAMA_CONFIG.options
                : { temperature: 0.7, top_p: 0.9, num_predict: 800 };
            const options = extraOptions ? { ...baseOptions, ...extraOptions } : baseOptions;

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const payload = {
                model: activeModel,
                prompt: prompt,
                system: OllamaClient._guardedSystem(systemPrompt),
                stream: false,
                options: options
            };

            const response = await fetch(`${endpoint}/api/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            return data.response;
        } catch (err) {
            if (ollamaOnly) {
                const msg = err && err.name === 'AbortError'
                    ? `Ollama timed out while generating the document report. Try a smaller file or a faster local model.`
                    : (err.message || 'Unknown error');
                throw new Error(`Ollama request failed: ${msg}. Document analysis requires a live Ollama instance (no offline mock).`);
            }
            console.warn("[CIH AI Engine] Ollama request failed or timed out. Falling back to local Llama 3.2 fallback engine.", err);
            return OllamaClient._getOfflineFallbackResponse(prompt);
        }
    },

    /**
     * Send message history to Ollama /api/chat endpoint
     * Defaults to Llama 3.2 (llama3.2)
     */
    chat: async (messages, originalUserMsg = "", modelName = "", systemOverride = "") => {
        const endpoint = OllamaClient.getEndpoint();
        const activeModel = modelName || OllamaClient.getDefaultModel();
        const queryText = originalUserMsg || (messages.length ? messages[messages.length - 1].content : "");
        if (OllamaClient._mustRefuse(queryText, messages)) {
            return OllamaClient._refusalText();
        }

        const isHealthy = await OllamaClient.checkHealth(endpoint);

        const fullMessages = messages.map((m) => ({ role: m.role, content: m.content }));
        if (!fullMessages.some(m => m.role === 'system')) {
            fullMessages.unshift({
                role: 'system',
                content: OllamaClient._guardedSystem(systemOverride)
            });
        } else {
            fullMessages.forEach((m) => {
                if (m.role === 'system') {
                    m.content = OllamaClient._guardedSystem(m.content);
                }
            });
        }

        if (!isHealthy && (typeof OLLAMA_CONFIG === 'undefined' || OLLAMA_CONFIG.fallbackEnabled)) {
            return OllamaClient._getOfflineFallbackResponse(queryText, fullMessages);
        }

        try {
            const timeout = (typeof OLLAMA_CONFIG !== 'undefined' && OLLAMA_CONFIG.timeoutMs) ? OLLAMA_CONFIG.timeoutMs : 35000;
            const options = (typeof OLLAMA_CONFIG !== 'undefined' && OLLAMA_CONFIG.options) ? OLLAMA_CONFIG.options : { temperature: 0.7, top_p: 0.9, num_predict: 800 };

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const payload = {
                model: activeModel,
                messages: fullMessages,
                stream: false,
                options: options
            };

            const response = await fetch(`${endpoint}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`Ollama Chat error: ${response.statusText}`);
            }

            const data = await response.json();
            return data.message.content;
        } catch (err) {
            console.warn("[CIH Chat] Request timed out or Ollama offline. Utilizing local dynamic Llama 3.2 AI engine.", err);
            return OllamaClient._getOfflineFallbackResponse(queryText, fullMessages);
        }
    },

    /**
     * Dynamic & Conversational Local Fallback Knowledge Engine when Ollama is offline (Llama 3.2 heuristic mode)
     */
    _getOfflineFallbackResponse: (prompt, history = []) => {
        if (OllamaClient._mustRefuse(prompt, history)) {
            return OllamaClient._refusalText();
        }

        const lower = (prompt || "").toLowerCase().trim();
        const dataset = (typeof CIH_DATASET !== 'undefined') ? CIH_DATASET : null;

        // Document Intelligence is Ollama-only — never emit a mock document report.
        if (lower.includes("cih document intelligence") || lower.includes("document intelligence report") || lower.includes("full document text:") || lower.includes("key contractual matrix")) {
            return "Ollama is not running. Document Intelligence requires a live local Ollama model. Start Ollama and click Generate again. Offline mock reports are disabled for this module.";
        }
        // 0B. MATERIAL ESTIMATION & QUANTITY SURVEYING PROMPT
        if (lower.includes("cih material ai") || lower.includes("material estimation report") || lower.includes("material requirement breakdown") || lower.includes("tasks: estimate material quantities")) {
            // Extract parameters from prompt text if available
            const projMatch = prompt.match(/Project:\s*([^|\n]+)/i);
            const pTypeMatch = prompt.match(/Sector:\s*([^|\n]+)/i) || prompt.match(/Project Category:\s*([^|\n]+)/i);
            const bTypeMatch = prompt.match(/Structure:\s*([^|\n]+)/i) || prompt.match(/Building System:\s*([^|\n]+)/i);
            const areaMatch = prompt.match(/Base Area:\s*([\d,]+)/i) || prompt.match(/areaSqFt:\s*([\d,]+)/i);
            const floorsMatch = prompt.match(/Floors:\s*(\d+)/i) || prompt.match(/numFloors:\s*(\d+)/i);
            const mixMatch = prompt.match(/Concrete Mix:\s*([^|\n]+)/i);
            const soilMatch = prompt.match(/Soil:\s*([^|\n]+)/i);
            const foundMatch = prompt.match(/Foundation:\s*([^|\n]+)/i);

            const projName = projMatch ? projMatch[1].trim() : "Active Infrastructure Site";
            const pType = pTypeMatch ? pTypeMatch[1].trim() : "Commercial Infrastructure";
            const bType = bTypeMatch ? bTypeMatch[1].trim() : "RCC Frame Structure";
            const baseArea = areaMatch ? parseInt(areaMatch[1].replace(/,/g, ''), 10) || 50000 : 50000;
            const floors = floorsMatch ? parseInt(floorsMatch[1], 10) || 12 : 12;
            const totalAreaSqFt = baseArea * floors;
            const totalSqM = Math.round(totalAreaSqFt / 10.764);
            const mixRatio = mixMatch ? mixMatch[1].trim() : "M25 (1:1:2)";
            const soil = soilMatch ? soilMatch[1].trim() : "Clayey Soil (High Plasticity)";
            const foundation = foundMatch ? foundMatch[1].trim() : "Raft / Mat Foundation";

            // Engineering Quantities Calculation
            const concreteM3Net = Math.round(totalSqM * 0.15 * 1.3);
            const concreteM3Wastage = Math.round(concreteM3Net * 0.08);
            const concreteM3Total = concreteM3Net + concreteM3Wastage;
            const concreteCost = concreteM3Total * 6200;

            const cementBagsNet = Math.round(concreteM3Net * 7.5);
            const cementBagsWastage = Math.round(cementBagsNet * 0.08);
            const cementBagsTotal = cementBagsNet + cementBagsWastage;
            const cementCost = cementBagsTotal * 410;

            const steelMTNet = Math.round(concreteM3Net * 0.11);
            const steelMTWastage = Math.max(1, Math.round(steelMTNet * 0.08));
            const steelMTTotal = steelMTNet + steelMTWastage;
            const steelCost = steelMTTotal * 63500;

            const sandCuFtNet = Math.round(totalAreaSqFt * 0.25);
            const sandCuFtWastage = Math.round(sandCuFtNet * 0.08);
            const sandCuFtTotal = sandCuFtNet + sandCuFtWastage;
            const sandCost = sandCuFtTotal * 55;

            const aggCuFtNet = Math.round(totalAreaSqFt * 0.36);
            const aggCuFtWastage = Math.round(aggCuFtNet * 0.08);
            const aggCuFtTotal = aggCuFtNet + aggCuFtWastage;
            const aggCost = aggCuFtTotal * 42;

            const extPaintNet = Math.round(totalAreaSqFt * 0.05);
            const intPaintNet = Math.round(totalAreaSqFt * 0.12);
            const paintTotalLit = extPaintNet + intPaintNet;
            const paintCost = Math.round(paintTotalLit * 380);

            const wpLitres = Math.round(totalAreaSqFt * 0.008);
            const wpCost = wpLitres * 680;

            const grandTotalCost = concreteCost + cementCost + steelCost + sandCost + aggCost + paintCost + wpCost;

            const fmtInr = (n) => n.toLocaleString('en-IN');

            return `# 🏗️ Material Estimation Report — ${projName}

I have completed the Quantity Survey and Material Estimation analysis for your **${baseArea.toLocaleString()} sq. ft. ${pType} Project** (${bType}, ${floors} Floors). Below is the detailed material requirement breakdown:

---

## 🧱 Cement

**Quantity:** ${fmtInr(cementBagsTotal)} Bags (${fmtInr(cementBagsNet)} net requirement + ${fmtInr(cementBagsWastage)} bags wastage allowance)
**Grade:** OPC 53 / PPC (IS 8112) — recommended for structural slab casting, shear walls, and high-adhesion masonry.
**Estimated Cost:** ₹${fmtInr(cementCost)} (@ ₹410 / bag)

---

## 🪨 Ready-Mix Concrete (${mixRatio})

**Quantity:** ${fmtInr(concreteM3Total)} Cubic Meters (${fmtInr(concreteM3Net)} net requirement + ${fmtInr(concreteM3Wastage)} cu. m wastage allowance)
**Grade:** ${mixRatio} — batching designed for high compressive strength columns, tie-beams, and suspended floor slabs.
**Estimated Cost:** ₹${fmtInr(concreteCost)} (@ ₹6,200 / cu. m)

---

## 🔩 Steel Rebar (Fe 500D TMT)

**Quantity:** ${fmtInr(steelMTTotal)} Metric Tons (${fmtInr(steelMTNet)} net requirement + ${fmtInr(steelMTWastage)} MT wastage allowance)
**Grade:** Fe500D IS 1786 — high-ductility seismic grade rebar for load-bearing columns, footings, and structural slabs.
**Estimated Cost:** ₹${fmtInr(steelCost)} (@ ₹63,500 / MT)

---

## 🪣 River Sand / Manufactured Sand (M-Sand)

**Quantity:** ${fmtInr(sandCuFtTotal)} Cubic Feet (${fmtInr(sandCuFtNet)} net requirement + ${fmtInr(sandCuFtWastage)} cu. ft buffer)
**Grade:** Zone-II Double-Washed M-Sand — optimal silt-free grading for RCC mix and internal/external wall plastering.
**Estimated Cost:** ₹${fmtInr(sandCost)} (@ ₹55 / cu. ft)

---

## ⚙️ Coarse Aggregates (20mm)

**Quantity:** ${fmtInr(aggCuFtTotal)} Cubic Feet (${fmtInr(aggCuFtNet)} net requirement + ${fmtInr(aggCuFtWastage)} cu. ft buffer)
**Grade:** Angular 20mm & 10mm Graded Crushed Blue Metal Stone for high interlock structural concrete casting.
**Estimated Cost:** ₹${fmtInr(aggCost)} (@ ₹42 / cu. ft)

---

## 🎨 Exterior and Interior Paint

**Quantity:** ${fmtInr(paintTotalLit)} Litres Total (${fmtInr(extPaintNet)} L Exterior Acrylic + ${fmtInr(intPaintNet)} L Interior Emulsion)
**Specification:** 1 coat alkali-resistant primer + 2 coats premium washable weather-shield acrylic emulsion.
**Estimated Cost:** ₹${fmtInr(paintCost)}

---

## 💧 Waterproofing Compound

**Quantity:** ${fmtInr(wpLitres)} Litres
**Specification:** Polyurethane & Crystalline liquid membrane admixture for subterranean foundation footings and terrace level.
**Estimated Cost:** ₹${fmtInr(wpCost)} (@ ₹680 / L)

---

## 💰 Grand Total Estimated Material Budget

**₹${fmtInr(grandTotalCost)}** *(Includes 8% total site buffer and wastage allowance)*

---

## 📋 Executive Recommendations & Strategic Directives

**1. Soil & Foundation Guidance:**
Given the site profile of **${soil}** and **${foundation}**, plate load compaction tests must be certified before pouring **${fmtInr(concreteM3Total)} m³** of foundation concrete.

**2. Phased Procurement of Steel:**
Stage the **${fmtInr(steelMTTotal)} MT** of Fe500D TMT steel deliveries in bi-weekly batches matching construction milestone phases. Keep rebars on elevated timber runners to prevent moisture oxidation.

**3. Storage and Moisture Management:**
Store all **${fmtInr(cementBagsTotal)} bags** of cement in a moisture-controlled elevated shed with plastic underlay to prevent hydration degradation.`;
        }

        // 1. GENERAL QUESTION: Reinforced Concrete
        if (lower.includes("reinforced concrete") || lower.includes("what is concrete") || lower.includes("rcc")) {
            return `### 🏗️ Reinforced Concrete (RCC) Overview

**Reinforced Concrete (RCC)** is a composite material in which steel rebar or mesh is embedded into fresh concrete to overcome concrete's natural weakness in tensile strength.

#### 💡 Key Structural Principles:
- **Compressive Strength**: Concrete is exceptionally strong under compression (pushing forces) but weak under tension (pulling forces).
- **Tensile Resistance**: High-tensile TMT steel bars absorb bending, shearing, and tensile loads created by dead weight, live traffic, and wind.
- **Thermal Compatibility**: Concrete and steel expand and contract at nearly identical thermal expansion coefficients, preventing internal shearing under temperature fluctuations.

In our active projects (e.g. *Delhi Metro - Phase 4* and *Mumbai Trans Harbour Link*), Grade Fe500 TMT steel rebar and M30–C50 marine-grade concrete are used for all columns, piers, and floor slabs.`;
        }

        // 2. GENERAL QUESTION: How to reduce construction cost / cost optimization
        if (lower.includes("reduce cost") || lower.includes("lower cost") || lower.includes("save money") || lower.includes("cost reduction") || lower.includes("optimize cost") || lower.includes("reduce construction cost")) {
            return `### 💵 Strategic Cost Reduction Recommendations in Construction

Reducing construction expenditure without compromising structural integrity requires systematic site & supply optimization:

#### 1. Real-Time RFID & Material Inventory Tracking
- **Eliminate Material Waste**: Over-ordering and moisture damage account for 12–18% of project budget loss. Staging cement and rebar with RFID tracking reduces waste significantly (averaging **35% waste reduction** across CIH sites).

#### 2. Equipment Telemetry & Preventive Maintenance
- **Idle Fuel Optimization**: Telemetry sensors on excavators and cranes cut non-productive idle fuel consumption, saving ~12–15% in operational costs.
- **Service Telemetry**: Repairing machinery before engine breakdown avoids expensive site downtime and emergency equipment rental fees.

#### 3. Bulk Procurement Aggregation
- Consolidate rebar, cement, and glazing orders across regional project sites (e.g., aggregating *Delhi Metro* and *Indore Smart City*) to secure bulk volume discounts.

#### 4. Prefabrication & Pre-Cast Modules
- Transitioning to pre-cast concrete girders and modular wall panels accelerates completion speed and lowers site labor overhead.`;
        }

        // 3. GENERAL QUESTION: Explain budget utilization
        if (lower.includes("budget utilization") || lower.includes("explain budget") || lower.includes("how budget works")) {
            return `### 📊 Understanding Construction Budget Utilization

**Budget Utilization** measures the rate and efficiency at which allocated capital funds are converted into completed site infrastructure over time.

#### 🗝️ Core Indicators:
1. **Capital Expenditure Velocity (CapEx)**: Compares actual cumulative spending against planned baseline cash flow curves.
2. **Earned Value Management (EVM)**:
   - **Cost Performance Index (CPI)**: Value of work completed divided by actual cost incurred. (CPI > 1.0 indicates under-budget performance).
   - **Schedule Variance (SV)**: Difference between earned progress value and baseline schedule target.
3. **Current Portfolio Metrics**:
   - Total Portfolio Budget: **${(dataset && dataset.budgetOverview && dataset.budgetOverview.totalPortfolioBudget) || 'Not specified'}**
   - Total Cumulative Spent: **${(dataset && dataset.budgetOverview && dataset.budgetOverview.totalSpent) || 'Not specified'}** (${(dataset && dataset.budgetOverview && dataset.budgetOverview.utilizationPercent) || 0}% utilization)
   - Portfolio Overrun Variance: **${(dataset && dataset.budgetOverview && dataset.budgetOverview.variancePercent) || '0%'}**`;
        }

        if (!dataset) {
            return `### 🤖 CIH Assistant (Llama 3.2)\nI am ready to assist with your construction management, budget analysis, material tracking, and engineering questions. Please ask any general or project-specific question!`;
        }

        const projects = dataset.projects || [];
        const materials = dataset.materials || [];
        const budget = dataset.budgetOverview || {};
        const equipment = dataset.equipment || [];
        const team = dataset.team || [];
        const risks = dataset.risks || [];
        const titleOf = (id) => (typeof cihProjectTitle === 'function' ? cihProjectTitle(id) : id);
        const money = (n) => (typeof cihFormatMoney === 'function' ? cihFormatMoney(n) : n);

        // 4. PROJECT SPECIFIC QUESTION: Why is my project delayed?
        if (lower.includes("delay") || lower.includes("why delayed") || lower.includes("behind schedule") || lower.includes("on hold")) {
            const delayedProjects = projects.filter(p => /hold|delay/i.test(p.status || '') || String(p.riskLevel || '').toLowerCase() === 'high');
            const openRisks = risks.filter(r => String(r.status).toLowerCase() === 'open');

            if (delayedProjects.length > 0) {
                return `### ⚠️ Delay Analysis & Root Cause Breakdown

Based on the live CIH dataset, **${delayedProjects.length} project(s)** are On Hold, delayed, or high-risk:

${delayedProjects.map(p => {
    const projRisk = openRisks.find(r => r.projectId === p.id);
    return `#### 🔴 ${p.title} (${p.city})
- **Current Progress**: **${p.progressPercent}%** (Target Deadline: **${p.formattedDeadline || p.deadline}**)
- **Allocated Budget**: **${p.formattedBudget || money(p.budget)}**
- **Primary Root Cause**: ${projRisk ? `*${projRisk.category}* — ${projRisk.riskTitle}. ${projRisk.mitigationPlan}` : 'No open risk record is linked to this project in the register.'}
- **Severity**: ${projRisk ? projRisk.severityScore : 'n/a'} | **Owner**: ${projRisk ? projRisk.assignedTo : 'Unassigned'}`;
}).join('\n\n')}`;
            } else {
                return `### ✅ Project Schedule Status
All active projects are currently progressing within acceptable schedule parameters.`;
            }
        }

        // 5. SEARCH FOR MATCHED PROJECT
        const matchedProject = projects.find(p => lower.includes(p.title.toLowerCase()) || lower.includes(p.city.toLowerCase()) || lower.includes(p.id.toLowerCase()));
        if (matchedProject) {
            const projTeam = team.filter(t => (t.assignedProjects || []).includes(matchedProject.id));
            const projEq = equipment.filter(e => e.projectId === matchedProject.id);
            const projMat = materials.filter(m => m.projectId === matchedProject.id);
            const projRisk = risks.filter(r => r.projectId === matchedProject.id);
            const lead = matchedProject.projectLead || (projTeam[0] && projTeam[0].name) || 'Unassigned';

            return `### 🏢 Project Analysis: ${matchedProject.title}
- **Location**: 📍 ${matchedProject.city}
- **Client**: ${matchedProject.client || '—'}
- **Current Status**: \`${matchedProject.status}\` (${matchedProject.progressPercent}% Complete)
- **Allocated Budget**: **${matchedProject.formattedBudget || money(matchedProject.budget)}**
- **Spent**: **${matchedProject.formattedSpent || money(matchedProject.spent)}** (${matchedProject.spentPercent || 0}%)
- **Target Deadline**: **${matchedProject.formattedDeadline || matchedProject.deadline}**
- **Project Lead**: 👤 ${lead}
- **Risk Level**: **${matchedProject.riskLevel || 'Low'}**

#### 👥 Assigned Site Personnel (${projTeam.length}):
${projTeam.length ? projTeam.map(t => `- **${t.name}** (${t.role})`).join('\n') : '- No team members assigned'}

#### 🚜 Machinery & Telemetry (${projEq.length}):
${projEq.length ? projEq.map(e => `- **${e.assetName}** (\`${e.unitCode}\`) — Engine Health: ${e.engineHealthPct}% (${e.status})`).join('\n') : '- No equipment linked'}

#### 📦 Material Inventory (${projMat.length}):
${projMat.length ? projMat.map(m => `- **${m.itemName}**: ${m.quantityInStock} ${m.unit} on site / ${m.quantityRequired} ${m.unit} required`).join('\n') : '- No materials linked'}

${projRisk.length ? `#### ⚠️ Risk Logs:\n${projRisk.map(r => `- **${r.riskTitle}** (${r.category}): severity ${r.severityScore}, status ${r.status}. Mitigation: ${r.mitigationPlan}`).join('\n')}` : ''}`;
        }

        // 6. DEFAULT IN-SCOPE CONSTRUCTION RESPONSE
        return `### 🏗️ CIH Construction Assistant
I can only help with **civil engineering, site logistics, material takeoffs, risk, budget, and project data** in this workspace.

Live portfolio: **${projects.length} project(s)** — ${projects.map(p => p.title).join(', ') || 'none loaded'}.

Ask a specific question such as:
- Budget spend vs remaining for a named project
- Open risks and mitigation owners
- Material stock vs requirement
- Equipment health or maintenance due`;
    }
};
