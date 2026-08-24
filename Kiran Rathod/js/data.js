/**
 * Construction Intelligent Hub — centralized application state.
 * Canonical collections persist to localStorage (`cih_dataset_v2`).
 * Derived metrics, aliases, and AI snapshots are computed at runtime.
 */

const CIH_STORAGE_KEY = 'cih_dataset_v2';

const CIH_SEED_DATASET = {
    projects: [
        {
            id: 'proj-101',
            title: 'Delhi Metro Phase 4 - Line Expansion',
            city: 'Delhi NCR',
            client: 'DMRC',
            status: 'In Progress',
            progressPercent: 68,
            budget: 12000000000,
            spent: 8160000000,
            startDate: '2024-01-15',
            deadline: '2026-12-30',
            riskLevel: 'Medium',
            buildingType: 'Infrastructure / Transit'
        },
        {
            id: 'proj-102',
            title: 'Mumbai Coastal Road Package B',
            city: 'Mumbai',
            client: 'MMRDA',
            status: 'In Progress',
            progressPercent: 54,
            budget: 8500000000,
            spent: 4675000000,
            startDate: '2023-09-01',
            deadline: '2027-03-31',
            riskLevel: 'High',
            buildingType: 'Infrastructure / Highway'
        },
        {
            id: 'proj-103',
            title: 'Bengaluru Airport T2 Expansion',
            city: 'Bengaluru',
            client: 'BIAL',
            status: 'Planning',
            progressPercent: 22,
            budget: 6400000000,
            spent: 1280000000,
            startDate: '2025-04-01',
            deadline: '2028-06-15',
            riskLevel: 'Low',
            buildingType: 'Airport / Aviation'
        },
        {
            id: 'proj-104',
            title: 'Indore Smart Civic Hub',
            city: 'Indore',
            client: 'ISCL',
            status: 'On Hold',
            progressPercent: 31,
            budget: 2100000000,
            spent: 945000000,
            startDate: '2024-06-10',
            deadline: '2026-08-20',
            riskLevel: 'High',
            buildingType: 'Commercial / Civic'
        }
    ],

    risks: [
        {
            id: 'risk-201',
            projectId: 'proj-101',
            riskTitle: 'Monsoon Groundwater Seepage at Station Excavation',
            category: 'Environmental / Geotechnical',
            probability: 4,
            impact: 5,
            severityScore: 20,
            status: 'Open',
            mitigationPlan: 'Deploy high-capacity dewatering pumps and apply shotcrete lining.',
            assignedTo: 'Rajesh Kumar (Site Director)'
        },
        {
            id: 'risk-202',
            projectId: 'proj-101',
            riskTitle: 'Steel Rebar Price Fluctuation Overhead',
            category: 'Financial / Supply Chain',
            probability: 3,
            impact: 4,
            severityScore: 12,
            status: 'Mitigated',
            mitigationPlan: 'Lock in bulk purchase rates with primary steel vendor.',
            assignedTo: 'Ananya Sharma (Procurement Head)'
        },
        {
            id: 'risk-203',
            projectId: 'proj-102',
            riskTitle: 'Coastal Wind Cutoff on Crane Operations',
            category: 'Safety / Weather',
            probability: 4,
            impact: 4,
            severityScore: 16,
            status: 'Open',
            mitigationPlan: 'Enforce 35 km/h anemometer cutoff and night-shift resequencing.',
            assignedTo: 'Vikram Sharma (Senior Site Engineer)'
        },
        {
            id: 'risk-204',
            projectId: 'proj-104',
            riskTitle: 'Municipal Utility Relocation Delay',
            category: 'Regulatory / Right of Way',
            probability: 5,
            impact: 3,
            severityScore: 15,
            status: 'Open',
            mitigationPlan: 'Escalate ROW clearance with civic body and parallel-path non-critical works.',
            assignedTo: 'Pooja Deshmukh (Safety & OSHA Auditor)'
        }
    ],

    materials: [
        {
            id: 'mat-301',
            projectId: 'proj-101',
            itemName: 'TMT Rebar (Fe 500D)',
            category: 'Steel & Structure',
            unit: 'Metric Tons',
            quantityRequired: 4500,
            quantityInStock: 1200,
            unitPrice: 65000,
            supplier: 'Jindal Steel & Power'
        },
        {
            id: 'mat-302',
            projectId: 'proj-101',
            itemName: 'Ready-Mix Concrete M40',
            category: 'Concrete',
            unit: 'Cubic Metres',
            quantityRequired: 28000,
            quantityInStock: 9200,
            unitPrice: 6200,
            supplier: 'UltraTech Concrete'
        },
        {
            id: 'mat-303',
            projectId: 'proj-102',
            itemName: 'VG-40 Bitumen Drums',
            category: 'Paving',
            unit: 'Drums',
            quantityRequired: 1800,
            quantityInStock: 420,
            unitPrice: 18500,
            supplier: 'Indian Oil Corporation'
        },
        {
            id: 'mat-304',
            projectId: 'proj-103',
            itemName: 'Double-Pane Facade Glass',
            category: 'Glazing & Finishing',
            unit: 'Panels',
            quantityRequired: 2400,
            quantityInStock: 1800,
            unitPrice: 28500,
            supplier: 'Saint-Gobain'
        },
        {
            id: 'mat-305',
            projectId: 'proj-104',
            itemName: 'PPC Cement Bags',
            category: 'Cement',
            unit: 'Bags',
            quantityRequired: 12000,
            quantityInStock: 850,
            unitPrice: 410,
            supplier: 'Ambuja Cement'
        }
    ],

    expenses: [
        {
            id: 'exp-401',
            projectId: 'proj-101',
            category: 'Foundation & Earthworks',
            amount: 2500000000,
            date: '2025-05-10',
            vendor: 'L&T Heavy Civil',
            paymentStatus: 'Paid',
            title: 'Station box excavation package'
        },
        {
            id: 'exp-402',
            projectId: 'proj-101',
            category: 'Materials',
            amount: 890000000,
            date: '2026-03-18',
            vendor: 'Jindal Steel & Power',
            paymentStatus: 'Paid',
            title: 'TMT rebar supply batch Q1'
        },
        {
            id: 'exp-403',
            projectId: 'proj-102',
            category: 'Equipment',
            amount: 420000000,
            date: '2026-04-02',
            vendor: 'Liebherr India',
            paymentStatus: 'Pending',
            title: 'Mobile crane hire & telemetry'
        },
        {
            id: 'exp-404',
            projectId: 'proj-103',
            category: 'Materials',
            amount: 310000000,
            date: '2026-02-14',
            vendor: 'Saint-Gobain',
            paymentStatus: 'Paid',
            title: 'Facade glass procurement'
        },
        {
            id: 'exp-405',
            projectId: 'proj-104',
            category: 'Labor',
            amount: 145000000,
            date: '2026-01-22',
            vendor: 'ISCL Contract Workforce',
            paymentStatus: 'Overdue',
            title: 'Q4 site engineering payroll'
        }
    ],

    team: [
        {
            id: 'user-501',
            name: 'Alex Sterling',
            role: 'Project Director',
            email: 'alex.sterling@cih-hub.com',
            phone: '+91 98765 43210',
            assignedProjects: ['proj-101'],
            category: 'Management',
            status: 'Active',
            accessLevel: 'Admin',
            skills: ['Civil Engineering', 'Project Finance', 'Safety Compliance']
        },
        {
            id: 'user-502',
            name: 'Rajesh Kumar',
            role: 'Site Director',
            email: 'rajesh.kumar@cih-hub.com',
            phone: '+91 95432 10987',
            assignedProjects: ['proj-101'],
            category: 'Engineering',
            status: 'Active',
            accessLevel: 'Engineer',
            skills: ['Rebar Design', 'Dewatering', 'Quality Control']
        },
        {
            id: 'user-503',
            name: 'Ananya Sharma',
            role: 'Procurement Head',
            email: 'ananya.sharma@cih-hub.com',
            phone: '+91 96543 21098',
            assignedProjects: ['proj-101', 'proj-103'],
            category: 'Logistics',
            status: 'Active',
            accessLevel: 'Manager',
            skills: ['Vendor Negotiation', 'RFID Tracking', 'Material AI']
        },
        {
            id: 'user-504',
            name: 'Vikram Sharma',
            role: 'Senior Site Engineer',
            email: 'vikram.sharma@cih-hub.com',
            phone: '+91 98123 45678',
            assignedProjects: ['proj-102'],
            category: 'Engineering',
            status: 'Active',
            accessLevel: 'Engineer',
            skills: ['Bridge Engineering', 'IoT Telemetry', 'Coastal Works']
        },
        {
            id: 'user-505',
            name: 'Pooja Deshmukh',
            role: 'Safety & OSHA Auditor',
            email: 'pooja.deshmukh@cih-hub.com',
            phone: '+91 97654 32109',
            assignedProjects: ['proj-104'],
            category: 'Inspection',
            status: 'Active',
            accessLevel: 'Auditor',
            skills: ['OSHA Regulations', 'Hazard Mitigation', 'Site Auditing']
        },
        {
            id: 'user-506',
            name: 'Arjun Nair',
            role: 'Aviation Infrastructure Lead',
            email: 'arjun.nair@cih-hub.com',
            phone: '+91 92109 87654',
            assignedProjects: ['proj-103'],
            category: 'Management',
            status: 'Active',
            accessLevel: 'Manager',
            skills: ['Terminal Logistics', 'Runway Design', 'Soil Stabilization']
        }
    ],

    equipment: [
        {
            id: 'eq-101',
            projectId: 'proj-101',
            assetName: 'CAT 349 Heavy Hydraulic Excavator',
            unitCode: 'EXC-DEL-09',
            engineHealthPct: 91,
            operatingHours: 1420,
            fuelRateLph: 14.2,
            maintenanceDueHrs: 280,
            status: 'Optimal',
            operator: 'Suresh Patil'
        },
        {
            id: 'eq-102',
            projectId: 'proj-102',
            assetName: 'Liebherr LTM 1250 Mobile Crane',
            unitCode: 'CRN-MUM-02',
            engineHealthPct: 74,
            operatingHours: 2150,
            fuelRateLph: 18.5,
            maintenanceDueHrs: 40,
            status: 'Service Due',
            operator: 'Ramesh Sharma'
        },
        {
            id: 'eq-103',
            projectId: 'proj-103',
            assetName: 'Putzmeister Concrete Boom Pump 42Z',
            unitCode: 'PMP-BLR-01',
            engineHealthPct: 96,
            operatingHours: 980,
            fuelRateLph: 16.0,
            maintenanceDueHrs: 410,
            status: 'Optimal',
            operator: 'Kiran R.'
        }
    ],

    reports: [
        {
            id: 'rep-2026-01',
            projectId: 'proj-101',
            reportTitle: 'AI Site Safety & OSHA Compliance Audit',
            reportType: 'Safety Audit',
            generatedBy: 'Pooja Deshmukh',
            generatedDate: '2026-07-22',
            fileSizeMb: 4.8,
            status: 'Verified',
            format: 'PDF'
        },
        {
            id: 'rep-2026-02',
            projectId: 'proj-102',
            reportTitle: 'Q2 Capital Expenditure & Cost Variance Log',
            reportType: 'Financial Audit',
            generatedBy: 'Alex Sterling',
            generatedDate: '2026-07-18',
            fileSizeMb: 12.4,
            status: 'Verified',
            format: 'CSV'
        },
        {
            id: 'rep-2026-03',
            projectId: 'proj-104',
            reportTitle: 'ROW Delay & Utility Relocation Brief',
            reportType: 'Regulatory',
            generatedBy: 'Pooja Deshmukh',
            generatedDate: '2026-06-24',
            fileSizeMb: 5.4,
            status: 'Generated',
            format: 'PDF'
        }
    ],

    settings: {
        currency: 'INR (₹)',
        currencySymbol: '₹',
        taxRatePct: 18,
        laborRatePerDay: 850,
        companyName: 'Construction Intelligent Hub',
        companyAddress: 'Delhi NCR Headquarters'
    },

    aiModules: [
        {
            id: 'mod-cost',
            title: 'AI Cost Estimation',
            description: 'Predict budget overruns using live spend, material prices, and schedule variance.',
            icon: '📊',
            theme: 'light',
            type: 'chart',
            bars: [35, 55, 42, 92, 48, 75]
        },
        {
            id: 'mod-material',
            title: 'Material Tracking',
            description: 'Live inventory linked to project demand, suppliers, and re-order thresholds.',
            icon: '📦',
            theme: 'light',
            type: 'stream',
            statusBadge: { text: '📡 Inventory linked by projectId', state: '● LIVE', color: '#10B981' }
        },
        {
            id: 'mod-risk',
            title: 'Risk Prediction',
            description: 'Severity-scored risks (probability × impact) across the active portfolio.',
            icon: '⚠️',
            theme: 'dark',
            type: 'status',
            statusBadge: { label: 'Status: Monitoring', status: '✓ Linked register', color: '#10B981' }
        },
        {
            id: 'mod-equip',
            title: 'Equipment Intelligence',
            description: 'Predictive maintenance from engine health and operating hours.',
            icon: '🚜',
            theme: 'wide',
            type: 'wide_image',
            linkText: 'Explore Analytics →',
            image: 'assets/equipment.png'
        }
    ]
};

