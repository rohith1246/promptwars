/**
 * FairShift - Frontend Application Logic
 * Implements:
 * 1. Attendance & Overtime Shift Tracking
 * 2. Transparent Multilingual Payslip Engine (English, Hindi, Tamil)
 * 3. Zero-Knowledge Anonymous Grievance & Safety Reporting
 * Supports Construction & College Industries
 */

const state = {
  industry: "construction",
  role: "worker",
  language: "en",
  workers: [],
  selectedWorkerId: null,
  activeCheckIn: null
};

document.addEventListener("DOMContentLoaded", async () => {
  initLucide();
  await refreshAll();
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

async function refreshAll() {
  await loadWorkers();
  await loadStats();
  await loadAttendance();
  await loadGrievances();
}

// ============================================================
// INDUSTRY & ROLE SWITCHING
// ============================================================

async function changeIndustry() {
  const select = document.getElementById("industrySelect");
  state.industry = select.value;

  const icon = document.getElementById("industryIcon");
  const title = document.getElementById("industryTitle");
  const desc = document.getElementById("industryDesc");

  if (state.industry === "construction") {
    icon.innerHTML = `<i data-lucide="hard-hat" class="w-5 h-5"></i>`;
    title.innerText = "Active Sector: Construction Site Operations (Skyline Infrastructure)";
    desc.innerText = "Monitoring high-risk site shifts, automated overtime multipliers, scaffolding hazard reporting, and fair wage calculation.";
  } else {
    icon.innerHTML = `<i data-lucide="graduation-cap" class="w-5 h-5"></i>`;
    title.innerText = "Active Sector: College Operations (SRM University Campus Facilities)";
    desc.innerText = "Managing campus sanitation shifts, security rosters, laboratory hazard reports, and transparent hourly wages.";
  }

  await refreshAll();
  initLucide();
}

function switchRole(role) {
  state.role = role;
  const workerView = document.getElementById("workerView");
  const employerView = document.getElementById("employerView");
  const workerBtn = document.getElementById("roleWorkerBtn");
  const employerBtn = document.getElementById("roleEmployerBtn");

  if (role === "worker") {
    workerView.classList.remove("hidden");
    employerView.classList.add("hidden");
    workerBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md bg-brand-600 text-white shadow-sm transition flex items-center space-x-1.5 focus:outline-none";
    employerBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md text-slate-600 hover:text-slate-900 transition flex items-center space-x-1.5 focus:outline-none";
  } else {
    workerView.classList.add("hidden");
    employerView.classList.remove("hidden");
    employerBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md bg-brand-600 text-white shadow-sm transition flex items-center space-x-1.5 focus:outline-none";
    workerBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md text-slate-600 hover:text-slate-900 transition flex items-center space-x-1.5 focus:outline-none";
    loadStats();
    loadAttendance();
    loadGrievances();
  }
  initLucide();
}

// ============================================================
// WORKER MANAGEMENT & IDENTITY
// ============================================================

async function loadWorkers() {
  try {
    const res = await fetch(`/api/workers?industry=${state.industry}`);
    const data = await res.json();
    state.workers = data;

    const select = document.getElementById("workerSelector");
    select.innerHTML = data.map(w => `<option value="${w.id}">${w.name} (${w.role})</option>`).join("");

    if (data.length > 0) {
      state.selectedWorkerId = data[0].id;
      updateWorkerDisplay(data[0]);
      await fetchWorkerPayslip();
    }

    document.getElementById("workerCountBadge").innerText = `${data.length} Active Workers`;
  } catch (err) {
    console.error("Failed to load workers:", err);
  }
}

function onWorkerChange() {
  const select = document.getElementById("workerSelector");
  const workerId = parseInt(select.value);
  state.selectedWorkerId = workerId;
  const worker = state.workers.find(w => w.id === workerId);
  if (worker) {
    updateWorkerDisplay(worker);
    fetchWorkerPayslip();
  }
}

function updateWorkerDisplay(worker) {
  document.getElementById("currentWorkerName").innerText = worker.name;
  document.getElementById("currentWorkerRole").innerText = worker.role;
  document.getElementById("currentWorkerCode").innerText = worker.worker_code;
}

// ============================================================
// FEATURE 1: ATTENDANCE & OVERTIME SHIFT TRACKING
// ============================================================

async function doCheckIn() {
  if (!state.selectedWorkerId) return;

  try {
    const res = await fetch("/api/check-in", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ worker_id: state.selectedWorkerId })
    });
    const data = await res.json();
    
    const badge = document.getElementById("shiftStatusBadge");
    badge.className = "px-2 py-0.5 text-[11px] font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300";
    badge.innerText = "Shift In Progress (Clocked In)";

    alert(data.message || "Clocked in successfully!");
    await refreshAll();
  } catch (err) {
    alert("Check-in failed: " + err.message);
  }
}

