CREATE DATABASE attendify;
USE attendify;
CREATE TABLE students (student_id INT AUTO_INCREMENT PRIMARY KEY,roll_no VARCHAR(20) UNIQUE NOT NULL,name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,password VARCHAR(100) NOT NULL,mac_address VARCHAR(50) UNIQUE,face_image_path VARCHAR(255));

CREATE TABLE teachers (teacher_id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(100) NOT NULL,subject_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,password VARCHAR(255) NOT NULL);    

CREATE TABLE timetable (timetable_id INT AUTO_INCREMENT PRIMARY KEY,subject_name VARCHAR(100) NOT NULL,teacher_id INT,
    day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),start_time TIME NOT NULL,
    end_time TIME NOT NULL,FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id));

CREATE TABLE attendance (attendance_id INT AUTO_INCREMENT PRIMARY KEY,student_id INT NOT NULL,
    timetable_id INT NOT NULL,    date DATE NOT NULL,
    face_verified BOOLEAN DEFAULT NULL,wifi_verified BOOLEAN DEFAULT NULL,
    status ENUM('Present','Absent') DEFAULT 'Absent',FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (timetable_id) REFERENCES timetable(timetable_id),UNIQUE(student_id, timetable_id, date));

INSERT INTO students (roll_no, name, email, password, mac_address, face_image_path) VALUES
('10', 'Sanjivani Chewale', 'spchewale371123@kkwagh.edu.in','pass@123','b8:94:e7:24:cd:8d','/images/students/sanjivani.jpg'),
('14', 'Atharva Deshmukh','asdeshmukh371123@kkwagh.edu.in', 'pass@123','78:5E:CC:35:AA:09','/images/students/atharva.jpg'),
('15', 'Dhawal Deshmukh','dndeshmukh371123@kkwagh.edu.in', 'pass@123', 'e4:8c:73:b2:c1:a7','/images/students/dhawal.jpg'),
('18', 'Manasi Jadhav','mujadhav371123@kkwagh.edu.in', 'pass@123','44:16:FA:56:B9:34','/images/students/manasi.jpg'),
('22', 'Bhumi Kalantri','bkkalantri371123@kkwagh.edu.in', 'pass@123','14:9b:f3:2f:28:e9','/images/students/bhumi.jpg');

INSERT INTO teachers (name, subject_name, email, password) VALUES
('Prof. Pranali Shinde', 'DSA', 'pkshinde@kkwagh.edu.in', 'pass@123'),
('Prof. Deepali Shinkar', 'DSBD', 'dvshinkar@kkwagh.edu.in', 'pass@123'),
('Prof. Mahindra Shinde', 'COA', 'ms-shinde@kkwagh.edu.in', 'pass@123'),
('Prof. Arti Bairagi', 'IOT', 'asbairagi@kkwagh.edu.in', 'pass@123'),
('Prof. Priyadarshini', 'IOTL', 'ipriyadarshini@kkwagh.edu.in', 'pass@123'),
('Prof. Samruddhi Patil', 'MIS', 'st-1patil@kkwagh.edu.in', 'pass@123'),
('Prof. Kushal Birla', 'AI', 'kpbirla@kkwagh.edu.in', 'pass@123');

-- Monday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('DSA', 1, 'Monday', '08:10:00', '09:10:00'),
('DSBD',2, 'Monday', '09:10:00', '10:10:00'),
('COA', 3, 'Monday', '10:25:00', '11:20:00'),
('IOT', 4, 'Monday', '11:20:00', '12:15:00');

-- Tuesday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('DSBD', 2, 'Tuesday', '08:10:00', '09:10:00'),
('DSA',1, 'Tuesday', '09:10:00', '10:10:00'),
('IOT', 4, 'Tuesday', '10:25:00', '11:20:00'),
('COA', 3, 'Tuesday', '11:20:00', '12:15:00'),
('IOTL', 5, 'Tuesday', '13:05:00', '14:55:00');

-- Wednesday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('DSBD', 2, 'Wednesday', '08:10:00', '09:10:00'),
('DSA',1, 'Wednesday', '09:10:00', '10:10:00'),
('IOT', 4, 'Wednesday', '10:25:00', '11:20:00'),
('PBLT', 2, 'Wednesday', '11:20:00', '12:15:00'),
('PBL', 3, 'Wednesday', '13:05:00', '14:55:00');

-- Thursday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('DSBDL', 2, 'Thursday', '08:10:00', '10:10:00'),
('MIS', 6, 'Thursday', '10:25:00', '11:20:00'),
('AI', 7, 'Thursday', '11:20:00', '12:15:00');