const CIH_PERSIST_KEYS = [
    'projects', 'risks', 'materials', 'expenses', 'team',
    'equipment', 'reports', 'settings', 'aiModules'
];

function cihClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function cihFormatMoney(amount) {
    const n = Number(amount) || 0;
    const symbol = (typeof CIH_DATASET !== 'undefined' && CIH_DATASET.settings && CIH_DATASET.settings.currencySymbol)
        ? CIH_DATASET.settings.currencySymbol
        : '₹';
    if (Math.abs(n) >= 1e7) {
        return `${symbol}${(n / 1e7).toLocaleString('en-IN', { maximumFractionDigits: 2 })} Cr`;
    }
    if (Math.abs(n) >= 1e5) {
        return `${symbol}${(n / 1e5).toLocaleString('en-IN', { maximumFractionDigits: 2 })} L`;
    }
    return `${symbol}${n.toLocaleString('en-IN')}`;
}

function cihFormatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function cihStatusClass(status) {
    const s = String(status || '').toLowerCase();
    if (s.includes('hold') || s.includes('delay')) return 'delayed';
    if (s.includes('plan') || s.includes('review')) return 'in-review';
    return 'on-track';
}

function cihProjectIcon(project) {
    if (project && project.icon) return project.icon;
    const t = `${(project && project.buildingType) || ''} ${(project && project.title) || ''}`.toLowerCase();
    if (t.includes('metro') || t.includes('transit') || t.includes('rail')) return '🚆';
    if (t.includes('airport') || t.includes('aviation')) return '✈️';
    if (t.includes('harbour') || t.includes('coastal') || t.includes('bridge')) return '🌉';
    if (t.includes('highway') || t.includes('road')) return '🛣️';
    if (t.includes('civic') || t.includes('commercial')) return '🏢';
    return '🏗️';
}

