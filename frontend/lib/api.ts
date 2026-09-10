const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface HealthResponse {
  status: string;
  service: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  access_role: "employee" | "admin";
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CompetencyItem {
  competency_id: string;
  competency_name: string;
  domain: string;
  current_level: number;
  current_level_label: string;
  required_level: number;
  required_level_label: string;
  gap: number;
  is_critical: boolean;
  organizational_priority: number;
  priority_score: number;
}

export interface RecommendationItem {
  recommendation_id?: string;
  course_id: string;
  course_title: string;
  provider: string;
  source?: string;
  url?: string;
  duration_minutes?: number;
  course_level?: string;
  competency_id: string;
  competency_name: string;
  current_level: number;
  required_level: number;
  course_target_level: number;
  gap_score: number;
  priority_score: number;
  is_critical?: boolean;
  organizational_priority?: number;
  reason?: string;
  status?: string;
}

export interface EmployeeDashboardData {
  employee: {
    user_id: string;
    email: string;
    role_id: string;
    role_name: string;
  };
  summary: {
    total_competencies: number;
    competencies_with_gaps: number;
    mastered_competencies: number;
    total_recommendations: number;
  };
  competencies: CompetencyItem[];
  priority_gaps: CompetencyItem[];
  recommendations: RecommendationItem[];
}

export interface AdminDashboardData {
  workforce_summary: {
    total_employees: number;
    total_departments: number;
    total_roles: number;
    departments: Record<string, number>;
    roles: Record<string, number>;
  };
  gap_analytics: {
    total_gaps_count: number;
    critical_gaps_count: number;
    average_gap: number;
    top_deficits: Array<{
      competency_id: string;
      competency_name: string;
      domain: string;
      affected_employees: number;
      total_gap: number;
      total_priority: number;
      is_critical: boolean;
    }>;
  };
  proficiency_distribution: Record<string, number>;
  domain_health: Array<{
    domain: string;
    average_level: number;
    label: string;
    evaluated_count: number;
  }>;
  training_effectiveness: {
    total_assessments: number;
    completed_assessments: number;
    reassessments_taken: number;
    average_score: number;
    competency_upgrades: number;
  };
  content_and_ai: {
    learning_materials: number;
    ai_questions: {
      total: number;
      pending: number;
      approved: number;
      rejected: number;
    };
  };
}

export interface QuizQuestion {
  id: string;
  competency_id?: string;
  question_text: string;
  question_type: string;
  difficulty: string;
  options: Record<string, string>;
  correct_answer?: string; // only present in mock/demo data for offline evaluation
}

export interface StartAssessmentResponse {
  message: string;
  assessment_id: string;
  assessment_type: string;
  status: string;
  total_questions: number;
  questions: QuizQuestion[];
}

export interface FinishAssessmentResponse {
  message: string;
  assessment_id: string;
  assessment_type: string;
  status: string;
  total_questions: number;
  total_answered: number;
  unanswered: number;
  correct_answers: number;
  score: number;
}

export interface ScoreAssessmentResponse {
  message: string;
  assessment_id: string;
  total_questions: number;
  correct_answers: number;
  accuracy: number;
  overall_score: number;
  competency_updates: Array<{
    competency_id: string;
    competency_name: string;
    previous_level: number;
    evidence_level: number;
    updated_level: number;
    previous_gap: number;
    new_gap: number;
  }>;
  refreshed_recommendations_count?: number;
}

export interface LearningMaterial {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface ContentChunkItem {
  id: string;
  chunk_index: number;
  chunk_text: string;
  has_embedding: boolean;
  text_length: number;
}

export interface AIGeneratedQuestionItem {
  id: string;
  learning_content_id: string;
  competency_id: string | null;
  question_text: string;
  question_type: string;
  difficulty: string;
  options: Record<string, string>;
  correct_answer: string;
  explanation: string;
  source_chunk_ids: string[];
  generation_model: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  updated_at: string;
}

import {
  MOCK_DASHBOARD,
  MOCK_ADMIN_DASHBOARD,
  MOCK_ASSESSMENT,
  MOCK_SCORE_RESULT,
  MOCK_LEARNING_CONTENT,
  MOCK_AI_QUESTIONS,
} from "./mockData";

function getDemoFallback<T>(endpoint: string, options: RequestInit = {}, token?: string): T | undefined {
  if (endpoint.includes("/health")) {
    return { status: "ok", service: "Skill Intelligence Platform (Demo)" } as unknown as T;
  }
  if (endpoint.includes("/api/auth/login")) {
    let isAdmin = false;
    try {
      if (typeof options.body === "string" && (options.body.includes("rohit") || options.body.includes("admin"))) {
        isAdmin = true;
      }
    } catch {}
    return {
      access_token: isAdmin ? "demo-token-admin" : "demo-token-employee",
      token_type: "bearer",
    } as unknown as T;
  }
  if (endpoint.includes("/api/auth/me")) {
    const isAdmin = token?.includes("admin");
    if (isAdmin) {
      return {
        id: "user-rohit",
        email: "rohit.kumar@demo.gov.in",
        full_name: "Rohit Kumar",
        access_role: "admin",
      } as unknown as T;
    }
    return {
      id: "user-ananya",
      email: "ananya.sharma@demo.gov.in",
      full_name: "Ananya Sharma",
      access_role: "employee",
    } as unknown as T;
  }
  if (endpoint.includes("/api/dashboard/admin")) {
    return MOCK_ADMIN_DASHBOARD as unknown as T;
  }
  if (endpoint.includes("/api/dashboard")) {
    return MOCK_DASHBOARD as unknown as T;
  }
  if (endpoint.includes("/api/competencies")) {
    return MOCK_DASHBOARD.competencies.map((c: CompetencyItem) => ({
      id: c.competency_id,
      name: c.competency_name,
      domain: c.domain,
    })) as unknown as T;
  }
  if (endpoint.includes("/api/assessments/start")) {
    return MOCK_ASSESSMENT as unknown as T;
  }
  if (endpoint.includes("/answers")) {
    // Parse request body to get question_id and selected_answer
    let questionId = "";
    let selectedAnswer = "";
    try {
      if (typeof options.body === "string") {
        const body = JSON.parse(options.body);
        questionId = body.question_id || "";
        selectedAnswer = (body.selected_answer || "").trim().toUpperCase();
      }
    } catch {}

    // Look up the question in mock data to find the correct answer
    const mockQuestion = MOCK_ASSESSMENT.questions.find((q) => q.id === questionId);
    const correctAnswer = (mockQuestion?.correct_answer || "").trim().toUpperCase();
    const isCorrect = !!correctAnswer && selectedAnswer === correctAnswer;

    const explanations: Record<string, string> = {
      "q-1": "Stratified Random Sampling ensures each sub-population is proportionately represented, reducing sampling variance.",
      "q-2": "GVA at basic prices = Output at basic prices minus Intermediate Consumption at purchasers' prices (SNA 2008).",
      "q-3": "pandas.DataFrame.groupby() enables efficient vectorized grouped aggregations in Python.",
    };

    return {
      question_id: questionId,
      is_correct: isCorrect,
      explanation: explanations[questionId] || "Answer evaluated against competency benchmarks.",
      correct_answer: correctAnswer,
    } as unknown as T;
  }
  if (endpoint.includes("/finish")) {
    return {
      assessment_id: "mock-assessment-id-1",
      score: 100,
      completed_at: new Date().toISOString(),
    } as unknown as T;
  }
  if (endpoint.includes("/score")) {
    return MOCK_SCORE_RESULT as unknown as T;
  }
  if (endpoint.includes("/chunks")) {
    return [
      { id: "chunk-1", chunk_index: 0, content: "SNA 2008 macro-aggregates definition and estimation rules.", token_count: 120 },
    ] as unknown as T;
  }
  if (endpoint.includes("/api/learning/content")) {
    return MOCK_LEARNING_CONTENT as unknown as T;
  }
  if (endpoint.includes("/api/ai-questions")) {
    return MOCK_AI_QUESTIONS as unknown as T;
  }
  return undefined;
}

// -------------------------------------------------------------
// CORE FETCH WRAPPER
// -------------------------------------------------------------

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Accept": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorDetail = `Request failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
      } catch {
        // fallback to status text
        errorDetail = response.statusText || errorDetail;
      }
      throw new Error(errorDetail);
    }

    return response.json();
  } catch (err: unknown) {
    // If backend is unreachable or returns network error, fallback gracefully to offline demo data
    const fallback = getDemoFallback<T>(endpoint, options, token);
    if (fallback !== undefined) {
      return fallback;
    }
    throw err;
  }
}

