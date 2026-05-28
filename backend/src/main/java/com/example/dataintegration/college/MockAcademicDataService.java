package com.example.dataintegration.college;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import com.example.dataintegration.integration.CourseOverlap;
import com.example.dataintegration.integration.DuplicateEnrollmentException;
import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.example.dataintegration.integration.StatsSummary;
import com.example.dataintegration.integration.WithdrawalResult;

import org.springframework.stereotype.Service;

@Service
public class MockAcademicDataService implements AcademicDataService {

    private static final Map<CollegeCode, String[]> COURSE_NAMES_BY_COLLEGE = Map.of(
        CollegeCode.A, new String[] {
            "算法设计", "软件工程实践", "网络空间安全", "智能系统导论", "云计算基础",
            "人机交互", "离散数学", "工程英语", "嵌入式系统", "移动应用开发"
        },
        CollegeCode.B, new String[] {
            "商业数据分析", "数字经济导论", "市场营销", "创新创业管理", "供应链管理",
            "会计信息化", "微观经济学", "商务英语", "组织行为学", "金融科技"
        },
        CollegeCode.C, new String[] {
            "新媒体传播", "数字内容设计", "用户研究方法", "文化数据分析", "公共表达训练",
            "视觉传达基础", "新闻写作", "影视剪辑", "品牌策划", "交互设计"
        }
    );

    private static final Map<CollegeCode, String[]> STUDENT_SURNAMES_BY_COLLEGE = Map.of(
        CollegeCode.A, new String[] {"林", "陈", "赵", "周", "吴", "郑", "王", "李", "张", "刘"},
        CollegeCode.B, new String[] {"周", "林", "陈", "赵", "李", "王", "刘", "张", "吴", "郑"},
        CollegeCode.C, new String[] {"苏", "林", "陈", "赵", "李", "王", "刘", "张", "吴", "郑"}
    );

    private static final Map<CollegeCode, String[]> STUDENT_GIVEN_NAMES_BY_COLLEGE = Map.of(
        CollegeCode.A, new String[] {"安然", "子昂", "明轩", "清越", "星河"},
        CollegeCode.B, new String[] {"景文", "若帆", "嘉仪", "思衡", "明达"},
        CollegeCode.C, new String[] {"知夏", "青岚", "慕白", "念初", "云舟"}
    );

    private final Map<CollegeCode, List<StudentRecord>> students = new EnumMap<>(CollegeCode.class);
    private final Map<CollegeCode, List<CourseRecord>> courses = new EnumMap<>(CollegeCode.class);
    private final Map<CollegeCode, List<EnrollmentRecord>> enrollments = new EnumMap<>(CollegeCode.class);

    public MockAcademicDataService() {
        seed();
    }

    @Override
    public List<StudentRecord> students(CollegeCode college) {
        return Collections.unmodifiableList(students.getOrDefault(college, List.of()));
    }

    @Override
    public List<CourseRecord> courses(CollegeCode college) {
        return Collections.unmodifiableList(courses.getOrDefault(college, List.of()));
    }

    @Override
    public List<EnrollmentRecord> enrollments(CollegeCode college) {
        return Collections.unmodifiableList(enrollments.getOrDefault(college, List.of()));
    }

    @Override
    public List<CourseRecord> sharedCourses(Optional<CollegeCode> source) {
        return source
            .map(this::courses)
            .orElseGet(() -> courses.values().stream().flatMap(List::stream).toList())
            .stream()
            .filter(CourseRecord::shared)
            .sorted(Comparator.comparing(CourseRecord::college).thenComparing(CourseRecord::id))
            .toList();
    }

    @Override
    public EnrollmentRecord createEnrollment(EnrollmentCreateRequest request) {
        List<EnrollmentRecord> target = enrollments.computeIfAbsent(request.courseCollege(), key -> new ArrayList<>());
        assertEnrollmentNotExists(request, target);
        String id = "%s-X%04d".formatted(request.courseCollege(), target.size() + 1);
        EnrollmentRecord record = new EnrollmentRecord(
            id,
            request.studentCollege(),
            request.studentId(),
            request.courseCollege(),
            request.courseId(),
            LocalDate.now(),
            "ACTIVE",
            "0"
        );
        target.add(record);
        return record;
    }

