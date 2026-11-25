
// ADMINISTRATOR LOGIN FORM VALIDATION
const API_BASE = "http://127.0.0.1:5000";
async function loginAdmin(email, password) {
    try {
        // 1. Send email and password to Flask as JSON
        const response = await fetch(`${API_BASE}/api`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password })
        });

        // 2. Read the JSON reply Flask sent back
        const result = await response.json();

        // 3. Redirect on success (200), or show Flask's error (401 / 403)
        if (response.ok) {
            localStorage.setItem("admin_id", result.admin_id);
            localStorage.setItem("admin_name", result.full_name);
            alert("Welcome " + result.full_name);
            window.location.href = "admin.html";
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Could not connect to the backend. Check that python app.py is running.");
    }
}

const adminLoginForm = document.getElementById("adminLoginForm");

if (adminLoginForm) {
    adminLoginForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Stops the browser from reloading the page

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (email === "" || password === "") {
            alert("Please fill in all the required fields.");
            return;
        }

        loginAdmin(email, password);
    });
}

// ======================================
// USER REGISTRATION (PATIENT / CAREGIVER / DOCTOR)
// ======================================
const registerForm = document.getElementById("registerForm");

if (registerForm) {
    const roleSelect = document.getElementById("role");
    const phoneGroup = document.getElementById("phoneGroup");
    const doctorFields = document.getElementById("doctorFields");
    const registrationNoInput = document.getElementById("registrationNo");

    // Show/hide extra fields depending on the selected role
    roleSelect.addEventListener("change", function() {
        const isDoctor = roleSelect.value === "doctor";
        doctorFields.style.display = isDoctor ? "block" : "none";
        phoneGroup.style.display = isDoctor ? "none" : "block";
        registrationNoInput.required = isDoctor;
    });

    registerForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const role = roleSelect.value;
        const payload = {
            role: role,
            full_name: document.getElementById("fullName").value.trim(),
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value,
            phone: document.getElementById("phone").value.trim(),
            registration_no: registrationNoInput.value.trim(),
            facility: document.getElementById("facility").value.trim()
        };

        try {
            const response = await fetch(`${API_BASE}/api/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                window.location.href = `${role}/login.html`;
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Registration error:", error);
            alert("Could not connect to the backend. Check that python app.py is running.");
        }
    });
}
// ======================================
// PATIENT MEDICATION MANAGEMENT
// ======================================
const medicationForm = document.getElementById("medicationForm");
const medicationTableBody = document.getElementById("medicationTableBody");

async function loadMedications() {
    if (!medicationTableBody) return;

    const patientId = localStorage.getItem("patient_id");
    if (!patientId) {
        medicationTableBody.innerHTML =
            '<tr><td colspan="5" class="empty-message">Please log in as a patient first.</td></tr>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/medications/${patientId}`);
        const meds = await response.json();

        if (meds.length === 0) {
            medicationTableBody.innerHTML =
                '<tr><td colspan="5" class="empty-message">No medication has been added yet.</td></tr>';
            return;
        }

        medicationTableBody.innerHTML = meds.map(med => `
            <tr>
                <td><strong>${med.medication_name}</strong></td>
                <td>${med.strength || "-"}</td>
                <td>${med.frequency || "-"}</td>
                <td>${med.reminder_time || "-"}</td>
                <td><span class="badge badge-success">Active</span></td>
            </tr>
        `).join("");
    } catch (error) {
        console.error("Load medications error:", error);
        medicationTableBody.innerHTML =
            '<tr><td colspan="5" class="empty-message">Could not load medications from backend.</td></tr>';
    }
}

if (medicationForm) {
    loadMedications();

    medicationForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const patientId = localStorage.getItem("patient_id");
        if (!patientId) {
            alert("Please log in as a patient first.");
            window.location.href = "login.html";
            return;
        }

        const payload = {
            patient_id: Number(patientId),
            medication_name: document.getElementById("medication-name").value.trim(),
            dosage: document.getElementById("dosage").value.trim(),
            frequency: document.getElementById("frequency").value,
            reminder_time: document.getElementById("time").value,
            start_date: document.getElementById("start-date").value,
            notes: document.getElementById("notes").value.trim()
        };

        try {
            const response = await fetch(`${API_BASE}/api/medications`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                medicationForm.reset();
                loadMedications(); // Refresh table immediately from MySQL
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Add medication error:", error);
            alert("Could not connect to the backend.");
        }
    });
}

// ======================================
// PATIENT HEALTH RECORDS (SEIZURES & SYMPTOMS)
// ======================================
const healthRecordForm = document.getElementById("healthRecordForm");
const healthRecordsTableBody = document.getElementById("healthRecordsTableBody");