-- Friday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('AI', 7, 'Friday', '10:25:00', '11:20:00'),
('COA', 3, 'Friday', '11:20:00', '12:15:00');

-- Saturday
INSERT INTO timetable (subject_name, teacher_id, day_of_week, start_time, end_time) VALUES
('DSAL', 1, 'Saturday', '08:10:00', '10:10:00'),
('MIS', 6, 'Saturday', '10:25:00', '11:20:00'),
('AI', 7, 'Saturday', '11:20:00', '12:15:00');

-- Monday’s class 

INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 1, CURDATE()),
(2, 1, CURDATE()),
(3, 1, CURDATE()),
(4, 1, CURDATE()),
(5, 1, CURDATE());

-- Tuesday 
INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 2, CURDATE()),
(2, 2, CURDATE()),
(3, 2, CURDATE()),
(4, 2, CURDATE()),
(5, 2, CURDATE());

-- Wednesday 
INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 3, CURDATE()),
(2, 3, CURDATE()),
(3, 3, CURDATE()),
(4, 3, CURDATE()),
(5, 3, CURDATE());

-- Thursday 
INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 4, CURDATE()),
(2, 4, CURDATE()),
(3, 4, CURDATE()),
(4, 4, CURDATE()),
(5, 4, CURDATE());

-- Friday 
INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 5, CURDATE()),
(2, 5, CURDATE()),
(3, 5, CURDATE()),
(4, 5, CURDATE()),
(5, 5, CURDATE());

-- Saturday 
INSERT INTO attendance (student_id, timetable_id, date)
VALUES
(1, 6, CURDATE()),
(2, 6, CURDATE()),
(3, 6, CURDATE()),
(4, 6, CURDATE()),
(5, 6, CURDATE());



DELIMITER $$

CREATE TRIGGER attendance_status_update
AFTER UPDATE ON attendance
FOR EACH ROW
BEGIN
    IF NEW.face_verified = TRUE AND NEW.wifi_verified = TRUE THEN
        UPDATE attendance
        SET status = 'Present'
        WHERE attendance_id = NEW.attendance_id;
    ELSE
        UPDATE attendance
        SET status = 'Absent'
        WHERE attendance_id = NEW.attendance_id;
    END IF;
END$$

DELIMITER ;
;

-- subject wise
SELECT 
    s.name AS Student,
    t.subject_name,
    COUNT(*) AS Total_Classes,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS Classes_Present,
    ROUND(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Attendance_Percentage
FROM 
    attendance a
JOIN 
    students s ON a.student_id = s.student_id
JOIN 
    timetable t ON a.timetable_id = t.timetable_id
GROUP BY 
    s.student_id, t.subject_name
ORDER BY 
    s.name, t.subject_name;

-- overall
SELECT 
    s.name AS Student,
    COUNT(*) AS Total_Classes,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS Classes_Present,
    ROUND(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Attendance_Percentage
FROM 
    attendance a
JOIN 
    students s ON a.student_id = s.student_id
GROUP BY 
    s.student_id, s.name;

-- daywise
SELECT 
    s.name AS Student,
    a.date,
    t.subject_name,
    a.status
FROM 
    attendance a
JOIN 
    students s ON a.student_id = s.student_id
JOIN
    timetable t ON a.timetable_id = t.timetable_id
ORDER BY 
    a.date, s.name, t.subject_name;
    
USE attendify; -- Select your database

-- Paste the command here to update the passwords
UPDATE students SET password = SHA2('pass@123', 256) WHERE student_id > 0;
UPDATE teachers SET password = SHA2('pass@123', 256) WHERE teacher_id > 0;

SET SQL_SAFE_UPDATES = 0;
ALTER TABLE timetable ADD COLUMN class_year VARCHAR(10) NOT NULL;
-- Assigning subjects to S.Y. (Second Year)
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'DSA';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'DSAL';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'COA';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'MIS';

-- Assigning subjects to T.Y. (Third Year)
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'DSBD';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'DSBDL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'IOT';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'IOTL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'PBL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'PBLT';

-- Assigning subjects to S.Y. (Second Year)
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'DSA';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'DSAL';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'COA';
UPDATE timetable SET class_year = 'S.Y.' WHERE subject_name = 'MIS';

-- Assigning subjects to T.Y. (Third Year)
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'DSBD';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'DSBDL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'IOT';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'IOTL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'PBL';
UPDATE timetable SET class_year = 'T.Y.' WHERE subject_name = 'PBLT';

-- Assigning subjects to B.TECH (Final Year)
UPDATE timetable SET class_year = 'B.TECH' WHERE subject_name = 'AI';