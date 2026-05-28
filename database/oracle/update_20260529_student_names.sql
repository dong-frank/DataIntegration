MERGE INTO B_STUDENT student
USING (
    SELECT
        student_no,
        CASE MOD(sequence_no - 1, 10)
            WHEN 0 THEN '周'
            WHEN 1 THEN '林'
            WHEN 2 THEN '陈'
            WHEN 3 THEN '赵'
            WHEN 4 THEN '李'
            WHEN 5 THEN '王'
            WHEN 6 THEN '刘'
            WHEN 7 THEN '张'
            WHEN 8 THEN '吴'
            ELSE '郑'
        END ||
        CASE TRUNC((sequence_no - 1) / 10)
            WHEN 0 THEN '景文'
            WHEN 1 THEN '若帆'
            WHEN 2 THEN '嘉仪'
            WHEN 3 THEN '思衡'
            ELSE '明达'
        END AS student_name
    FROM (
        SELECT
            student_no,
            TO_NUMBER(SUBSTR(student_no, 5)) AS sequence_no
        FROM B_STUDENT
    )
) names
ON (student.student_no = names.student_no)
WHEN MATCHED THEN
    UPDATE SET student.student_name = names.student_name;

COMMIT;

SELECT student_no, student_name
FROM B_STUDENT
ORDER BY student_no
FETCH FIRST 5 ROWS ONLY;
