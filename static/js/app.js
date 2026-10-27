/**
 * FairShift - Frontend Application Logic with Role-Based Authentication
 * 1. Secure Authentication Flow (Worker Login with ID + PIN, Admin Login with Password)
 * 2. 1-Click Evaluator/Judge Quick Login presets
 * 3. Attendance & Shift Overtime Tracking
 * 4. Transparent Multilingual Payslip Engine
 * 5. Anonymous Grievance & Safety Incident Reporting
 */

const state = {
  authenticated: false,
  currentUser: null,
  industry: "construction",
  language: "en",
  workers: [],
  selectedWorkerId: null
};

document.addEventListener("DOMContentLoaded", async () => {
  initLucide();
  await checkAuth();
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// ============================================================
// AUTHENTICATION & SESSION MANAGEMENT
// ============================================================

async function checkAuth() {
  try {
    const res = await fetch("/api/auth/me");
    const data = await res.json();

    if (data.authenticated && data.user) {
      applyAuthState(data.user);
    } else {
      showLoginScreen();
    }
  } catch (err) {
    showLoginScreen();
  }
}

function showLoginScreen() {
  state.authenticated = false;
  state.currentUser = null;

  document.getElementById("loginScreen").classList.remove("hidden");
  document.getElementById("authenticatedPortal").classList.add("hidden");
  document.getElementById("authenticatedControls").classList.add("hidden");
  initLucide();
}

async function applyAuthState(user) {
  state.authenticated = true;
  state.currentUser = user;

  document.getElementById("loginScreen").classList.add("hidden");
  document.getElementById("authenticatedPortal").classList.remove("hidden");
  document.getElementById("authenticatedControls").classList.remove("hidden");

  // Update top bar user info
  document.getElementById("navUserName").innerText = user.name;
  const roleBadge = document.getElementById("navRoleBadge");

  if (user.role === "admin") {
    roleBadge.innerText = "Admin";
    roleBadge.className = "px-1.5 py-0.2 rounded text-[10px] font-bold bg-slate-200 text-slate-800 uppercase";
    document.getElementById("industrySelectorWrap").classList.remove("hidden");

    // Show Admin dashboard
    document.getElementById("workerView").classList.add("hidden");
    document.getElementById("employerView").classList.remove("hidden");

    await loadStats();
    await loadAttendance();
    await loadGrievances();
  } else {
    // Worker logged in
    roleBadge.innerText = "Worker";
    roleBadge.className = "px-1.5 py-0.2 rounded text-[10px] font-bold bg-brand-100 text-brand-800 uppercase";
    document.getElementById("industrySelectorWrap").classList.add("hidden");

    // Set industry based on worker's assigned industry
    state.industry = user.industry || "construction";
    state.selectedWorkerId = user.worker_id;

    // Show Worker Portal
    document.getElementById("workerView").classList.remove("hidden");
    document.getElementById("employerView").classList.add("hidden");

    document.getElementById("currentWorkerName").innerText = user.name;
    document.getElementById("currentWorkerRole").innerText = user.job_role;
    document.getElementById("currentWorkerCode").innerText = user.worker_code;

    await fetchWorkerPayslip();
  }

  initLucide();
}

function setLoginTab(tab) {
  const workerTabBtn = document.getElementById("loginTabWorker");
  const adminTabBtn = document.getElementById("loginTabAdmin");
  const workerForm = document.getElementById("workerLoginForm");
  const adminForm = document.getElementById("adminLoginForm");

  if (tab === "worker") {
    workerTabBtn.className = "py-2 rounded-lg bg-white text-slate-900 shadow-sm transition";
    adminTabBtn.className = "py-2 rounded-lg text-slate-500 hover:text-slate-900 transition";
    workerForm.classList.remove("hidden");
    adminForm.classList.add("hidden");
  } else {
    adminTabBtn.className = "py-2 rounded-lg bg-white text-slate-900 shadow-sm transition";
    workerTabBtn.className = "py-2 rounded-lg text-slate-500 hover:text-slate-900 transition";
    adminForm.classList.remove("hidden");
    workerForm.classList.add("hidden");
  }
}

async function submitWorkerLogin(e) {
  e.preventDefault();
  const code = document.getElementById("workerCodeInput").value.trim().toUpperCase();
  const pin = document.getElementById("workerPinInput").value.trim();

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: "worker", worker_code: code, pin: pin })
    });
    const data = await res.json();
    if (data.error) {
      alert("Sign-in error: " + data.error);
      return;
    }
    applyAuthState(data.user);
  } catch (err) {
    alert("Login failed: " + err.message);
  }
}

async function submitAdminLogin(e) {
  e.preventDefault();
  const username = document.getElementById("adminUsernameInput").value.trim();
  const password = document.getElementById("adminPasswordInput").value.trim();

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: "admin", username: username, password: password })
    });
    const data = await res.json();
    if (data.error) {
      alert("Sign-in error: " + data.error);
      return;
    }
    applyAuthState(data.user);
  } catch (err) {
    alert("Admin login failed: " + err.message);
  }
}

async function quickLogin(codeOrUser, role) {
  if (role === "admin") {
    document.getElementById("adminUsernameInput").value = "admin";
    document.getElementById("adminPasswordInput").value = "fairshift2026";
    setLoginTab("admin");
    const fakeEvent = { preventDefault: () => {} };
    await submitAdminLogin(fakeEvent);
  } else {
    document.getElementById("workerCodeInput").value = codeOrUser;
    document.getElementById("workerPinInput").value = "1234";
    setLoginTab("worker");
    const fakeEvent = { preventDefault: () => {} };
    await submitWorkerLogin(fakeEvent);
  }
}

async function doLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
    showLoginScreen();
  } catch (err) {
    showLoginScreen();
  }
}

// ============================================================
// INDUSTRY SWITCHING (ADMIN MODE)
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

  await loadStats();
  await loadAttendance();
  await loadGrievances();
  initLucide();
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
    await fetchWorkerPayslip();
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

    document.getElementById("lblBasePay").innerText = data.labels.base_pay + ":";
    document.getElementById("lblOvertimePay").innerText = data.labels.overtime_pay + ":";
    document.getElementById("lblDeductions").innerText = data.labels.deductions + ":";
    document.getElementById("lblNetPay").innerText = data.labels.net_pay + ":";

    document.getElementById("valBasePay").innerText = `₹${data.base_pay.toFixed(2)}`;
    document.getElementById("valOvertimePay").innerText = `+₹${data.overtime_pay.toFixed(2)} (${data.total_overtime_hours}h)`;
    document.getElementById("valDeductions").innerText = `-₹${data.deductions.toFixed(2)}`;
    document.getElementById("valNetPay").innerText = `₹${data.net_pay.toFixed(2)}`;

    document.getElementById("valFormulaExplanation").innerText = data.formula_explanation;

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
