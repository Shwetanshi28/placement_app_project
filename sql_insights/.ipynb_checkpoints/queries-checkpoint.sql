/*
1.) Average Programming Score per Course Batch
*/
SELECT course_batch, ROUND(AVG(P.latest_project_score),2) AS avg_programming_score
FROM Students AS S
JOIN Programming AS P ON S.student_id = P.student_id
GROUP BY course_batch;

/*
2.) Top 5 students ready for placement based on mock interview score
*/
SELECT s.full_name, pl.mock_interview_score, pl.placement_status
FROM Students AS s
JOIN Placements AS pl ON s.student_id = pl.student_id
WHERE pl.placement_status = 'Ready'
ORDER BY pl.mock_interview_score DESC
LIMIT 5

/*
3.) Distribution of average soft skill score
*/
SELECT 
    CASE
        WHEN avg_score>=85 THEN 'Excellent'
        WHEN avg_score>=70  THEN 'Good'
        WHEN avg_score>=50 THEN 'Average'
        ELSE 'Needs Improvement'
    END AS category,
    COUNT(*) AS student_count
FROM (
    SELECT
        (communication + teamwork + presentation + leadership + critical_thinking + interpersonal_skills) / 6 AS avg_score
    FROM Soft_skills
    ) AS derived
GROUP BY category;

/*
4.) Number of students that are placed/ready/not ready
*/
SELECT
placement_status, 
COUNT(*) AS student_count
FROM Placements
GROUP BY placement_status;

/*
5.)Top 5 cities with highest number of students
*/
SELECT city, COUNT(*) AS student_count
FROM students
GROUP BY city
ORDER BY student_count DESC
LIMIT 5

/*
6.)Average Mock Interview Score by Graduation Year
*/
SELECT s.graduation_year, ROUND(AVG(pl.mock_interview_score),2) AS avg_mock_score
FROM Students AS s
JOIN Placements AS pl ON s.student_id=pl.student_id
GROUP BY s.graduation_year
ORDER BY s.graduation_year

/*
7.)Most Commonly used programming language among students
*/
SELECT language, COUNT(*) AS student_count
FROM Programming
GROUP BY language
ORDER BY student_count DESC;

/*
8.)Students with 2 or more internships completed and placed
*/
SELECT s.full_name, pl.internships_completed, pl.placement_status
FROM Students AS s
JOIN Placements AS pl ON s.student_id = pl.student_id
WHERE pl.internships_completed>=2 and pl.placement_status='Placed';

/*
9.)Students who have cleared more than 3 interview rounds
*/
SELECT s.full_name, pl.interview_rounds_cleared
FROM Students AS s
JOIN Placements AS pl ON s.student_id = pl.student_id
WHERE pl.interview_rounds_cleared>=3
ORDER BY pl.interview_rounds_cleared DESC;

/*
10.)Students who earned more than 2 programming certifications
*/
SELECT s.full_name, p.certifications_earned
FROM Students AS s
JOIN Programming AS p ON s.student_id = p.student_id
WHERE p.certifications_earned>=2
ORDER BY p.certifications_earned DESC;





















