USE college_c;

UPDATE C_STUDENT
SET Snm = CONCAT(
    ELT(((CAST(RIGHT(Sno, 5) AS UNSIGNED) - 1) % 10) + 1, '苏', '林', '陈', '赵', '李', '王', '刘', '张', '吴', '郑'),
    ELT(FLOOR((CAST(RIGHT(Sno, 5) AS UNSIGNED) - 1) / 10) + 1, '知夏', '青岚', '慕白', '念初', '云舟')
);

SELECT Sno, Snm
FROM C_STUDENT
ORDER BY Sno
LIMIT 5;