// -------------------------------------------------------------
// PUBLIC & AUTH API CALLS
// -------------------------------------------------------------

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe(token: string): Promise<UserResponse> {
  return request<UserResponse>("/api/auth/me", {}, token);
}

// -------------------------------------------------------------
// DASHBOARD APIS
// -------------------------------------------------------------

export async function getEmployeeDashboard(token: string): Promise<EmployeeDashboardData> {
  return request<EmployeeDashboardData>("/api/dashboard", {}, token);
}

export async function getAdminDashboard(token: string): Promise<AdminDashboardData> {
  return request<AdminDashboardData>("/api/dashboard/admin", {}, token);
}

// -------------------------------------------------------------
// ASSESSMENT & QUIZ APIS
// -------------------------------------------------------------

export async function startAssessment(
  token: string,
  type: "initial" | "learning" | "reassessment" = "initial",
  count: number = 5,
  courseId?: string
): Promise<StartAssessmentResponse> {
  const params = new URLSearchParams({
    assessment_type: type,
    question_count: count.toString(),
  });
  if (courseId) {
    params.append("course_id", courseId);
  }
  return request<StartAssessmentResponse>(
    `/api/assessments/start?${params.toString()}`,
    { method: "POST" },
    token
  );
}

export async function submitAnswer(
  token: string,
  assessmentId: string,
  questionId: string,
  selectedOption: string
): Promise<{ message: string; is_correct: boolean; explanation?: string }> {
  return request(
    `/api/assessments/${assessmentId}/answers`,
    {
      method: "POST",
      body: JSON.stringify({
        question_id: questionId,
        selected_answer: selectedOption,
      }),
    },
    token
  );
}

