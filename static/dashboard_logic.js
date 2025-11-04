document.addEventListener("DOMContentLoaded", () => {
    const classCards = document.querySelectorAll(".class-card");
    const subjectsContainer = document.getElementById("subjects-container");
    const attendanceContainer = document.getElementById("attendance-marker-container");

    let selectedSubject = null;

    // --- Handles clicking on a class year (F.Y., S.Y., etc.) ---
    classCards.forEach((card) => {
        card.addEventListener("click", (event) => {
            event.preventDefault();
            const classYear = card.dataset.year;

            fetch(`/api/teacher_subjects/${classYear}`)
                .then((response) => response.json())
                .then((subjects) => {
                    let subjectLinksHTML = "";
                    if (subjects && subjects.length > 0) {
                        subjectLinksHTML = subjects
                            .map(
                                (subject) =>
                                    `<a href="#" class="subject-link" data-subject-name="${subject.subject_name}">${subject.subject_name}</a>`
                            )
                            .join("");
                    } else {
                        subjectLinksHTML = "<p>You have no subjects for this class year.</p>";
                    }

                    subjectsContainer.innerHTML = `
                        <h3>Subjects for ${classYear}.</h3>
                        <div class="subjects-list">${subjectLinksHTML}</div>`;
                    subjectsContainer.classList.remove("hidden");
                    attendanceContainer.classList.add("hidden");
                });
        });
    });

    // --- Handles clicking on a subject ---
    subjectsContainer.addEventListener("click", (event) => {
        const target = event.target.closest(".subject-link");
        if (!target) return;
        event.preventDefault();
        selectedSubject = target.dataset.subjectName;
        displayAttendanceOptions(selectedSubject);
    });

    // --- Display Attendance Options ---
    // --- Display Attendance Options ---
const displayAttendanceOptions = (subjectName) => {
    attendanceContainer.classList.remove("hidden");

    // Show the three options as cards
    attendanceContainer.querySelector("#wifi-scan-btn").style.display = "none"; // hide button initially
    attendanceContainer.querySelector("#wifi-scan-results").innerHTML = ""; // clear previous results

    attendanceContainer.innerHTML = `
        <h3>Attendance for ${subjectName}</h3>
        <div class="attendance-method-options">
            <div class="attendance-card" data-method="wifi">📶<br>Wi-Fi Scan</div>
            <div class="attendance-card" data-method="face">😊<br>Face Scan</div>
            <div class="attendance-card" data-method="final">📋<br>Final Attendance</div>
        </div>
        <button id="wifi-scan-btn" style="display:none;">Start Lecture (Wi-Fi Scan)</button>
        <div id="wifi-scan-results"></div>
    `;

    // Attach click listeners to the cards
    const cards = attendanceContainer.querySelectorAll(".attendance-card");
    const wifiButton = attendanceContainer.querySelector("#wifi-scan-btn");
    const wifiResults = attendanceContainer.querySelector("#wifi-scan-results");

    cards.forEach((card) => {
        card.addEventListener("click", () => {
            const method = card.dataset.method;

            if (method === "wifi") {
                wifiButton.style.display = "block"; // show button
                wifiButton.onclick = () => startWifiScanning(subjectName, wifiResults); // pass results div
            } else if (method === "face") {
                alert("Face Scan selected for " + subjectName);
            } else if (method === "final") {
                alert("Final Attendance selected for " + subjectName);
            }
        });
    });
};

// --- Wi-Fi Scanning Function ---
async function startWifiScanning(subjectName, wifiResults) {
    wifiResults.innerHTML = "⏳ Scanning Wi-Fi network... please wait...";

    try {
        const timetableRes = await fetch(`/api/get-timetable-id/${subjectName}`);
        const { timetable_id } = await timetableRes.json();

        const res = await fetch(`/api/scan_wifi/${timetable_id}`);
        const data = await res.json();

        if (data.status === "ok") {
            wifiResults.innerHTML = `
                <h4>✅ Wi-Fi Scan Completed</h4>
                <h5>Present Students (${data.present.length}):</h5>
                <ul>${data.present.map((n) => `<li>${n}</li>`).join("")}</ul>
                <h5>❌ Absent Students (${data.absent.length}):</h5>
                <ul>${data.absent.map((n) => `<li>${n}</li>`).join("")}</ul>
            `;
        } else {
            wifiResults.innerHTML = `<p style="color:red;">⚠️ Scan failed: ${data.error || "Unknown error"}</p>`;
        }
    } catch (err) {
        console.error(err);
        wifiResults.innerHTML = `<p style="color:red;">❌ Error during Wi-Fi scan. Check console.</p>`;
    }
}

});
