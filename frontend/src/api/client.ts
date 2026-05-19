import type {
  ApiResponse,
  CollegeCode,
  EnrollmentCreatePayload,
  CourseRecord,
  EnrollmentRecord,
  LoginResponse,
  StatsSummary,
  StudentRecord,
  WithdrawalResult,
} from '../types/domain';

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 12000;

async function errorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as Partial<ApiResponse<unknown>> & { error?: string };
    return payload.message || payload.error || `请求失败: ${response.status}`;
  } catch {
    return `请求失败: ${response.status}`;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
      signal: options.signal ?? controller.signal,
    });

    if (!response.ok) {
      throw new Error(await errorMessage(response));
    }

    const payload = (await response.json()) as ApiResponse<T>;
    if (!payload.success) {
      throw new Error(payload.message || '接口返回失败');
    }
    return payload.data;
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('请求超时，请确认后端服务已启动');
    }
    throw err;
  } finally {
    window.clearTimeout(timeout);
  }
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
  enroll(payload: EnrollmentCreatePayload): Promise<EnrollmentRecord> {
    return request<EnrollmentRecord>('/integration/enrollments', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  withdraw(enrollmentId: string): Promise<WithdrawalResult> {
    return request<WithdrawalResult>(
      `/integration/enrollments/${encodeURIComponent(enrollmentId)}`,
      { method: 'DELETE' },
    );
  },
};