async function loadHealthRecords() {
    if (!healthRecordsTableBody) return;

    const patientId = localStorage.getItem("patient_id");
    if (!patientId) {
        healthRecordsTableBody.innerHTML =
            '<tr><td colspan="4" class="empty-message">Please log in as a patient first.</td></tr>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/health-records/${patientId}`);
        const records = await response.json();

        if (records.length === 0) {
            healthRecordsTableBody.innerHTML =
                '<tr><td colspan="4" class="empty-message">No health records have been added yet.</td></tr>';
            return;
        }

        healthRecordsTableBody.innerHTML = records.map(rec => `
            <tr>
                <td>${rec.record_date}</td>
                <td>
                    <span class="badge ${rec.had_seizure ? "badge-danger" : "badge-success"}">
                        ${rec.seizure_occurrence}
                    </span>
                </td>
                <td>${rec.symptoms}</td>
                <td>${rec.observations}</td>
            </tr>
        `).join("");
    } catch (error) {
        console.error("Load health records error:", error);
        healthRecordsTableBody.innerHTML =
            '<tr><td colspan="4" class="empty-message">Could not load health records from backend.</td></tr>';
    }
}

if (healthRecordForm) {
    loadHealthRecords();

    healthRecordForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const patientId = localStorage.getItem("patient_id");
        if (!patientId) {
            alert("Please log in as a patient first.");
            window.location.href = "login.html";
            return;
        }

        const payload = {
            patient_id: Number(patientId),
            record_date: document.getElementById("record-date").value,
            seizure: document.getElementById("seizure").value,
            seizure_type: document.getElementById("seizure-type").value.trim(),
            duration_secs: document.getElementById("duration").value,
            symptoms: document.getElementById("symptoms").value.trim(),
            observations: document.getElementById("observations").value.trim()
        };

        try {
            const response = await fetch(`${API_BASE}/api/health-records`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                healthRecordForm.reset();
                loadHealthRecords(); // Refresh table immediately from MySQL
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Add health record error:", error);
            alert("Could not connect to the backend.");
        }
    });
}
// ======================================
// ADMIN: DOCTOR APPLICATIONS APPROVAL
// ======================================
const doctorApplicationsBody = document.getElementById("doctorApplicationsBody");

function getStatusBadgeClass(status) {
    if (status === "approved") return "badge-success";
    if (status === "rejected") return "badge-danger";
    return "badge-warning";
}

async function loadDoctorApplications() {
    if (!doctorApplicationsBody) return;

    const adminId = localStorage.getItem("admin_id");
    if (!adminId) {
        doctorApplicationsBody.innerHTML =
            '<tr><td colspan="6" class="empty-message">Please log in as an administrator first.</td></tr>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/admin/doctors`);
        const doctors = await response.json();

        if (doctors.length === 0) {
            doctorApplicationsBody.innerHTML =
                '<tr><td colspan="6" class="empty-message">No doctor applications found.</td></tr>';
            return;
        }

        doctorApplicationsBody.innerHTML = doctors.map(doc => {
            const status = (doc.approval_status || "pending").toLowerCase();
            const badgeClass = getStatusBadgeClass(status);
            const displayStatus = status.charAt(0).toUpperCase() + status.slice(1);

            return `
                <tr>
                    <td><strong>${doc.full_name}</strong></td>
                    <td>${doc.email}</td>
                    <td>${doc.registration_no || "-"}</td>
                    <td>${doc.facility || "-"}</td>
                    <td><span class="badge ${badgeClass}">${displayStatus}</span></td>
                    <td>
                        <div class="action-buttons">
                            ${status !== "approved"
                                ? `<button class="btn-sm btn-approve" onclick="updateDoctorStatus(${doc.doctor_id}, 'approved')">Approve</button>`
                                : ""}
                            ${status !== "rejected"
                                ? `<button class="btn-sm btn-reject" onclick="updateDoctorStatus(${doc.doctor_id}, 'rejected')">Reject</button>`
                                : ""}
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    } catch (error) {
        console.error("Load doctor applications error:", error);
        doctorApplicationsBody.innerHTML =
            '<tr><td colspan="6" class="empty-message">Could not load doctor applications from backend.</td></tr>';
    }
}

async function updateDoctorStatus(doctorId, newStatus) {
    try {
        const response = await fetch(`${API_BASE}/api/admin/doctors/${doctorId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ approval_status: newStatus })
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            loadDoctorApplications(); // Refresh table immediately from MySQL
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Update doctor status error:", error);
        alert("Could not connect to the backend.");
    }
}

if (doctorApplicationsBody) {
    loadDoctorApplications();
}