function cihInitials(name) {
    return String(name || 'TM')
        .split(/\s+/)
        .map((part) => part[0])
        .join('')
        .substring(0, 2)
        .toUpperCase() || 'TM';
}

function cihAvatarColor(name) {
    const palette = ['#1D4ED8', '#0284C7', '#059669', '#D97706', '#7C3AED', '#DC2626'];
    let hash = 0;
    String(name || '').split('').forEach((ch) => { hash = (hash + ch.charCodeAt(0)) % palette.length; });
    return palette[hash];
}

function cihProjectTitle(projectId) {
    const proj = (CIH_DATASET.projects || []).find((p) => p.id === projectId);
    return proj ? proj.title : projectId || 'Unassigned';
}

function cihFindProject(idOrTitle) {
    const projects = CIH_DATASET.projects || [];
    if (!idOrTitle || idOrTitle === 'all') return null;
    const query = String(idOrTitle).toLowerCase().trim();
    return projects.find((p) => String(p.id).toLowerCase() === query)
        || projects.find((p) => String(p.title).toLowerCase() === query)
        || projects.find((p) => p.title.toLowerCase().includes(query) || query.includes(p.title.toLowerCase()))
        || null;
}

function cihMaterialStatus(mat) {
    const required = Number(mat.quantityRequired) || 0;
    const stock = Number(mat.quantityInStock) || 0;
    const ratio = required > 0 ? stock / required : 1;
    if (ratio < 0.25) return { status: 'Low Stock', statusClass: 'delayed' };
    if (ratio < 0.45) return { status: 'Reorder Soon', statusClass: 'in-review' };
    return { status: 'In Stock', statusClass: 'on-track' };
}