export async function finishAssessment(
  token: string,
  assessmentId: string
): Promise<FinishAssessmentResponse> {
  return request<FinishAssessmentResponse>(
    `/api/assessments/${assessmentId}/finish`,
    { method: "POST" },
    token
  );
}

export async function scoreAssessment(
  token: string,
  assessmentId: string
): Promise<ScoreAssessmentResponse> {
  return request<ScoreAssessmentResponse>(
    `/api/assessments/${assessmentId}/score`,
    { method: "POST" },
    token
  );
}

// -------------------------------------------------------------
// RECOMMENDATIONS
// -------------------------------------------------------------

export async function getRecommendations(token: string): Promise<{
  total_recommendations: number;
  recommendations: RecommendationItem[];
}> {
  return request("/api/recommendations", {}, token);
}

// -------------------------------------------------------------
// LEARNING CONTENT & RAG
// -------------------------------------------------------------

export async function uploadLearningContent(
  token: string,
  file: File
): Promise<{
  message: string;
  content_id: string;
  file_name: string;
  file_type: string;
  chunk_count: number;
  status: string;
}> {
  const formData = new FormData();
  formData.append("file", file);

  return request(
    "/api/learning/upload",
    {
      method: "POST",
      body: formData,
    },
    token
  );
}

export async function getLearningContents(token: string): Promise<LearningMaterial[]> {
  return request<LearningMaterial[]>("/api/learning/content", {}, token);
}

export async function getContentChunks(
  token: string,
  contentId: string
): Promise<ContentChunkItem[]> {
  return request<ContentChunkItem[]>(
    `/api/learning/content/${contentId}/chunks`,
    {},
    token
  );
}

// -------------------------------------------------------------
// AI QUESTIONS GENERATION & REVIEW
// -------------------------------------------------------------

export async function generateAIQuestions(
  token: string,
  learningContentId: string,
  difficulty: "beginner" | "intermediate" | "advanced" = "beginner",
  count: number = 3
): Promise<{
  learning_content_id: string;
  generated_count: number;
  questions: AIGeneratedQuestionItem[];
}> {
  const params = new URLSearchParams({
    learning_content_id: learningContentId,
    difficulty,
    count: count.toString(),
  });
  return request(
    `/api/ai-questions/generate?${params.toString()}`,
    { method: "POST" },
    token
  );
}

export async function getAIQuestions(token: string): Promise<AIGeneratedQuestionItem[]> {
  return request<AIGeneratedQuestionItem[]>("/api/ai-questions", {}, token);
}

export async function reviewAIQuestion(
  token: string,
  questionId: string,
  payload: {
    status: "approved" | "rejected";
    question_text?: string;
    options?: Record<string, string>;
    correct_answer?: string;
    explanation?: string;
    competency_id?: string;
  }
): Promise<{
  message: string;
  id: string;
  status: string;
  published_question_id?: string;
}> {
  return request(
    `/api/ai-questions/${questionId}/review`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
    token
  );
}

// -------------------------------------------------------------
// MASTER DATA CATALOGS
// -------------------------------------------------------------

export async function getCompetencies(): Promise<Array<{ id: string; name: string; domain: string }>> {
  return request("/api/competencies");
}

export async function getRoles(): Promise<Array<{ id: string; name: string; description: string }>> {
  return request("/api/roles");
}

export async function getCourses(): Promise<Array<{
  id: string;
  title: string;
  provider: string;
  source: string;
  url: string;
  duration_minutes: number;
  level: string;
}>> {
  return request("/api/courses");
}
