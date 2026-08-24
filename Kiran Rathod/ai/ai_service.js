/**
 * Construction Intelligent Hub (CIH) - High-Level AI Service Facade
 * 
 * Exposes clean, modular business logic methods for all application pages.
 * Fully decoupled from UI DOM logic and Ollama network endpoints.
 * Primary Default Model: Llama 3.2 (llama3.2)
 */

function containsConstructionContext(text) {
    const keywords = [
        "concrete", "rebar", "cement", "boq", "bill of quantities", "steel",
        "contract", "site", "drawing", "specification", "labor", "excavation",
        "foundation", "structural", "safety", "invoice", "vendor", "material", "cost"
    ];
    const lowerText = String(text || "").toLowerCase();
    return keywords.some(keyword => lowerText.includes(keyword));
}

const CIH_AI_SERVICE = {
    containsConstructionContext,
    outOfScopeRefusal: () => (
        (typeof CIH_OUT_OF_SCOPE_REFUSAL !== 'undefined')
            ? CIH_OUT_OF_SCOPE_REFUSAL
            : '⚠️ Out of Scope Request: I am specialized exclusively in civil engineering, construction management, material takeoffs, and site risk analysis. Please reframe your query around your project data or site logistics.'
    ),

    guardedSystem: (roleBlock) => (
        typeof composeGuardedSystemPrompt === 'function'
            ? composeGuardedSystemPrompt(roleBlock)
            : String(roleBlock || '')
    ),

    refuseOutOfScope: (userMessage) => ({
        userMessage: userMessage,
        outOfScope: true,
        rawText: CIH_AI_SERVICE.outOfScopeRefusal(),
        html: AIUtils.formatMarkdownToHTML(CIH_AI_SERVICE.outOfScopeRefusal())
    }),
    /**
     * File Validator for Document Uploads
     */
    validateUploadedDocumentFile: (file) => {
        if (!file) {
            return { valid: false, message: "No file selected." };
        }

        const maxSizeBytes = 15 * 1024 * 1024; // 15 MB limit
        if (file.size > maxSizeBytes) {
            return { valid: false, message: `File size exceeds 15 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB).` };
        }

        if (file.size === 0) {
            return { valid: false, message: "Selected file is empty (0 bytes)." };
        }

        const allowedExtensions = ['.pdf', '.txt', '.json', '.csv', '.md', '.doc', '.docx'];
        const fileName = file.name.toLowerCase();
        const hasValidExt = allowedExtensions.some(ext => fileName.endsWith(ext));

        if (!hasValidExt) {
            return { valid: false, message: `Unsupported file format. Please upload a PDF, TXT, CSV, JSON, or MD document.` };
        }

        return { valid: true, message: "File validated successfully." };
    },

    /**
     * Extract readable text from uploaded files (PDF, TXT, JSON, CSV, MD)
     */
    extractTextFromFile: async (file) => {
        const fileName = file.name.toLowerCase();

        if (fileName.endsWith('.pdf')) {
            const arrayBuffer = await file.arrayBuffer();

            // 1. Try PDF.js if available on window
            if (typeof window.pdfjsLib !== 'undefined') {
                try {
                    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                    const loadingTask = window.pdfjsLib.getDocument({ data: arrayBuffer });
                    const pdfDoc = await loadingTask.promise;
                    let fullText = '';

                    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                        const page = await pdfDoc.getPage(pageNum);
                        const textContent = await page.getTextContent();
                        const pageText = textContent.items.map(item => item.str).join(' ');
                        fullText += `--- Page ${pageNum} ---\n${pageText}\n\n`;
                    }

                    if (fullText.trim().length > 20) {
                        return fullText.trim();
                    }
                } catch (pdfErr) {
                    console.warn("[CIH PDF.js] Standard PDF.js worker extraction fallback.", pdfErr);
                }
            }

            // 2. Fallback Binary Stream PDF Text Extractor
            const textDecoder = new TextDecoder('latin1');
            const binaryString = textDecoder.decode(arrayBuffer);

            // Extract text tokens inside (text) Tj or [(text)] TJ
            const textMatches = [];
            const tjRegex = /\(([^()]+)\)\s*Tj/g;
            let match;
            while ((match = tjRegex.exec(binaryString)) !== null) {
                if (match[1] && match[1].trim().length > 1) {
                    textMatches.push(match[1].trim());
                }
            }

            const tjArrayRegex = /\[\s*\(([^()]+)\)[\s\S]*?\]\s*TJ/g;
            while ((match = tjArrayRegex.exec(binaryString)) !== null) {
                if (match[1] && match[1].trim().length > 1) {
                    textMatches.push(match[1].trim());
                }
            }

            if (textMatches.length > 5) {
                return textMatches.join(' ');
            }

            // Fallback plain text stream clean up
            const cleanedText = binaryString.replace(/[^\x20-\x7E\n\r\t]/g, ' ')
                .replace(/\s+/g, ' ')
                .replace(/stream[\s\S]*?endstream/g, ' ')
                .trim();

            if (cleanedText.length > 80) {
                return cleanedText.substring(0, 15000);
            }

            throw new Error(`Could not extract readable text from PDF "${file.name}". Try a text-based PDF or a TXT/CSV/JSON/MD file.`);
        } else {
            // Text-based files (.txt, .json, .csv, .md)
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result || '');
                reader.onerror = (e) => reject(e);
                reader.readAsText(file);
            });
        }
    },

    /**
     * Material Management AI: Quantity Estimation & Recommendations (Live Llama 3.2 Inference)
     */
    estimateMaterials: async (paramsOrProjectName, specs = "", modelName = "llama3.2") => {
        let prompt;
        let projTitle = "Active Infrastructure Site";

        if (typeof paramsOrProjectName === 'object' && paramsOrProjectName !== null) {
            prompt = CIH_PROMPTS.materialEstimation(paramsOrProjectName);
            projTitle = paramsOrProjectName.projectName || paramsOrProjectName.projName || "Active Infrastructure Site";
        } else {
            prompt = CIH_PROMPTS.materialEstimation(paramsOrProjectName, specs);
            projTitle = paramsOrProjectName || "Active Infrastructure Site";
        }

        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are CIH Material AI — a Senior Chartered Quantity Surveyor (MRICS) and Civil Cost Engineer for Construction Intelligent Hub.

ABSOLUTE RULES — NEVER VIOLATE:
1. Replace EVERY [bracketed placeholder] with a real, calculated number. Zero placeholders allowed in output.
2. Each material section must show: net quantity + wastage quantity = total, plus INR cost.
3. Grand Total = arithmetic sum of all material subtotals. Show the number.
4. Use Indian number formatting: ₹X,XX,XXX (lakhs notation).
5. Executive Recommendations must be specific to the project parameters given — not generic advice.`);

        const response = await OllamaClient.generate(prompt, systemPrompt, modelName);
        return {
            projectName: projTitle,
            prompt: prompt,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * Quantity Surveying Analysis Facade for Material Telemetry
     */
    generateQuantitySurveyingAnalysis: async (materialData, modelName = "llama3.2") => {
        return CIH_AI_SERVICE.estimateMaterials(materialData, "", modelName);
    },



    /**
     * Budget Management AI: Interactive Project Budget Estimation (Defaults to Llama 3.2)
     */
    estimateProjectBudget: async (params, modelName = "llama3.2") => {
        const p = params || {
            projectType: 'Commercial High-Rise Tower',
            areaSqFt: '250,000',
            city: 'Mumbai (Coastal / Metro)',
            qualityGrade: 'Standard Commercial',
            durationMonths: '24',
            contingencyBuffer: '10%'
        };

        const prompt = CIH_PROMPTS.budgetEstimation(p);
        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are CIH Financial AI, an expert civil engineering quantity surveyor and cost estimator for Construction Intelligent Hub. Evaluate project parameters and generate structured, accurate budget estimations.`);

        const response = await OllamaClient.generate(prompt, systemPrompt, modelName);

        return {
            params: p,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * Budget Management AI: Spending Analysis & Overrun Prediction (Defaults to Llama 3.2)
     */
    analyzeBudget: async (projectName, totalBudget, spent, categoryList, modelName = "llama3.2") => {
        const prompt = CIH_PROMPTS.budgetAnalysis(projectName, totalBudget, spent, categoryList);
        const response = await OllamaClient.generate(prompt, CIH_PROMPTS.systemPrompt, modelName);
        return {
            prompt: prompt,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * Risk Analysis AI: Dynamic Llama 3.2 Risk Report & Mitigation Plan Generator (Defaults to Llama 3.2)
     */
    evaluateRisk: async (projectName, snapshotData, modelName = "llama3.2") => {
        const liveSnap = (typeof getProjectSnapshot === 'function')
            ? getProjectSnapshot(projectName)
            : ((typeof CIH_DATASET !== 'undefined' && typeof CIH_DATASET.getProjectSnapshot === 'function')
                ? CIH_DATASET.getProjectSnapshot(projectName)
                : null);
        const snap = liveSnap || snapshotData || { title: projectName, city: 'Site', status: 'Active', progressPercent: 50, budget: 0, spent: 0, remainingBudget: 0, risks: [], expenses: [], materials: [] };

        const prompt = CIH_PROMPTS.riskAssessment(projectName, snap);
        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are CIH Risk AI, an expert civil engineering risk analyst for Construction Intelligent Hub. Evaluate project telemetry and generate clean, structured, executive risk analysis reports.`);

        const response = await OllamaClient.generate(prompt, systemPrompt, modelName);

        return {
            projectName: snap.title,
            snapshot: snap,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * Reports AI: Executive Project Performance & Audit Generator (Defaults to Llama 3.2)
     */
    generateExecutiveReport: async (projectName, reportFrequency = 'Weekly Report', modelName = "llama3.2") => {
        const liveSnap = (typeof getProjectSnapshot === 'function')
            ? getProjectSnapshot(projectName)
            : ((typeof CIH_DATASET !== 'undefined' && typeof CIH_DATASET.getProjectSnapshot === 'function')
                ? CIH_DATASET.getProjectSnapshot(projectName)
                : null);
        const snap = liveSnap || { title: projectName, city: 'Site', status: 'Active', progressPercent: 50, budget: 0, spent: 0, remainingBudget: 0, risks: [], expenses: [], materials: [] };

        const freq = reportFrequency || 'Weekly Report';
        const fmt = (n) => (typeof cihFormatMoney === 'function' ? cihFormatMoney(n) : n);

        const progressSummary = `${snap.progressPercent}% completion achieved against milestone targets for target completion date ${snap.deadline}. Current status is marked as '${snap.status}'.`;
        const budgetSummary = `Allocated budget: ${snap.formattedBudget || fmt(snap.budget)}. Current capital spend: ${snap.formattedSpent || fmt(snap.spent)} (${snap.spentPercent || 0}%). Remaining: ${snap.formattedRemaining || fmt(snap.remainingBudget)}.`;
        const riskSummary = `Overall project risk is evaluated as '${snap.suggestedRiskLevel || snap.riskLevel || 'MEDIUM'}'. Active site environmental hazard: ${snap.weatherHazard}. Open risks: ${(snap.risks || snap.risksList || []).length}.`;
        const materialSummary = `Total inventory parcels tracked: ${(snap.materials || []).length} items. ${(snap.lowStockMaterialsCount || 0) > 0 ? `Low stock alert for ${snap.lowStockMaterialsCount} item(s) requiring re-order.` : 'All material inventory stock levels remain within requirement thresholds.'}`;
        const teamSummary = `Site operations led by ${snap.projectLead || 'Unassigned'} with ${snap.teamCount || 0} assigned specialist(s).`;
        const recommendations = [
            `Maintain regular supply re-order cycles to prevent stock bottlenecks at ${snap.title}.`,
            `Conduct milestone risk audits with lead engineers to ensure schedule compliance before ${snap.deadline}.`,
            `Optimize heavy equipment fuel telemetry and schedule preventive maintenance checks on-site.`
        ];

        return {
            projectName: snap.title,
            frequency: freq,
            date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
            snapshot: snap,
            sections: {
                progress: progressSummary,
                budget: budgetSummary,
                risks: riskSummary,
                materials: materialSummary,
                team: teamSummary,
                recommendations: recommendations
            }
        };
    },

    /**
     * AI Insights 1: PDF & Construction Document Analyzer (Mandates Llama 3.2)
     */
    analyzeUploadedDocument: async (docTitle, docContent, modelName = "llama3.2", presetType = null) => {
        const title = docTitle || "Uploaded Construction Document";
        const text = (docContent && String(docContent).trim()) ? String(docContent).trim() : "";

        if (!text) {
            throw new Error("No document content provided for analysis. Upload a readable PDF/TXT/CSV/JSON/MD file first.");
        }

        if (!containsConstructionContext(text)) {
            const refusal = CIH_AI_SERVICE.outOfScopeRefusal();
            return {
                docTitle: title,
                presetType: 'out-of-scope',
                outOfScope: true,
                prompt: '',
                rawText: refusal,
                html: refusal
            };
        }

        const detectedPreset = presetType || (typeof CIH_PROMPTS !== 'undefined' ? CIH_PROMPTS.detectDocumentPreset(title, text) : "general");
        const prompt = CIH_PROMPTS.documentAnalysis(title, text, detectedPreset);
        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are CIH Document Intelligence AI — a Senior Construction Contract Auditor and Chartered Cost Engineer. Analyze only construction, site engineering, or project logistics documents. If the file is out of scope, reply with the exact mandatory refusal and nothing else. Never invent facts, rates, parties, or clauses. If information is missing, write "Not specified in document". Output the exact markdown headings requested in the user prompt.`);

        const activeModel = modelName || "llama3.2";
        const response = await OllamaClient.generate(prompt, systemPrompt, activeModel, true, {
            temperature: 0.2,
            top_p: 0.9,
            num_predict: 1800
        });

        if (!response || !String(response).trim()) {
            throw new Error("Ollama returned an empty report. Ensure the selected model is pulled and try Generate again.");
        }

        return {
            docTitle: title,
            presetType: detectedPreset,
            prompt: prompt,
            rawText: String(response).trim(),
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * AI Insights 1 (Chatbot): Document-Specific Q&A (Defaults to Llama 3.2)
     */
    chatWithUploadedDocument: async (docContent, userQuestion, modelName = "llama3.2") => {
        const text = docContent || "Construction Agreement & BOQ Document Context";
        const q = userQuestion || "What is the penalty for delay?";
        if (typeof isQueryInScope === 'function' && !isQueryInScope(q)) {
            return CIH_AI_SERVICE.refuseOutOfScope(q);
        }

        if (!containsConstructionContext(text)) {
            return CIH_AI_SERVICE.refuseOutOfScope(q);
        }

        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are a Document AI Assistant powered by Llama 3.2. You must answer questions STRICTLY based on the provided construction document text below. If the question is outside civil engineering / site logistics, use the mandatory refusal. If the answer cannot be found in the document, state clearly that the document does not mention it.

DOCUMENT CONTENT:
"""
${text}
"""`);

        const prompt = `User Question: "${q}"\n\nAnswer strictly from the document content provided. Keep response concise, accurate, and structured with bullet points.`;

        const response = await OllamaClient.generate(prompt, systemPrompt, modelName);
        return {
            question: q,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    },

    /**
     * AI Insights 3: Predictive AI Forecast — live Ollama (llama3.2) from project telemetry
     */
    generateProjectForecast: async (projectName, modelName = "llama3.2") => {
        const liveSnap = (typeof getProjectSnapshot === 'function')
            ? getProjectSnapshot(projectName)
            : ((typeof CIH_DATASET !== 'undefined' && typeof CIH_DATASET.getProjectSnapshot === 'function')
                ? CIH_DATASET.getProjectSnapshot(projectName)
                : null);
        const snap = liveSnap || {
            title: projectName,
            city: 'Site',
            status: 'Active',
            progressPercent: 65,
            budget: 0,
            spent: 0,
            remainingBudget: 0,
            formattedBudget: 'Not specified',
            deadline: 'Not specified',
            spentPercent: 0,
            teamCount: 0,
            lowStockMaterialsCount: 0,
            suggestedRiskLevel: 'MEDIUM',
            risks: [],
            expenses: [],
            materials: []
        };

        const projectData = {
            title: snap.title || projectName || "Active Project",
            city: snap.city || "Not specified",
            progressPercent: snap.progressPercent,
            deadline: snap.deadline || "Not specified",
            formattedBudget: snap.formattedBudget || snap.budget || "Not specified",
            formattedRemaining: snap.formattedRemaining,
            remainingBudget: snap.remainingBudget,
            status: snap.status || "Not specified",
            riskLevel: snap.riskLevel || snap.suggestedRiskLevel || "Not specified",
            spentPercent: snap.spentPercent,
            formattedSpent: snap.formattedSpent,
            spent: snap.spent,
            teamCount: snap.teamCount,
            lowStockMaterialsCount: snap.lowStockMaterialsCount
        };

        const prompt = CIH_PROMPTS.predictiveForecast(projectData);
        const systemPrompt = CIH_AI_SERVICE.guardedSystem(`You are CIH Forecast AI, a Senior Construction Operations Analyst. Write a simple, owner-friendly project forecast using only the supplied project details. Do not invent numbers, dates, or project names. Do not use placeholders.`);
        const activeModel = modelName || "llama3.2";

        const response = await OllamaClient.generate(prompt, systemPrompt, activeModel, true, {
            temperature: 0.3,
            top_p: 0.9,
            num_predict: 900
        });

        if (!response || !String(response).trim()) {
            throw new Error("Ollama returned an empty forecast. Confirm llama3.2 (or the selected model) is running, then try again.");
        }

        const rawText = String(response).trim();
        const generatedDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

        return {
            projectName: projectData.title,
            snapshot: snap,
            projectData: projectData,
            date: generatedDate,
            modelName: activeModel,
            prompt: prompt,
            rawText: rawText,
            html: AIUtils.formatMarkdownToHTML(rawText)
        };
    },

    /**
     * Global Chatbot AI Assistant (ChatGPT Style, Defaults to Llama 3.2)
     */
    chatWithAssistant: async (userMsg, history = [], modelName = "llama3.2") => {
        if (typeof isQueryInScope === 'function' && !isQueryInScope(userMsg, history)) {
            return CIH_AI_SERVICE.refuseOutOfScope(userMsg);
        }

        const messages = history.map(h => ({
            role: h.role === 'user' ? 'user' : 'assistant',
            content: h.content
        }));

        messages.push({
            role: 'user',
            content: userMsg
        });

        const response = await OllamaClient.chat(messages, userMsg, modelName);
        return {
            userMessage: userMsg,
            rawText: response,
            html: AIUtils.formatMarkdownToHTML(response)
        };
    }
};

// ==========================================================================
// DOCUMENT INTELLIGENCE — ON-DEMAND UI BINDINGS (ai-insights.html)
// Upload stores text only. Ollama runs exclusively on Generate Analysis.
// ==========================================================================
let uploadedDocumentText = "";
let uploadedDocumentTitle = "";

function getDocumentAnalysisOutputEl() {
    return document.getElementById("documentAnalysisOutput");
}

function showDocLoadingState() {
    const outputEl = getDocumentAnalysisOutputEl();
    const generateBtn = document.getElementById("generateDocAnalysisBtn");
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.style.opacity = "0.55";
        generateBtn.style.cursor = "not-allowed";
        generateBtn.innerHTML = "⏳ Generating with Ollama...";
    }
    if (outputEl) {
        outputEl.innerHTML = `
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; gap: 10px; color: #1E293B; font-weight: 700;">
                    <span style="display: inline-block; width: 16px; height: 16px; border: 2px solid #CBD5E1; border-top-color: #2563EB; border-radius: 50%; animation: spin 0.8s linear infinite;"></span>
                    Analyzing document with llama3.2 — please wait.
                </div>
                <p style="margin: 10px 0 0; color: #64748B; font-size: 13px;">Calling local Ollama (llama3.2). This can take a moment.</p>
            </div>
            <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
        `;
    }
}

function resetDocGenerateButton() {
    const generateBtn = document.getElementById("generateDocAnalysisBtn");
    if (!generateBtn) return;
    generateBtn.disabled = false;
    generateBtn.style.opacity = "1";
    generateBtn.style.cursor = "pointer";
    generateBtn.innerHTML = "⚡ Generate Analysis";
}

async function sendDocumentToOllama(docText) {
    const instructionsEl = document.getElementById("docUserInstructions");
    const instructions = instructionsEl ? String(instructionsEl.value || "").trim() : "";
    const title = uploadedDocumentTitle || "Uploaded Construction Document";
    const modelSelect = document.getElementById("ai-model-select");
    const activeModel = (modelSelect && modelSelect.value) ? modelSelect.value : "llama3.2";

    let payload = String(docText || "");
    if (instructions) {
        payload += `\n\nUSER ANALYSIS INSTRUCTIONS:\n${instructions}`;
    }

    return CIH_AI_SERVICE.analyzeUploadedDocument(title, payload, activeModel);
}

function renderDocumentReport(analysisResponse) {
    resetDocGenerateButton();
    const outputEl = getDocumentAnalysisOutputEl();
    if (!outputEl) return;

    if (analysisResponse && analysisResponse.outOfScope) {
        outputEl.innerHTML = `
            <div style="padding: 1rem; border-left: 4px solid #f59e0b; background-color: #fef3c7; color: #92400e; border-radius: 4px; font-weight: 500;">
                ⚠️ Off-Topic Document: The uploaded file does not contain recognized civil engineering, BOQ, or construction project data.
            </div>
        `;
        return;
    }

    const html = (analysisResponse && analysisResponse.html)
        ? analysisResponse.html
        : AIUtils.formatMarkdownToHTML((analysisResponse && analysisResponse.rawText) || String(analysisResponse || ""));
    const rawText = (analysisResponse && analysisResponse.rawText) || "";

    if (typeof currentDocAnalysisReportText !== "undefined") currentDocAnalysisReportText = rawText;
    if (typeof currentDocAnalysisData !== "undefined") currentDocAnalysisData = analysisResponse;
    if (typeof currentUploadedDocTitle !== "undefined") currentUploadedDocTitle = uploadedDocumentTitle;
    if (typeof currentUploadedDocContent !== "undefined") currentUploadedDocContent = uploadedDocumentText;

    outputEl.innerHTML = `
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #0F172A;">📄 Document Intelligence Report</span>
                <span style="color: #059669; font-size: 12px; font-weight: 600;">[STATUS: COMPLETE]</span>
            </div>
            <div id="documentAnalysisReportBody" style="color: #1E293B; font-size: 14px; line-height: 1.7;">${html}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 18px; padding-top: 14px; border-top: 1px solid #E2E8F0;">
                <span style="color: #64748B; font-size: 12px;">Generated by <strong>CIH Neural AI Engine (Llama 3.2)</strong></span>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button type="button" class="btn-primary" id="btnCopyDocSummary" onclick="copyDocAISummary()" style="padding: 8px 14px; font-size: 12px; border-radius: 6px;">📋 Copy Text</button>
                    <button type="button" class="btn-primary" id="btnPrintDocSummary" onclick="printDocAISummary()" style="padding: 8px 14px; font-size: 12px; border-radius: 6px;">🖨️ Export PDF</button>
                    <button type="button" class="btn-primary" id="btnDownloadDocSummary" onclick="downloadDocAISummary()" style="padding: 8px 16px; font-size: 12px; border-radius: 6px;">📥 Download Insights Report (.TXT)</button>
                </div>
            </div>
        </div>
    `;
}

function renderDocError(error) {
    resetDocGenerateButton();
    const outputEl = getDocumentAnalysisOutputEl();
    if (!outputEl) return;
    const message = (error && error.message) ? error.message : String(error || "Unknown error");
    outputEl.innerHTML = `
        <div style="padding: 1rem; border-left: 4px solid #ef4444; background-color: #fef2f2; color: #991b1b; border-radius: 4px; font-weight: 500;">
            ⚠️ Document Intelligence requires a live Ollama instance (llama3.2).<br><br>
            ${message}<br><br>
            Start Ollama locally, confirm the model is available, then click Generate Analysis again.
        </div>
    `;
}

function setDocFileStatus(message, isError) {
    const statusEl = document.getElementById("docFileStatus");
    if (!statusEl) return;
    statusEl.style.color = isError ? "#B91C1C" : "#334155";
    statusEl.innerHTML = message;
}

async function storeUploadedDocumentFile(file) {
    if (!file) return;

    const validation = CIH_AI_SERVICE.validateUploadedDocumentFile(file);
    if (!validation.valid) {
        uploadedDocumentText = "";
        uploadedDocumentTitle = "";
        setDocFileStatus(`⚠️ ${validation.message}`, true);
        alert(`Upload Error: ${validation.message}`);
        return;
    }

    setDocFileStatus(`⏳ Reading <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)…`, false);

    try {
        const extractedText = await CIH_AI_SERVICE.extractTextFromFile(file);
        uploadedDocumentText = String(extractedText || "");
        uploadedDocumentTitle = file.name;

        if (typeof currentUploadedDocContent !== "undefined") currentUploadedDocContent = uploadedDocumentText;
        if (typeof currentUploadedDocTitle !== "undefined") currentUploadedDocTitle = uploadedDocumentTitle;
        if (typeof currentDocAnalysisReportText !== "undefined") currentDocAnalysisReportText = null;
        if (typeof currentDocAnalysisData !== "undefined") currentDocAnalysisData = null;

        const outputEl = getDocumentAnalysisOutputEl();
        if (outputEl) outputEl.innerHTML = "";

        setDocFileStatus(`📄 Uploaded: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB). Click Generate Analysis when ready.`, false);
    } catch (err) {
        uploadedDocumentText = "";
        uploadedDocumentTitle = "";
        setDocFileStatus(`⚠️ Could not read <strong>${file.name}</strong>.`, true);
        alert(`Failed to extract text from ${file.name}: ${err.message}`);
    }
}

function initDocumentIntelligenceWorkflow() {
    const fileInput = document.getElementById("docFileInput");
    const dropZone = document.getElementById("docDropZone");
    const generateBtn = document.getElementById("generateDocAnalysisBtn");
    if (!fileInput || !generateBtn) return;

    fileInput.addEventListener("change", async (event) => {
        const file = event.target.files && event.target.files[0];
        await storeUploadedDocumentFile(file);
    });

    if (dropZone) {
        dropZone.addEventListener("click", (event) => {
            if (event.target === fileInput) return;
            fileInput.click();
        });
        dropZone.addEventListener("dragover", (event) => {
            event.preventDefault();
            dropZone.style.borderColor = "#2563EB";
            dropZone.style.background = "#EFF6FF";
        });
        dropZone.addEventListener("dragleave", () => {
            dropZone.style.borderColor = "#CBD5E1";
            dropZone.style.background = "#F8FAFC";
        });
        dropZone.addEventListener("drop", async (event) => {
            event.preventDefault();
            dropZone.style.borderColor = "#CBD5E1";
            dropZone.style.background = "#F8FAFC";
            const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
            if (file) {
                fileInput.value = "";
                await storeUploadedDocumentFile(file);
            }
        });
    }

    generateBtn.addEventListener("click", async () => {
        if (!uploadedDocumentText || uploadedDocumentText.trim() === "") {
            alert("Please upload a valid construction document first.");
            return;
        }

        if (!containsConstructionContext(uploadedDocumentText)) {
            const outputEl = getDocumentAnalysisOutputEl();
            if (outputEl) {
                outputEl.innerHTML = `
                    <div style="padding: 1rem; border-left: 4px solid #f59e0b; background-color: #fef3c7; color: #92400e; border-radius: 4px; font-weight: 500;">
                        ⚠️ Off-Topic Document: The uploaded file does not contain recognized civil engineering, BOQ, or construction project data.
                    </div>
                `;
            }
            return;
        }

        showDocLoadingState();

        try {
            const analysisResponse = await sendDocumentToOllama(uploadedDocumentText);
            renderDocumentReport(analysisResponse);
        } catch (error) {
            renderDocError(error);
        }
    });
}

if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initDocumentIntelligenceWorkflow);
    } else {
        initDocumentIntelligenceWorkflow();
    }
}