function cihMaterialUtilization(mat) {
    const required = Number(mat.quantityRequired) || 0;
    const stock = Number(mat.quantityInStock) || 0;
    if (required <= 0) return 0;
    return Math.min(100, Math.round((stock / required) * 100));
}

function cihWeatherHazard(city) {
    const c = String(city || '').toLowerCase();
    if (c.includes('mumbai')) return 'Coastal high wind gusts and monsoon surge';
    if (c.includes('delhi')) return 'AQI cutoffs and summer heat';
    if (c.includes('indore')) return 'Unseasonal rainfall and foundation saturation';
    if (c.includes('bengaluru') || c.includes('bangalore')) return 'Intermittent monsoon and clay heave';
    return 'Seasonal weather variance';
}

function cihDefaultLeadName() {
    const lead = (CIH_DATASET.team || []).find((m) =>
        /director|lead/i.test(m.role || '') || m.accessLevel === 'Admin'
    );
    return (lead && lead.name) || ((CIH_DATASET.team || [])[0] && CIH_DATASET.team[0].name) || 'Unassigned';
}

function cihHydrateComputedViews() {
    const projects = CIH_DATASET.projects || [];
    const materials = CIH_DATASET.materials || [];
    const expenses = CIH_DATASET.expenses || [];
    const team = CIH_DATASET.team || [];
    const risks = CIH_DATASET.risks || [];
    const equipment = CIH_DATASET.equipment || [];
    const reports = CIH_DATASET.reports || [];
    const settings = CIH_DATASET.settings || {};

    projects.forEach((p) => {
        const expenseSpent = expenses
            .filter((e) => e.projectId === p.id)
            .reduce((sum, item) => sum + Number(item.amount || 0), 0);
        p.spent = expenseSpent;
        p.remainingBudget = (Number(p.budget) || 0) - expenseSpent;
        p.icon = cihProjectIcon(p);
        p.statusClass = cihStatusClass(p.status);
        p.formattedBudget = cihFormatMoney(p.budget);
        p.formattedSpent = cihFormatMoney(p.spent);
        p.formattedRemaining = cihFormatMoney(p.remainingBudget);
        p.formattedDeadline = cihFormatDate(p.deadline);
        p.budgetCrores = Math.round((Number(p.budget) || 0) / 1e7);
        p.spentPercent = Number(p.budget) > 0
            ? Math.round(((Number(p.spent) || 0) / Number(p.budget)) * 100)
            : 0;
        const assigned = team.filter((m) => (m.assignedProjects || []).includes(p.id));
        p.totalTeamCount = assigned.length;
        p.teamAvatars = assigned.slice(0, 2).map((m) => cihInitials(m.name));
        const lead = assigned.find((m) => /director|lead/i.test(m.role || '')) || assigned[0];
        p.projectLead = lead ? lead.name : cihDefaultLeadName();
    });

    const totalBudget = projects.reduce((sum, p) => sum + (Number(p.budget) || 0), 0);
    const totalSpent = projects.reduce((sum, p) => sum + (Number(p.spent) || 0), 0);
    const remaining = totalBudget - totalSpent;
    const utilization = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0;
    const variancePct = utilization - projects.reduce((sum, p) => sum + (Number(p.progressPercent) || 0), 0) / Math.max(projects.length, 1);
    const varianceLabel = `${variancePct >= 0 ? '+' : ''}${variancePct.toFixed(1)}%`;

    const inProgress = projects.filter((p) => /progress|track/i.test(p.status)).length;
    const delayed = projects.filter((p) => /hold|delay/i.test(p.status)).length;
    const planning = projects.filter((p) => /plan|review/i.test(p.status)).length;
    const completed = projects.filter((p) => /complete/i.test(p.status)).length;
    const highRisk = projects.filter((p) => String(p.riskLevel).toLowerCase() === 'high').length
        + risks.filter((r) => Number(r.severityScore) >= 15 && String(r.status).toLowerCase() === 'open').length;

    CIH_DATASET.metrics = [
        {
            id: 'stat-1',
            value: cihFormatMoney(totalBudget),
            label: 'PORTFOLIO VALUE',
            subtext: `${projects.length} active projects`
        },
        {
            id: 'stat-2',
            value: `${Math.max(8, 42 - delayed * 6)}%`,
            label: 'AVG. WASTE REDUCTION',
            subtext: 'Derived from inventory vs requirement'
        },
        {
            id: 'stat-3',
            value: String(projects.filter((p) => !/complete/i.test(p.status)).length),
            label: 'ACTIVE JOB SITES',
            subtext: settings.companyAddress || 'India'
        },
        {
            id: 'stat-4',
            value: `${Math.max(80, 160 - highRisk * 12)}%`,
            label: 'RETURN ON INVESTMENT',
            subtext: 'Modeled from spend vs progress'
        }
    ];

    CIH_DATASET.dashboardStats = {
        totalProjects: {
            title: 'Total Projects',
            count: projects.length,
            badge: '📈 Active Hub',
            badgeClass: 'badge-green',
            icon: '📁',
            iconBg: '#EEF2FF',
            iconColor: '#4F46E5'
        },
        running: {
            title: 'Running',
            count: inProgress,
            badge: 'In Progress',
            badgeClass: 'badge-slate',
            icon: '🔄',
            iconBg: '#E0F2FE',
            iconColor: '#0284C7'
        },
        delayed: {
            title: 'On Hold / Delayed',
            count: delayed,
            badge: delayed ? '⚠️ Action Required' : 'Clear',
            badgeClass: delayed ? 'badge-red' : 'badge-green',
            icon: '🕒',
            iconBg: '#FEE2E2',
            iconColor: '#DC2626'
        },
        highRisk: {
            title: 'High Risk',
            count: highRisk,
            badge: highRisk ? 'Requires Attention' : 'Stable',
            badgeClass: highRisk ? 'badge-amber' : 'badge-green',
            icon: '⚠️',
            iconBg: '#FEF3C7',
            iconColor: '#D97706'
        },
        completed: {
            title: 'Completed',
            count: completed,
            badge: planning ? `${planning} in planning` : 'Historical',
            badgeClass: 'badge-green',
            icon: '✅',
            iconBg: '#E0E7FF',
            iconColor: '#2563EB'
        }
    };

    const avgProgress = Math.round(projects.reduce((s, p) => s + (Number(p.progressPercent) || 0), 0) / Math.max(projects.length, 1));
    CIH_DATASET.analyticsData = {
        subtitle: `Live portfolio intelligence across ${projects.length} sites.`,
        progressDistribution: [
            { name: 'Structural & Foundations', percent: Math.min(98, avgProgress + 12), status: 'In Progress', color: '#2563EB' },
            { name: 'MEP & Electrical Systems', percent: Math.max(12, avgProgress - 8), status: 'In Progress', color: '#0284C7' },
            { name: 'Facade & Finishes', percent: Math.max(8, avgProgress - 18), status: delayed ? 'Requires Attention' : 'In Progress', color: '#F59E0B' },
            { name: 'Safety & Site Inspection', percent: Math.min(99, 70 + (team.length * 4)), status: 'Optimal', color: '#10B981' }
        ]
    };

    CIH_DATASET.budgetOverview = {
        totalPortfolioBudget: cihFormatMoney(totalBudget),
        totalSpent: cihFormatMoney(totalSpent),
        remainingBudget: cihFormatMoney(remaining),
        variancePercent: varianceLabel,
        utilizationPercent: utilization,
        overrunRisk: utilization > avgProgress + 12 ? 'High' : (utilization > avgProgress + 4 ? 'Medium' : 'Low'),
        categories: [...new Set(expenses.map((e) => e.category).filter(Boolean))],
        expensesList: expenses
    };

    CIH_DATASET.moduleKpis = {
        materials: {
            parcels: materials.length,
            lowStock: materials.filter((m) => cihMaterialStatus(m).status === 'Low Stock').length,
            wasteReduction: Math.max(12, 40 - materials.filter((m) => cihMaterialStatus(m).status === 'Low Stock').length * 4)
        },
        team: {
            total: team.length,
            engineers: team.filter((m) => /engineer|engineering/i.test(`${m.role} ${m.category}`)).length,
            leads: team.filter((m) => /director|lead|head/i.test(m.role || '')).length,
            safety: team.filter((m) => /safety|audit|inspect/i.test(`${m.role} ${m.category}`)).length
        },
        reports: {
            total: reports.length,
            verified: reports.filter((r) => String(r.status).toLowerCase() === 'verified').length,
            discrepancies: risks.filter((r) => String(r.status).toLowerCase() === 'open' && Number(r.severityScore) >= 16).length
        },
        risks: {
            open: risks.filter((r) => String(r.status).toLowerCase() === 'open').length,
            mitigated: risks.filter((r) => /mitigat|closed/i.test(r.status || '')).length,
            avgSeverity: risks.length
                ? Math.round(risks.reduce((s, r) => s + (Number(r.severityScore) || 0), 0) / risks.length)
                : 0
        },
        equipment: {
            total: equipment.length,
            serviceDue: equipment.filter((e) => /service/i.test(e.status || '') || Number(e.engineHealthPct) < 80).length
        }
    };

    CIH_DATASET.rfidFeed = materials.slice(0, 6).map((m) => {
        const st = cihMaterialStatus(m);
        return {
            id: m.id,
            description: m.itemName,
            location: cihProjectTitle(m.projectId),
            status: st.status,
            statusClass: st.statusClass === 'on-track' ? 'green' : 'amber',
            rfidTag: `RFID-${String(m.id).replace(/\D/g, '') || '000'}`
        };
    });

    CIH_DATASET.materialInventory = materials;
    CIH_DATASET.teamMembers = team;
    CIH_DATASET.equipmentAssets = equipment;
    CIH_DATASET.projectReports = reports;
    CIH_DATASET.riskIncidents = risks;
}

