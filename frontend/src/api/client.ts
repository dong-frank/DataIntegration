import type {
  ApiResponse,
  CollegeCode,
  CourseRecord,
  EnrollmentRecord,
  LoginResponse,
  StatsSummary,
  StudentRecord,
} from '../types/domain';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`);
  }

  const payload = (await response.json()) as ApiResponse<T>;
  if (!payload.success) {
    throw new Error(payload.message);
  }
  return payload.data;
}

export const api = {
  login(username: string, password: string): Promise<LoginResponse> {
    return request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },
  students(college: CollegeCode): Promise<StudentRecord[]> {
    return request<StudentRecord[]>(`/college/${college}/students`);
  },
  courses(college: CollegeCode): Promise<CourseRecord[]> {
    return request<CourseRecord[]>(`/college/${college}/courses`);
  },
  enrollments(college: CollegeCode): Promise<EnrollmentRecord[]> {
    return request<EnrollmentRecord[]>(`/college/${college}/enrollments`);
  },
  sharedCourses(source?: CollegeCode): Promise<CourseRecord[]> {
    const query = source ? `?source=${source}` : '';
    return request<CourseRecord[]>(`/integration/shared-courses${query}`);
  },
  stats(): Promise<StatsSummary> {
    return request<StatsSummary>('/integration/stats');
  },
  withdraw(enrollmentId: string) {
    return request<{ enrollmentId: string; withdrawn: boolean; courseCollege: CollegeCode | null }>(
      `/integration/enrollments/${enrollmentId}`,
      { method: 'DELETE' },
    );
  },
};
