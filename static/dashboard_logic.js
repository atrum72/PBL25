document.addEventListener('DOMContentLoaded', () => {
    const classCards = document.querySelectorAll('.class-card');
    const subjectsContainer = document.getElementById('subjects-container');
    const attendanceContainer = document.getElementById('attendance-marker-container');

    // --- Handles clicking on a class year (F.Y., S.Y., etc.) ---
    classCards.forEach(card => {
        card.addEventListener('click', (event) => {
            event.preventDefault();
            const classYear = card.dataset.year;

            // Fetch subjects for the clicked year from the Python API
            fetch(`/api/teacher_subjects/${classYear}`)
                .then(response => response.json())
                .then(subjects => {
                    let subjectLinksHTML = '';
                    if (subjects && subjects.length > 0) {
                        subjectLinksHTML = subjects.map(subject => 
                            `<a href="#" class="subject-link" data-subject-name="${subject.subject_name}">${subject.subject_name}</a>`
                        ).join('');
                    } else {
                        subjectLinksHTML = '<p>You have no subjects for this class year.</p>';
                    }
                    
                    subjectsContainer.innerHTML = `<h3>Subjects for ${classYear}</h3><div class="subjects-list">${subjectLinksHTML}</div>`;
                    subjectsContainer.classList.remove('hidden');
                    attendanceContainer.classList.add('hidden');
                });
        });
    });

    // --- Handles clicking on a subject ---
    subjectsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('subject-link')) {
            event.preventDefault();
            const subjectName = event.target.dataset.subjectName;
            displayAttendanceOptions(subjectName);
        }
    });

    // --- Displays the three attendance options ---
    const displayAttendanceOptions = (subjectName) => {
        const optionsHTML = `
            <h3>Attendance for ${subjectName}</h3>
            <div class="attendance-method-options">
                <div class="attendance-card" data-method="wifi">
                    <div class="icon">📶</div><h4>Wi-Fi Scanning</h4><p>Scan the local network.</p>
                </div>
                <div class="attendance-card" data-method="face">
                    <div class="icon">😊</div><h4>Face Scanning</h4><p>Use camera for recognition.</p>
                </div>
                <div class="attendance-card" data-method="final">
                    <div class="icon">📋</div><h4>Final Attendance</h4><p>Review the final list.</p>
                </div>
            </div>`;
        attendanceContainer.innerHTML = optionsHTML;
        attendanceContainer.classList.remove('hidden');
    };
    
    // --- Handles clicking on Wi-Fi, Face, or Final Attendance ---
    attendanceContainer.addEventListener('click', (event) => {
        const card = event.target.closest('.attendance-card');
        if (card) {
            const method = card.dataset.method;
            alert(`Selected option: ${method.toUpperCase()}`);
        }
    });
});