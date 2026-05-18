export type CollegeCode = 'A' | 'B' | 'C';

export type Role = 'COLLEGE' | 'INTEGRATION_ADMIN';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface LoginResponse {
  token: string;
  displayName: string;
  role: Role;
  college: CollegeCode | null;
}

export interface StudentRecord {
  id: string;
  college: CollegeCode;
  name: string;
  gender: string;
  major: string;
  grade: number;
}

export interface CourseRecord {
  id: string;
  college: CollegeCode;
  name: string;
  hours: number;
  credits: number;
  teacher: string;
  location: string;
  shared: boolean;
}

export interface EnrollmentRecord {
  id: string;
  studentCollege: CollegeCode;
  studentId: string;
  courseCollege: CollegeCode;
  courseId: string;
  enrolledAt: string;
  status: string;
  score: string;
}

export interface EnrollmentCreatePayload {
  studentCollege: CollegeCode;
  studentId: string;
  courseCollege: CollegeCode;
  courseId: string;
}

export interface WithdrawalResult {
  enrollmentId: string;
  withdrawn: boolean;
  courseCollege: CollegeCode | null;
}

export interface CollegeStat {
  college: CollegeCode;
  displayName: string;
  studentCount: number;
  courseCount: number;
  enrollmentCount: number;
  dbms: string;
}

export interface StatsSummary {
  totalStudents: number;
  totalCourses: number;
  totalEnrollments: number;
  colleges: CollegeStat[];
  overlappingCourses: Array<{
    courseName: string;
    collegeCount: number;
  }>;
}
