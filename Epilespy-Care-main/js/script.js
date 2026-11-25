// ======================================
// EPILEPSY CARE SYSTEM
// Main JavaScript File
// ======================================
console.log("Epilepsy Care JavaScript is connected successfully!");

// CAREGIVER LOGIN FORM VALIDATION

const caregiverLoginForm = document.getElementById("caregiverLoginForm");

if (caregiverLoginForm) {

    caregiverLoginForm.addEventListener("submit", function(event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (email === "" || password === "") {
            alert("Please fill in all the required fields.");
            return;
        }

        if (!caregiverLoginForm.checkValidity()) {
            caregiverLoginForm.reportValidity();
            return;
        }

       window.location.href = "caregiver.html";

    });

}

// PATIENT LOGIN FORM VALIDATION

const patientLoginForm = document.getElementById("patientLoginForm");

if (patientLoginForm) {

    patientLoginForm.addEventListener("submit", function(event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (email === "" || password === "") {
            alert("Please fill in all the required fields.");
            return;
        }

        if (!patientLoginForm.checkValidity()) {
            patientLoginForm.reportValidity();
            return;
        }

       window.location.href = "patient.html";
    });

}


// DOCTOR LOGIN FORM VALIDATION

const doctorLoginForm = document.getElementById("doctorLoginForm");

if (doctorLoginForm) {

    doctorLoginForm.addEventListener("submit", function(event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (email === "" || password === "") {
            alert("Please fill in all the required fields.");
            return;
        }

        if (!doctorLoginForm.checkValidity()) {
            doctorLoginForm.reportValidity();
            return;
        }

         window.location.href = "doctor.html";

    });

}

// ======================================
// ADMINISTRATOR LOGIN FORM VALIDATION
// ======================================
async function loginAdmin(email, password) {
    // send the email and password to the backend
    const response = await fetch("http://127.0.0.1:5000/api/login/admin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
    });

    // read the answer the backend sent back
    const result = await response.json();

    if (response.ok) {
        alert("Welcome " + result.full_name);
        window.location.href = "admin.html";
    } else {
        alert(result.message);
    }
}