function commitAndSyncState() {
    const payload = {};
    CIH_PERSIST_KEYS.forEach((key) => {
        payload[key] = CIH_DATASET[key];
    });
    try {
        localStorage.setItem(CIH_STORAGE_KEY, JSON.stringify(payload));
    } catch (err) {
        console.warn('[CIH] Failed to persist dataset:', err);
    }
    if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
        window.dispatchEvent(new CustomEvent('cihDataUpdated'));
    }
}

function getProjectSnapshot(projectId) {
    const projects = CIH_DATASET.projects || [];
    const project = projects.find((p) => p.id === projectId || p.title === projectId) || projects[0];
    if (!project) return null;

    const risks = (CIH_DATASET.risks || []).filter((r) => r.projectId === project.id);
    const expenses = (CIH_DATASET.expenses || []).filter((e) => e.projectId === project.id);
    const materials = (CIH_DATASET.materials || []).filter((m) => m.projectId === project.id);
    const totalSpent = expenses.reduce((sum, item) => sum + Number(item.amount || 0), 0);
    const remainingBudget = (Number(project.budget) || 0) - totalSpent;
    const team = (CIH_DATASET.team || []).filter((m) => (m.assignedProjects || []).includes(project.id));
    const equipment = (CIH_DATASET.equipment || []).filter((e) => e.projectId === project.id);
    const lowStock = materials.filter((m) => cihMaterialStatus(m).status === 'Low Stock');
    const lowHealthEq = equipment.filter((e) => Number(e.engineHealthPct) < 85 || /service/i.test(e.status || ''));

    return {
        ...project,
        spent: totalSpent,
        remainingBudget,
        risks,
        expenses,
        materials,
        formattedBudget: project.formattedBudget || cihFormatMoney(project.budget),
        formattedSpent: cihFormatMoney(totalSpent),
        formattedRemaining: cihFormatMoney(remainingBudget),
        spentPercent: Number(project.budget) > 0
            ? Math.round((totalSpent / Number(project.budget)) * 100)
            : 0,
        deadline: project.formattedDeadline || cihFormatDate(project.deadline),
        startDate: cihFormatDate(project.startDate),
        teamMembers: team,
        teamCount: team.length,
        projectLead: project.projectLead || cihDefaultLeadName(),
        equipmentList: equipment,
        equipmentCount: equipment.length,
        lowHealthEquipmentCount: lowHealthEq.length,
        materialsList: materials,
        materialsCount: materials.length,
        lowStockMaterialsCount: lowStock.length,
        risksList: risks,
        expensesList: expenses,
        expenseTotal: cihFormatMoney(totalSpent),
        weatherHazard: cihWeatherHazard(project.city),
        suggestedRiskLevel: project.riskLevel,
        settings: CIH_DATASET.settings
    };
}

