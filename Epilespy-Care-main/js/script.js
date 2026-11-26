const API_BASE = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
    // ======================================
    // 1. REGISTRATION FORM (register.html)
    // ======================================
    const roleSelect = document.getElementById("role");
    const phoneGroup = document.getElementById("phoneGroup");
    const doctorFields = document.getElementById("doctorFields");
    const registerForm = document.getElementById("registerForm");

    const params = new URLSearchParams(window.location.search);
    const inviteToken = params.get("invite") || "";

    function updateRoleFields() {
        if (!roleSelect) return;
        const isDoctor = roleSelect.value === "doctor";
        if (doctorFields) doctorFields.style.display = isDoctor ? "block" : "none";
        if (phoneGroup) phoneGroup.style.display = isDoctor ? "none" : "block";
    }

    if (roleSelect) {
        roleSelect.addEventListener("change", updateRoleFields);

        // If a caregiver opened an invitation link, pre-select Caregiver and pre-fill their email
        if (inviteToken) {
            roleSelect.value = "caregiver";
            roleSelect.disabled = true;
            updateRoleFields();

            fetch(`${API_BASE}/api/caregiver/invite/${inviteToken}`)
                .then((res) => res.json())
                .then((data) => {
                    if (data.caregiver_email) {
                        const emailInput = document.getElementById("email");
                        if (emailInput) emailInput.value = data.caregiver_email;
                    }
                })
                .catch((err) => console.error("Invite check error:", err));
        } else {
            updateRoleFields();
        }
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const role = document.getElementById("role").value;
            const payload = {
                role,
                fullName: document.getElementById("fullName").value.trim(),
                email: document.getElementById("email").value.trim(),
                password: document.getElementById("password").value,
                phone: document.getElementById("phone").value.trim(),
                registrationNo: document.getElementById("registrationNo").value.trim(),
                facility: document.getElementById("facility").value.trim(),
                inviteToken
            };

            try {
                const res = await fetch(`${API_BASE}/api/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();
                if (!res.ok) {
                    alert(data.error || data.message || "Registration failed.");
                    return;
                }

                alert("Account created! Redirecting to login...");
                window.location.href = `${role}/login.html`;
            } catch (err) {
                console.error("Register fetch error:", err);
                alert("Could not reach the server. Make sure Flask is running.");
            }
        });
    }

    // ======================================
    // 2. LOGIN FORMS (patient, doctor, caregiver, admin)
    // ======================================
    function setupLoginForm(formId, role, redirectPage) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            try {
                const res = await fetch(`${API_BASE}/api/login/${role}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });

                const data = await res.json();
                if (!res.ok) {
                    alert(data.error || data.message || "Invalid email or password.");
                    return;
                }

                // Save logged-in user details so the dashboard knows who is logged in
                localStorage.setItem("currentUser", JSON.stringify(data));
                localStorage.setItem("role", role);
                localStorage.setItem("full_name", data.full_name || "");
                if (data.patient_id) localStorage.setItem("patient_id", data.patient_id);
                if (data.doctor_id) localStorage.setItem("doctor_id", data.doctor_id);
                if (data.caregiver_id) localStorage.setItem("caregiver_id", data.caregiver_id);
                if (data.admin_id) localStorage.setItem("admin_id", data.admin_id);
                if (data.linked_patient_id) localStorage.setItem("linked_patient_id", data.linked_patient_id);

                window.location.href = redirectPage;
            } catch (err) {
                console.error(`${role} login error:`, err);
                alert("Could not reach the server. Make sure Flask is running.");
            }
        });
    }

    setupLoginForm("patientLoginForm", "patient", "patient.html");
    setupLoginForm("doctorLoginForm", "doctor", "doctor.html");
    setupLoginForm("caregiverLoginForm", "caregiver", "caregiver.html");
    setupLoginForm("adminLoginForm", "admin", "admin.html");

    // ======================================
    // 3. CAREGIVER DASHBOARD COUNTS (HELP REQUESTS & DOSE UPDATES)
    // ======================================
    const caregiverId = Number(localStorage.getItem("caregiver_id"));
    const helpRequestsCountEl = document.getElementById("helpRequestsCount");
    const doseUpdatesCountEl = document.getElementById("doseUpdatesCount");

    if (caregiverId && helpRequestsCountEl) {
        fetch(`${API_BASE}/api/help-requests/caregiver/${caregiverId}`)
            .then((res) => res.json())
            .then((data) => {
                if (Array.isArray(data)) {
                    helpRequestsCountEl.textContent = data.length;
                }
            })
            .catch((err) => console.error("Help request count error:", err));
    }

    if (caregiverId && doseUpdatesCountEl) {
        fetch(`${API_BASE}/api/dose-logs/caregiver/${caregiverId}`)
            .then((res) => res.json())
            .then((data) => {
                if (Array.isArray(data)) {
                    doseUpdatesCountEl.textContent = data.length;
                }
            })
            .catch((err) => console.error("Dose updates count error:", err));
    }

    // ======================================
    // 4. ADD MEDICATION FORM (patient medications page)
    // ======================================
    const medicationForm = document.getElementById("medicationForm");
    if (medicationForm) {
        const frequencySelect = document.getElementById("frequency");
        const timeContainer = document.getElementById("timeInputsContainer");

        if (frequencySelect && timeContainer) {
            frequencySelect.addEventListener("change", () => {
                let count = 1;
                if (frequencySelect.value === "Twice a day") count = 2;
                else if (frequencySelect.value === "Three times a day") count = 3;

                const labels = ["Dose 1", "Dose 2", "Dose 3"];
                timeContainer.innerHTML = "";

                for (let i = 0; i < count; i++) {
                    const wrapper = document.createElement("div");
                    wrapper.innerHTML = `
                        <small style="display:block; color:#555; margin-bottom:2px;">${count > 1 ? labels[i] : "Time"}</small>
                        <input type="time" class="med-time-input" required>
                    `;
                    timeContainer.appendChild(wrapper);
                }
            });
        }

        medicationForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const patientId = Number(localStorage.getItem("patient_id"));
            if (!patientId) {
                alert("Please log in as a patient before adding a medication.");
                return;
            }

            const reminderTimes = Array.from(document.querySelectorAll(".med-time-input"))
                .map((input) => input.value.trim())
                .filter(Boolean)
                .join(", ");

            const payload = {
                patient_id: patientId,
                medication_name: document.getElementById("medication-name")?.value.trim() || "",
                dosage: document.getElementById("dosage")?.value.trim() || "",
                frequency: document.getElementById("frequency")?.value.trim() || "",
                reminder_time: reminderTimes,
                start_date: document.getElementById("start-date")?.value.trim() || "",
                notes: document.getElementById("notes")?.value.trim() || ""
            };

            try {
                const res = await fetch(`${API_BASE}/api/medications`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    alert(data.message || data.error || "Could not add medication.");
                    return;
                }

                alert("Medication added successfully!");
                medicationForm.reset();

                if (timeContainer) {
                    timeContainer.innerHTML = `<input type="time" class="med-time-input" required>`;
                }

                if (typeof loadPatientMedications === "function") {
                    await loadPatientMedications();
                } else {
                    window.location.reload();
                }
            } catch (err) {
                console.error("Add medication error:", err);
                alert("Could not reach the server. Make sure Flask is running.");
            }
        });
    }

    // ======================================
    // 5. MEDICATION REMINDER NOTIFICATIONS (patient pages)
    // ======================================
    const loggedInRole = localStorage.getItem("role");
    const loggedInPatientId = Number(localStorage.getItem("patient_id"));

    if (loggedInRole === "patient" && loggedInPatientId) {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }

        function getHandledReminders() {
            return JSON.parse(localStorage.getItem("handledReminders") || "[]");
        }

        function markReminderHandled(key) {
            const list = getHandledReminders();
            if (!list.includes(key)) {
                list.push(key);
                localStorage.setItem("handledReminders", JSON.stringify(list));
            }
        }

        function getOrCreateReminderBanner() {
            let banner = document.getElementById("reminderBanner");
            if (!banner) {
                banner = document.createElement("div");
                banner.id = "reminderBanner";
                banner.style.cssText =
                    "display: none; background-color: #f3effa; border-left: 5px solid #6b4c9a; color: #2e1f47; padding: 14px 20px; margin: 16px auto; max-width: 1100px; border-radius: 6px; justify-content: space-between; align-items: center; gap: 12px;";
                banner.innerHTML = `
                    <span id="reminderMessage"></span>
                    <button type="button" id="reminderTakenBtn" class="btn">Mark Taken</button>
                `;
                const main = document.querySelector("main") || document.body;
                main.prepend(banner);
            }
            return banner;
        }

        const browserNotified = new Set();

        async function checkMedicationReminders() {
            try {
                const res = await fetch(`${API_BASE}/api/medications/${loggedInPatientId}`);
                const meds = await res.json();
                if (!res.ok || !Array.isArray(meds)) return;

                const now = new Date();
                const currentTime = now.toTimeString().slice(0, 5); // "HH:MM"
                const today = now.toISOString().split("T")[0];
                const handled = getHandledReminders();

                let dueMed = null;
                let dueTime = "";

                for (const med of meds) {
                    const times = (med.reminder_time || "")
                        .split(",")
                        .map((t) => t.trim().slice(0, 5))
                        .filter(Boolean);

                    for (const t of times) {
                        const key = `${med.med_id}-${today}-${t}`;
                        if (currentTime >= t && !handled.includes(key)) {
                            dueMed = med;
                            dueTime = t;
                            break;
                        }
                    }
                    if (dueMed) break;
                }

                const banner = getOrCreateReminderBanner();
                if (!dueMed) {
                    banner.style.display = "none";
                    return;
                }

                const key = `${dueMed.med_id}-${today}-${dueTime}`;
                const msg = document.getElementById("reminderMessage");
                const btn = document.getElementById("reminderTakenBtn");

                msg.innerHTML = `<strong>Medication Reminder (${dueTime}):</strong> Time to take ${dueMed.medication_name} (${dueMed.strength || dueMed.dosage || ""}).`;
                banner.style.display = "flex";

                // Trigger browser popup once per dose time per session
                if ("Notification" in window && Notification.permission === "granted" && !browserNotified.has(key)) {
                    new Notification("Medication Reminder", {
                        body: `Time to take ${dueMed.medication_name} (${dueMed.strength || dueMed.dosage || ""}) — ${dueTime}.`
                    });
                    browserNotified.add(key);
                }

                btn.onclick = async () => {
                    btn.disabled = true;
                    btn.textContent = "Saving...";
                    try {
                        const logRes = await fetch(`${API_BASE}/api/dose-logs`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                schedule_id: dueMed.schedule_id || null,
                                med_id: dueMed.med_id,
                                dose_date: today,
                                status: "taken"
                            })
                        });
                        if (logRes.ok) {
                            markReminderHandled(key);
                            banner.style.display = "none";
                            if (typeof loadPatientMedications === "function") {
                                loadPatientMedications();
                            }
                            checkMedicationReminders();
                        }
                    } catch (err) {
                        console.error("Reminder dose log error:", err);
                    } finally {
                        btn.disabled = false;
                        btn.textContent = "Mark Taken";
                    }
                };
            } catch (err) {
                console.error("Reminder check error:", err);
            }
        }

        checkMedicationReminders();
        setInterval(checkMedicationReminders, 60000);
    }

    // ======================================
    // 6. CAREGIVER MISSED-DOSE ALERTS (caregiver pages)
    // ======================================
    if (loggedInRole === "caregiver" && caregiverId) {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }

        function getOrCreateCaregiverAlertBanner() {
            let banner = document.getElementById("caregiverAlertBanner");
            if (!banner) {
                banner = document.createElement("div");
                banner.id = "caregiverAlertBanner";
                banner.style.cssText =
                    "display: none; background-color: #fdf2f2; border-left: 5px solid #c0392b; color: #5c1a1b; padding: 14px 20px; margin: 16px auto; max-width: 1100px; border-radius: 6px; justify-content: space-between; align-items: center; gap: 12px;";
                banner.innerHTML = `
                    <div id="caregiverAlertMessage"></div>
                    <button type="button" id="dismissCaregiverAlert" class="btn" style="background-color: #c0392b;">Dismiss</button>
                `;
                const main = document.querySelector("main") || document.body;
                main.prepend(banner);

                document.getElementById("dismissCaregiverAlert").addEventListener("click", () => {
                    banner.style.display = "none";
                });
            }
            return banner;
        }

        let lastAlertSignature = "";

        async function checkCaregiverMissedDoses() {
            try {
                const res = await fetch(`${API_BASE}/api/caregiver/${caregiverId}/missed-doses`);
                const alerts = await res.json();
                if (!res.ok || !Array.isArray(alerts)) return;

                const banner = getOrCreateCaregiverAlertBanner();
                if (alerts.length === 0) {
                    banner.style.display = "none";
                    return;
                }

                const signature = JSON.stringify(alerts);
                const msg = document.getElementById("caregiverAlertMessage");
                const itemsHtml = alerts
                    .map((a) => `<li><strong>${a.patient_name}</strong> — ${a.medication_name} ${a.strength} (${a.time}) <em>[${a.reason}]</em></li>`)
                    .join("");

                msg.innerHTML = `
                    <strong>Missed Dose Alert (${alerts.length}):</strong>
                    <ul style="margin: 6px 0 0 18px; padding: 0;">${itemsHtml}</ul>
                `;
                banner.style.display = "flex";

                if ("Notification" in window && Notification.permission === "granted" && signature !== lastAlertSignature) {
                    new Notification("Caregiver Missed Dose Alert", {
                        body: `${alerts[0].patient_name} has ${alerts.length} missed/overdue medication dose(s) today.`
                    });
                    lastAlertSignature = signature;
                }
            } catch (err) {
                console.error("Caregiver missed-dose check error:", err);
            }
        }

        checkCaregiverMissedDoses();
        setInterval(checkCaregiverMissedDoses, 60000);
    }
});