    @Override
    public WithdrawalResult withdraw(String enrollmentId) {
        for (Map.Entry<CollegeCode, List<EnrollmentRecord>> entry : enrollments.entrySet()) {
            List<EnrollmentRecord> records = entry.getValue();
            for (int index = 0; index < records.size(); index++) {
                EnrollmentRecord record = records.get(index);
                if (!record.id().equals(enrollmentId)) {
                    continue;
                }
                records.set(index, new EnrollmentRecord(
                    record.id(),
                    record.studentCollege(),
                    record.studentId(),
                    record.courseCollege(),
                    record.courseId(),
                    record.enrolledAt(),
                    "WITHDRAWN",
                    record.score()
                ));
                return new WithdrawalResult(enrollmentId, true, entry.getKey());
            }
        }
        return new WithdrawalResult(enrollmentId, false, null);
    }

    @Override
    public StatsSummary stats() {
        List<StatsSummary.CollegeStat> collegeStats = List.of(CollegeCode.values()).stream()
            .map(college -> new StatsSummary.CollegeStat(
                college,
                college.getDisplayName(),
                students(college).size(),
                courses(college).size(),
                enrollments(college).size(),
                college.getDbms()
            ))
            .toList();

        Map<String, Long> courseNameCounts = courses.values().stream()
            .flatMap(List::stream)
            .collect(Collectors.groupingBy(CourseRecord::name, LinkedHashMap::new, Collectors.counting()));

        List<CourseOverlap> overlaps = courseNameCounts.entrySet().stream()
            .filter(entry -> entry.getValue() > 1)
            .map(entry -> new CourseOverlap(entry.getKey(), entry.getValue().intValue()))
            .toList();

        return new StatsSummary(
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::studentCount).sum(),
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::courseCount).sum(),
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::enrollmentCount).sum(),
            collegeStats,
            overlaps
        );
    }

    private void seed() {
        for (CollegeCode college : CollegeCode.values()) {
            List<StudentRecord> collegeStudents = new ArrayList<>();
            List<CourseRecord> collegeCourses = new ArrayList<>();
            List<EnrollmentRecord> collegeEnrollments = new ArrayList<>();

            for (int i = 1; i <= 50; i++) {
                collegeStudents.add(new StudentRecord(
                    "%s-S%03d".formatted(college, i),
                    college,
                    studentName(college, i),
                    i % 2 == 0 ? "女" : "男",
                    "%s教学管理".formatted(college.getDisplayName()),
                    2022 + (i % 3)
                ));
            }

            for (int i = 1; i <= 10; i++) {
                collegeCourses.add(new CourseRecord(
                    "%s-C%03d".formatted(college, i),
                    college,
                    COURSE_NAMES_BY_COLLEGE.get(college)[i - 1],
                    (int) ((2.0 + (i % 3)) * 16),
                    2.0 + (i % 3),
                    "%s教师%02d".formatted(college.getDisplayName(), i),
                    "%s教学楼%03d".formatted(college.getDisplayName(), 100 + i),
                    i <= 6
                ));
            }

            int enrollmentCounter = 1;
            for (int studentIndex = 0; studentIndex < collegeStudents.size(); studentIndex++) {
                StudentRecord student = collegeStudents.get(studentIndex);
                for (int j = 0; j < 5; j++) {
                    CourseRecord course = collegeCourses.get((studentIndex + j) % collegeCourses.size());
                    collegeEnrollments.add(new EnrollmentRecord(
                        "%s-E%04d".formatted(college, enrollmentCounter++),
                        college,
                        student.id(),
                        college,
                        course.id(),
                        LocalDate.of(2026, 3, 1).plusDays(j),
                        "ACTIVE",
                        Integer.toString(70 + ((studentIndex + j) % 26))
                    ));
                }
            }

            students.put(college, collegeStudents);
            courses.put(college, collegeCourses);
            enrollments.put(college, collegeEnrollments);
        }
    }

    private String studentName(CollegeCode college, int sequence) {
        String[] surnames = STUDENT_SURNAMES_BY_COLLEGE.get(college);
        String[] givenNames = STUDENT_GIVEN_NAMES_BY_COLLEGE.get(college);
        int nameIndex = sequence - 1;
        return surnames[nameIndex % surnames.length] + givenNames[nameIndex / surnames.length];
    }

    private void assertEnrollmentNotExists(EnrollmentCreateRequest request, List<EnrollmentRecord> target) {
        boolean exists = target.stream().anyMatch(record ->
            record.studentCollege() == request.studentCollege()
                && record.studentId().equals(request.studentId())
                && record.courseCollege() == request.courseCollege()
                && record.courseId().equals(request.courseId())
                && "ACTIVE".equals(record.status())
        );
        if (exists) {
            throw new DuplicateEnrollmentException(
                request.studentCollege(),
                request.studentId(),
                request.courseCollege(),
                request.courseId()
            );
        }
    }
}