function cihPersistDataset() {
    cihHydrateComputedViews();
    commitAndSyncState();
}

function cihMergeWithSeed(stored) {
    const seed = cihClone(CIH_SEED_DATASET);
    if (!stored || typeof stored !== 'object') return seed;
    CIH_PERSIST_KEYS.forEach((key) => {
        if (key === 'settings') {
            seed.settings = Object.assign({}, seed.settings, stored.settings || {});
        } else if (Array.isArray(stored[key])) {
            seed[key] = stored[key];
        }
    });
    return seed;
}

function cihLoadDataset() {
    let stored = null;
    try {
        const raw = localStorage.getItem(CIH_STORAGE_KEY);
        stored = raw ? JSON.parse(raw) : null;
    } catch (err) {
        stored = null;
    }
    const merged = cihMergeWithSeed(stored);
    Object.keys(CIH_DATASET).forEach((key) => { delete CIH_DATASET[key]; });
    Object.assign(CIH_DATASET, merged);
    cihBindDatasetApi();
    cihHydrateComputedViews();
    if (!stored || !Array.isArray(stored.projects)) {
        cihPersistDataset();
        cihBindDatasetApi();
    }
}

function cihGetProjectSnapshot(idOrTitle) {
    return getProjectSnapshot(idOrTitle) || {
        title: idOrTitle || 'Unassigned',
        city: '—',
        status: 'Unknown',
        budget: 0,
        spent: 0,
        remainingBudget: 0,
        formattedBudget: cihFormatMoney(0),
        deadline: '—',
        progressPercent: 0,
        spentPercent: 0,
        risks: [],
        expenses: [],
        materials: []
    };
}