async function doCheckOut() {
  if (!state.selectedWorkerId) return;
  const hoursInput = document.getElementById("simulatedHoursInput");
  const simulatedHours = parseFloat(hoursInput.value) || 10.5;

  try {
    const res = await fetch("/api/check-out", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        worker_id: state.selectedWorkerId,
        simulated_hours: simulatedHours
      })
    });
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    const badge = document.getElementById("shiftStatusBadge");
    badge.className = "px-2 py-0.5 text-[11px] font-bold rounded-full bg-slate-100 text-slate-700";
    badge.innerText = "Shift Completed";

    const otText = data.attendance.overtime_hours > 0 ? ` including ${data.attendance.overtime_hours} hrs overtime (1.5x)` : "";
    alert(`Clock-out recorded! Logged ${data.attendance.total_hours} hrs${otText}. Transparent payslip updated.`);

    await fetchWorkerPayslip();
    await loadAttendance();
    await loadStats();
  } catch (err) {
    alert("Check-out failed: " + err.message);
  }
}

// ============================================================
// FEATURE 2: TRANSPARENT MULTILINGUAL PAYSLIP
// ============================================================

function setPayslipLanguage(lang) {
  state.language = lang;
  
  ["en", "hi", "ta"].forEach(l => {
    const btn = document.getElementById(`lang${l.charAt(0).toUpperCase() + l.slice(1)}Btn`);
    if (l === lang) {
      btn.className = "px-2 py-0.5 text-[11px] font-bold rounded bg-indigo-600 text-white";
    } else {
      btn.className = "px-2 py-0.5 text-[11px] font-bold rounded bg-slate-100 text-slate-700";
    }
  });

  fetchWorkerPayslip();
}

async function fetchWorkerPayslip() {
  if (!state.selectedWorkerId) return;

  try {
    const res = await fetch(`/api/payslip/${state.selectedWorkerId}?lang=${state.language}`);
    const data = await res.json();
    if (data.error) return;

    // Update labels and values
    document.getElementById("lblBasePay").innerText = data.labels.base_pay + ":";
    document.getElementById("lblOvertimePay").innerText = data.labels.overtime_pay + ":";
    document.getElementById("lblDeductions").innerText = data.labels.deductions + ":";
    document.getElementById("lblNetPay").innerText = data.labels.net_pay + ":";

    document.getElementById("valBasePay").innerText = `₹${data.base_pay.toFixed(2)}`;
    document.getElementById("valOvertimePay").innerText = `+₹${data.overtime_pay.toFixed(2)} (${data.total_overtime_hours}h)`;
    document.getElementById("valDeductions").innerText = `-₹${data.deductions.toFixed(2)}`;
    document.getElementById("valNetPay").innerText = `₹${data.net_pay.toFixed(2)}`;

    document.getElementById("valFormulaExplanation").innerText = data.formula_explanation;

    // Fatigue status indicator
    const fatigueBox = document.getElementById("fatigueAlertBox");
    const fatigueText = document.getElementById("fatigueStatusText");
    fatigueText.innerText = data.fatigue_status;

    if (data.is_fatigued) {
      fatigueBox.className = "p-2.5 rounded-lg border text-[11px] font-semibold bg-rose-50 text-rose-800 border-rose-300";
    } else {
      fatigueBox.className = "p-2.5 rounded-lg border text-[11px] font-semibold bg-emerald-50 text-emerald-800 border-emerald-200";
    }

    document.getElementById("todayHoursDisplay").innerText = `${data.total_work_hours} hrs total`;
  } catch (err) {
    console.error("Failed to load payslip:", err);
  }
}

