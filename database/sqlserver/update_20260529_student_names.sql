USE college_a;
GO

WITH numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 50
),
student_names AS (
    SELECT
        n,
        CONCAT(
            CHOOSE(((n - 1) % 10) + 1, N'林', N'陈', N'赵', N'周', N'吴', N'郑', N'王', N'李', N'张', N'刘'),
            CHOOSE(((n - 1) / 10) + 1, N'安然', N'子昂', N'明轩', N'清越', N'星河')
        ) AS student_name
    FROM numbers
)
UPDATE student
SET student.student_name = names.student_name
FROM dbo.A_STUDENT AS student
JOIN student_names AS names
    ON CAST(RIGHT(student.student_no, 8) AS INT) = names.n
OPTION (MAXRECURSION 50);
GO

SELECT TOP 5 student_no, student_name
FROM dbo.A_STUDENT
ORDER BY student_no;
GO