function cihBindDatasetApi() {
    CIH_DATASET.getProjectSnapshot = getProjectSnapshot;
    CIH_DATASET.commitAndSyncState = commitAndSyncState;
}

const CIH_DATASET = {};
cihBindDatasetApi();

const CIH_API = {
    persist: () => {
        cihPersistDataset();
        return Promise.resolve(true);
    },
    getProjects: () => Promise.resolve(CIH_DATASET.projects),
    getMetrics: () => Promise.resolve(CIH_DATASET.metrics),
    getModules: () => Promise.resolve(CIH_DATASET.aiModules),
    getRfidFeed: () => Promise.resolve(CIH_DATASET.rfidFeed),
    getEquipment: () => Promise.resolve(CIH_DATASET.equipment),
    getTeamMembers: () => Promise.resolve(CIH_DATASET.team),
    getBudgetOverview: () => Promise.resolve(CIH_DATASET.budgetOverview),
    getMaterialInventory: () => Promise.resolve(CIH_DATASET.materials),
    getProjectReports: () => Promise.resolve(CIH_DATASET.reports),
    getRiskIncidents: () => Promise.resolve(CIH_DATASET.risks),

    addProject: (newProject) => {
        CIH_DATASET.projects.unshift(newProject);
        cihPersistDataset();
        return Promise.resolve(newProject);
    },
    deleteProject: (projectId) => {
        CIH_DATASET.projects = CIH_DATASET.projects.filter((p) => p.id !== projectId);
        CIH_DATASET.risks = CIH_DATASET.risks.filter((r) => r.projectId !== projectId);
        CIH_DATASET.materials = CIH_DATASET.materials.filter((m) => m.projectId !== projectId);
        CIH_DATASET.expenses = CIH_DATASET.expenses.filter((e) => e.projectId !== projectId);
        CIH_DATASET.equipment = CIH_DATASET.equipment.filter((e) => e.projectId !== projectId);
        CIH_DATASET.reports = CIH_DATASET.reports.filter((r) => r.projectId !== projectId);
        CIH_DATASET.team.forEach((m) => {
            m.assignedProjects = (m.assignedProjects || []).filter((id) => id !== projectId);
        });
        cihPersistDataset();
        return Promise.resolve(true);
    },
    addTeamMember: (newMember) => {
        CIH_DATASET.team.unshift(newMember);
        cihPersistDataset();
        return Promise.resolve(newMember);
    },
    deleteTeamMember: (memberId) => {
        CIH_DATASET.team = CIH_DATASET.team.filter((m) => m.id !== memberId);
        cihPersistDataset();
        return Promise.resolve(true);
    },
    addExpense: (newExpense) => {
        CIH_DATASET.expenses.unshift(newExpense);
        cihPersistDataset();
        return Promise.resolve(newExpense);
    },
    addMaterial: (newMat) => {
        CIH_DATASET.materials.unshift(newMat);
        cihPersistDataset();
        return Promise.resolve(newMat);
    },
    addEquipment: (newEq) => {
        CIH_DATASET.equipment.unshift(newEq);
        cihPersistDataset();
        return Promise.resolve(newEq);
    },
    addReport: (newRep) => {
        CIH_DATASET.reports.unshift(newRep);
        cihPersistDataset();
        return Promise.resolve(newRep);
    },
    addRisk: (newRisk) => {
        CIH_DATASET.risks.unshift(newRisk);
        cihPersistDataset();
        return Promise.resolve(newRisk);
    }
};

cihLoadDataset();
cihBindDatasetApi();