// ============================================================
// FEATURE 3: ANONYMOUS GRIEVANCE & SAFETY REPORTING
// ============================================================

async function submitGrievance(e) {
  e.preventDefault();
  const category = document.getElementById("grievanceCategory").value;
  const urgency = document.getElementById("grievanceUrgency").value;
  const description = document.getElementById("grievanceDescription").value.trim();

  if (!description) {
    alert("Please provide an incident description.");
    return;
  }

  try {
    const res = await fetch("/api/grievances", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        industry: state.industry,
        category: category,
        urgency: urgency,
        description: description
      })
    });

    const data = await res.json();
    if (data.error) {
      alert("Submission error: " + data.error);
      return;
    }

    alert(`Zero-Knowledge Report Submitted!\n\nYour Anonymous Ticket Code: ${data.ticket_code}\n\nSave this code to check resolution progress without revealing your identity.`);
    document.getElementById("grievanceDescription").value = "";
    document.getElementById("trackCodeInput").value = data.ticket_code;
    trackTicket();
    await loadGrievances();
    await loadStats();
  } catch (err) {
    alert("Failed to submit grievance: " + err.message);
  }
}

async function trackTicket() {
  const code = document.getElementById("trackCodeInput").value.trim().toUpperCase();
  if (!code) return;

  const resultBox = document.getElementById("trackResultBox");
  resultBox.classList.remove("hidden");
  resultBox.innerHTML = `<span class="text-slate-400">Checking ticket status...</span>`;

  try {
    const res = await fetch(`/api/grievances/track/${code}`);
    const data = await res.json();
    if (data.error) {
      resultBox.innerHTML = `<span class="text-rose-600 font-bold">${data.error}</span>`;
      return;
    }

    let statusBadge = "bg-amber-100 text-amber-800";
    if (data.status === "Resolved") statusBadge = "bg-emerald-100 text-emerald-800";

    resultBox.innerHTML = `
      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <strong class="text-slate-900">${data.ticket_code} (${data.category})</strong>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${statusBadge}">${data.status}</span>
        </div>
        <p class="text-slate-600 text-[11px]"><strong>Report:</strong> ${data.description}</p>
        <p class="text-slate-800 text-[11px] bg-white p-2 rounded border border-slate-200">
          <strong>Action Note:</strong> ${data.resolution_note}
        </p>
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<span class="text-rose-600">Error tracking ticket.</span>`;
  }
}

// ============================================================
// EMPLOYER DASHBOARD DATA
// ============================================================

async function loadStats() {
  try {
    const res = await fetch(`/api/stats?industry=${state.industry}`);
    const data = await res.json();

    document.getElementById("kpiWorkforce").innerText = data.total_workforce;
    document.getElementById("kpiHours").innerText = data.total_hours_logged;
    document.getElementById("kpiOvertime").innerText = `${data.total_overtime_hours} hrs overtime`;
    document.getElementById("kpiGrievances").innerText = data.open_grievances;
    document.getElementById("kpiCritical").innerText = `${data.critical_safety_alerts} Critical Hazard(s)`;
    document.getElementById("kpiSDG").innerText = `${data.sdg_compliance_score}%`;

    const fatigueBanner = document.getElementById("employerFatigueBanner");
    const fatigueDesc = document.getElementById("fatigueBannerDesc");
    if (data.fatigued_workers_count > 0) {
      fatigueBanner.classList.remove("hidden");
      fatigueDesc.innerText = `${data.fatigued_workers_count} worker(s) in this sector have exceeded the 48-hour weekly labor cap. Rotating shifts is recommended to prevent fatigue-induced accidents.`;
    } else {
      fatigueBanner.classList.add("hidden");
    }
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

async function loadAttendance() {
  try {
    const res = await fetch(`/api/attendance?industry=${state.industry}`);
    const records = await res.json();
    const tbody = document.getElementById("attendanceTableBody");

    if (records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-3 text-center text-slate-400">No shift records yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => `
      <tr class="hover:bg-slate-50">
        <td class="py-2 px-2.5 font-bold text-slate-900">${r.worker_name} <span class="text-[10px] text-slate-400 font-normal">(${r.worker_code})</span></td>
        <td class="py-2 px-2.5 text-slate-500">${r.date}</td>
        <td class="py-2 px-2.5 font-semibold">${r.regular_hours} hrs</td>
        <td class="py-2 px-2.5 font-semibold ${r.overtime_hours > 0 ? 'text-emerald-700' : 'text-slate-400'}">${r.overtime_hours} hrs</td>
        <td class="py-2 px-2.5">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.status === 'completed' ? 'bg-slate-100 text-slate-700' : 'bg-emerald-100 text-emerald-800'}">
            ${r.status === 'completed' ? 'Completed' : 'Active Shift'}
          </span>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load attendance:", err);
  }
}

async function loadGrievances() {
  try {
    const res = await fetch(`/api/grievances?industry=${state.industry}`);
    const grievances = await res.json();
    const container = document.getElementById("grievanceListContainer");

    if (grievances.length === 0) {
      container.innerHTML = `<div class="p-4 text-center text-slate-400 text-xs">No grievances reported for this sector.</div>`;
      return;
    }

    container.innerHTML = grievances.map(g => {
      let urgencyBadge = "bg-slate-100 text-slate-700";
      if (g.urgency === "Critical") urgencyBadge = "bg-rose-100 text-rose-800 font-bold border border-rose-300";
      if (g.urgency === "Medium") urgencyBadge = "bg-amber-100 text-amber-800";

      let statusBadge = "bg-amber-100 text-amber-800";
      if (g.status === "Resolved") statusBadge = "bg-emerald-100 text-emerald-800";

      return `
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-1.5">
              <span class="font-bold text-slate-900">${g.ticket_code}</span>
              <span class="px-2 py-0.5 rounded text-[10px] ${urgencyBadge}">${g.urgency}</span>
              <span class="text-slate-500 font-medium">(${g.category})</span>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${statusBadge}">${g.status}</span>
          </div>

          <p class="text-slate-700 leading-snug">${g.description}</p>
          <div class="text-[11px] text-slate-500 bg-white p-2 rounded border border-slate-200">
            <strong>Action Note:</strong> ${g.resolution_note}
          </div>

          <!-- Employer Status Triage Action -->
          <div class="flex items-center justify-between pt-1 border-t border-slate-200 text-[11px]">
            <span class="text-slate-400">Logged: ${g.created_at || 'Recently'}</span>
            <div class="space-x-1">
              ${g.status !== 'Under Investigation' && g.status !== 'Resolved' ? `
                <button onclick="updateGrievance('${g.ticket_code}', 'Under Investigation')" class="px-2 py-0.5 bg-amber-500 hover:bg-amber-600 text-white rounded font-semibold">Mark Investigating</button>
              ` : ''}
              ${g.status !== 'Resolved' ? `
                <button onclick="updateGrievance('${g.ticket_code}', 'Resolved')" class="px-2 py-0.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-semibold">Mark Resolved</button>
              ` : '<span class="text-emerald-700 font-bold">✓ Case Closed</span>'}
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Failed to load grievances:", err);
  }
}

async function updateGrievance(ticketCode, status) {
  const note = prompt(`Enter corrective action / resolution note for ticket ${ticketCode}:`, status === "Resolved" ? "Corrective action verified on site. Issue resolved." : "Investigating on site.");
  if (note === null) return;

  try {
    const res = await fetch("/api/grievances/update-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticket_code: ticketCode,
        status: status,
        resolution_note: note
      })
    });
    const data = await res.json();
    alert(data.message || "Grievance status updated.");
    await loadGrievances();
    await loadStats();
  } catch (err) {
    alert("Failed to update status: " + err.message);
  }
}
