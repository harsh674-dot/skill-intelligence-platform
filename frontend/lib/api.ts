const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim() || "";
const API_BASE_URL =
  configuredApiUrl === "/api" || configuredApiUrl === "/api/"
    ? ""
    : configuredApiUrl.replace(/\/$/, "");


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
  average_helpfulness?: number;
  review_count?: number;
}

export interface EmployeeDashboardData {
  employee: {
    user_id: string;
    email: string;
    full_name: string;
    role_id: string;
    role_name: string;
    designation?: string;
    department?: string;
    cadre?: string;
    education?: string;
    experience_years?: number;
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
    cadres?: Record<string, number>;
    designations?: Record<string, number>;
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
  bloom_tag: string | null;
  options: Record<string, string>;
  correct_answer: string;
  explanation: string;
  source_chunk_ids: string[];
  generation_model: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  updated_at: string;
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "running" | "done" | "failed";
  created_at: string;
  updated_at: string;
  result: {
    learning_content_id: string;
    generated_count: number;
    questions: AIGeneratedQuestionItem[];
  } | null;
  error: string | null;
}

export async function pollJob(
  token: string,
  jobId: string,
  intervalMs = 2000,
  timeoutMs = 120_000
): Promise<JobStatus> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const job = await request<JobStatus>(`/api/jobs/${jobId}`, {}, token);
    if (job.status === "done" || job.status === "failed") return job;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  throw new Error(`Job ${jobId} timed out after ${timeoutMs / 1000}s`);
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  // Ensure real requests are prioritized with healthy timeout
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

  const controller = new AbortController();
  const timeoutMs = endpoint.includes("/health") ? 2000 : 10000;
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `Request failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
      } catch {
        errorDetail = response.statusText || errorDetail;
      }
      throw new Error(errorDetail);
    }

    return response.json();
  } catch (err: unknown) {
    clearTimeout(timeoutId);
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

export async function register(
  email: string,
  password: string,
  full_name: string,
  role_id?: string,
  department?: string,
  designation?: string
): Promise<UserResponse> {
  const body: Record<string, unknown> = { email, password, full_name };
  if (role_id) body.role_id = role_id;
  if (department) body.department = department;
  if (designation) body.designation = designation;
  return request<UserResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
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
): Promise<{ message: string; is_correct: boolean; explanation?: string; correct_answer?: string }> {
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

export interface UploadLearningContentResponse {
  message?: string;
  id?: string;
  content_id?: string;
  file_name: string;
  file_type: string;
  chunk_count: number;
  status: string;
}

export async function uploadLearningContent(
  token: string,
  file: File
): Promise<UploadLearningContentResponse & { content_id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await request<UploadLearningContentResponse>(
    "/api/learning/upload",
    {
      method: "POST",
      body: formData,
    },
    token
  );
  const contentId = response.id ?? response.content_id;

  if (!contentId) {
    throw new Error("Upload response did not include a content id.");
  }

  return { ...response, content_id: contentId };
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

  // 1. Enqueue — backend returns 202 immediately
  const enqueued = await request<{
    job_id: string;
    poll_url: string;
    learning_content_id: string;
    requested_count: number;
  }>(
    `/api/ai-questions/generate?${params.toString()}`,
    { method: "POST" },
    token
  );

  // 2. Poll until the background job completes
  const job = await pollJob(token, enqueued.job_id);

  if (job.status === "failed") {
    throw new Error(job.error ?? "MCQ generation failed.");
  }

  return {
    learning_content_id: job.result?.learning_content_id ?? learningContentId,
    generated_count: job.result?.generated_count ?? 0,
    questions: job.result?.questions ?? [],
  };
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

// -------------------------------------------------------------
// AI CHATBOT (RAG GROUNDED)
// -------------------------------------------------------------

export interface ChatSourceItem {
  chunk_id: string;
  text: string;
  similarity: number;
}

export interface ChatMessageItem {
  id: string;
  session_id: string;
  user_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ChatMessageAnswer {
  session_id: string;
  user_message: ChatMessageItem;
  assistant_message: ChatMessageItem;
  sources: ChatSourceItem[];
  grounded_gaps: string[];
  recommended_courses: string[];
}

export interface ChatSessionSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export async function sendChatMessage(
  token: string,
  message: string,
  sessionId?: string
): Promise<ChatMessageAnswer> {
  return request(
    "/api/chatbot/message",
    {
      method: "POST",
      body: JSON.stringify({
        message,
        session_id: sessionId || null,
      }),
    },
    token
  );
}

export async function getChatHistory(
  token: string,
  sessionId: string
): Promise<ChatMessageItem[]> {
  return request(`/api/chatbot/history/${sessionId}`, {}, token);
}

export async function getChatSessions(
  token: string
): Promise<ChatSessionSummary[]> {
  return request("/api/chatbot/sessions", {}, token);
}

// -------------------------------------------------------------
// COMMUNITY SPACE (EMPLOYEE INTERACTION)
// -------------------------------------------------------------

export interface AuthorSummary {
  id: string;
  full_name: string;
  email: string;
  designation: string | null;
  department: string | null;
  access_role: "employee" | "admin";
}

export interface CommentItem {
  id: string;
  post_id: string;
  author_id: string;
  author: AuthorSummary;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface PostItem {
  id: string;
  author_id: string;
  author: AuthorSummary;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  has_liked: boolean;
}

export interface PostDetailItem extends PostItem {
  comments: CommentItem[];
}

export interface LikeToggleResult {
  post_id: string;
  liked: boolean;
  likes_count: number;
}

export async function getCommunityPosts(
  token: string,
  tag?: string,
  search?: string
): Promise<PostItem[]> {
  const params = new URLSearchParams();
  if (tag) params.set("tag", tag);
  if (search) params.set("search", search);
  const queryStr = params.toString() ? `?${params.toString()}` : "";
  return request(`/api/community/posts${queryStr}`, {}, token);
}

export async function getCommunityPost(
  token: string,
  postId: string
): Promise<PostDetailItem> {
  return request(`/api/community/posts/${postId}`, {}, token);
}

export async function createCommunityPost(
  token: string,
  title: string,
  body: string,
  tags: string[] = []
): Promise<PostItem> {
  return request(
    "/api/community/posts",
    {
      method: "POST",
      body: JSON.stringify({ title, body, tags }),
    },
    token
  );
}

export async function deleteCommunityPost(
  token: string,
  postId: string
): Promise<{ message: string; post_id: string }> {
  return request(
    `/api/community/posts/${postId}`,
    {
      method: "DELETE",
    },
    token
  );
}

export async function addCommunityComment(
  token: string,
  postId: string,
  body: string
): Promise<CommentItem> {
  return request(
    `/api/community/posts/${postId}/comments`,
    {
      method: "POST",
      body: JSON.stringify({ body }),
    },
    token
  );
}

export async function deleteCommunityComment(
  token: string,
  commentId: string
): Promise<{ message: string; comment_id: string }> {
  return request(
    `/api/community/comments/${commentId}`,
    {
      method: "DELETE",
    },
    token
  );
}

export async function toggleCommunityLike(
  token: string,
  postId: string
): Promise<LikeToggleResult> {
  return request(
    `/api/community/posts/${postId}/like`,
    {
      method: "POST",
    },
    token
  );
}

// -------------------------------------------------------------
// EMPLOYEE EXPERIENCE REVIEWS
// -------------------------------------------------------------

export interface ExperienceReviewItem {
  id: string;
  user_id: string;
  user_name: string;
  user_role: string;
  category: "platform" | "training_program" | "onboarding";
  rating: number;
  comments: string | null;
  created_at: string;
}

export interface CategoryAggregationItem {
  category: string;
  average_rating: number;
  total_reviews: number;
  distribution: Record<string, number>;
}

export interface AggregatedReviewsData {
  overall_average: number;
  total_reviews: number;
  categories: CategoryAggregationItem[];
  recent_reviews: ExperienceReviewItem[];
}

export async function submitExperienceReview(
  token: string,
  category: "platform" | "training_program" | "onboarding",
  rating: number,
  comments?: string
): Promise<ExperienceReviewItem> {
  return request(
    "/api/experience-reviews",
    {
      method: "POST",
      body: JSON.stringify({ category, rating, comments }),
    },
    token
  );
}

export async function getMyExperienceReviews(
  token: string
): Promise<ExperienceReviewItem[]> {
  return request("/api/experience-reviews/my", {}, token);
}

export async function getAggregatedExperienceReviews(
  token: string
): Promise<AggregatedReviewsData> {
  return request("/api/experience-reviews/aggregated", {}, token);
}

// -------------------------------------------------------------
// COURSE COMPLETION & HELPFULNESS REVIEWS
// -------------------------------------------------------------

export interface CourseReviewItem {
  id: string;
  user_id: string;
  user_name: string;
  course_id: string;
  helpfulness_rating: number;
  comments: string | null;
  created_at: string;
}

export interface CourseReviewStats {
  course_id: string;
  average_helpfulness: number;
  total_reviews: number;
  reviews: CourseReviewItem[];
}

export async function submitCourseReview(
  token: string,
  courseId: string,
  helpfulnessRating: number,
  comments?: string
): Promise<CourseReviewItem> {
  return request(
    `/api/courses/${courseId}/reviews`,
    {
      method: "POST",
      body: JSON.stringify({
        helpfulness_rating: helpfulnessRating,
        comments,
      }),
    },
    token
  );
}

export async function getCourseReviews(
  courseId: string,
  token?: string
): Promise<CourseReviewItem[]> {
  return request(`/api/courses/${courseId}/reviews`, {}, token);
}

export async function getCourseReviewStats(
  courseId: string,
  token?: string
): Promise<CourseReviewStats> {
  return request(`/api/courses/${courseId}/reviews/stats`, {}, token);
}
export interface TPACApprovalRequestItem {
  id: string;
  course_id: string;
  requested_by: string;
  status: string;
  request_date: string;
  approval_date?: string;
  approved_by?: string;
  comments?: string;
}

export interface TPACApprovalResponse {
  message: string;
  approval_request: TPACApprovalRequestItem;
}

export interface PredictedSkillGap {
  competency_id: string;
  competency_name: string;
  predicted_gap_increase: number;
  timeframe: string;
  reason: string;
}

export interface PredictedCourseSuccess {
  course_id: string;
  user_id: string;
  success_probability: number;
  predicted_completion_time_days: number;
  confidence_score: number;
  factors: string[];
}

export async function submitTPACRequest(courseId: string, requestedBy: string, token?: string): Promise<TPACApprovalResponse> {
  return request(`/api/tpac/request?course_id=${courseId}&requested_by=${requestedBy}`, { method: "POST" }, token);
}

export async function getTPACRequests(status?: string, token?: string): Promise<TPACApprovalRequestItem[]> {
  const url = status ? `/api/tpac/requests?status=${status}` : `/api/tpac/requests`;
  return request(url, {}, token);
}

export async function approveTPACRequest(requestId: string, approvedBy: string, comments?: string, token?: string): Promise<TPACApprovalResponse> {
  let url = `/api/tpac/request/${requestId}/approve?approved_by=${approvedBy}`;
  if (comments) url += `&comments=${encodeURIComponent(comments)}`;
  return request(url, { method: "PUT" }, token);
}

export async function rejectTPACRequest(requestId: string, rejectedBy: string, comments: string, token?: string): Promise<TPACApprovalResponse> {
  return request(`/api/tpac/request/${requestId}/reject?rejected_by=${rejectedBy}&comments=${encodeURIComponent(comments)}`, { method: "PUT" }, token);
}

export async function getPredictedSkillGaps(departmentId?: string, token?: string): Promise<PredictedSkillGap[]> {
  const url = departmentId ? `/api/analytics/predict/skill-gaps?department_id=${departmentId}` : `/api/analytics/predict/skill-gaps`;
  return request(url, {}, token);
}

export async function getPredictedCourseSuccess(courseId: string, userId: string, token?: string): Promise<PredictedCourseSuccess> {
  return request(`/api/analytics/predict/course-success?course_id=${courseId}&user_id=${userId}`, {}, token);
}

// -------------------------------------------------------------
// AUDIT LOGS (ADMIN)
// -------------------------------------------------------------

export async function getAuditLogs(token: string, limit?: number): Promise<Array<{
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}>> {
  const params = new URLSearchParams();
  if (limit) params.set("limit", limit.toString());
  const url = params.toString() ? `/api/audit?${params.toString()}` : "/api/audit";
  return request(url, {}, token);
}

// -------------------------------------------------------------
// DPDP CONSENT (ADMIN)
// -------------------------------------------------------------

export interface DPDPConsentResponse {
  id: string;
  user_id: string;
  purpose: string;
  consent_given: boolean;
  consent_date: string | null;
  withdrawn_date: string | null;
  legal_basis: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DPDPConsentUpdateRequest {
  consent_given: boolean;
  legal_basis: string | null;
  notes: string | null;
}

export async function getDPDPConsent(userId: string, token: string): Promise<DPDPConsentResponse> {
  return request(`/api/dpdp/consent/${userId}`, {}, token);
}

export async function updateDPDPConsent(userId: string, data: DPDPConsentUpdateRequest, token: string): Promise<DPDPConsentResponse> {
  return request(`/api/dpdp/consent/${userId}`, {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

// -------------------------------------------------------------
// ADMIN USER MANAGEMENT
// -------------------------------------------------------------

export interface AdminCreateUserRequest {
  email: string;
  password: string;
  full_name: string;
  role_id?: string;
  department?: string;
  designation?: string;
  access_role: "employee" | "admin" | "manager";
}

export async function adminCreateUser(data: AdminCreateUserRequest, token: string): Promise<UserResponse> {
  return request("/api/auth/admin/create", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function adminListUsers(token: string): Promise<UserResponse[]> {
  return request("/api/auth/admin/users", {}, token);
}

export async function adminDeactivateUser(userId: string, token: string): Promise<{ message: string; user_id: string }> {
  return request(`/api/auth/admin/users/${userId}/deactivate`, {
    method: "PATCH",
  }, token);
}

// -------------------------------------------------------------
// COURSE CRUD (ADMIN)
// -------------------------------------------------------------

export interface CourseCreateRequest {
  title: string;
  description?: string;
  provider?: string;
  source?: string;
  external_id?: string;
  url?: string;
  duration_minutes?: number;
  level?: string;
}

export async function createCourse(data: CourseCreateRequest, token: string): Promise<{
  id: string;
  title: string;
  description: string | null;
  provider: string | null;
  source: string;
  external_id: string | null;
  url: string | null;
  duration_minutes: number | null;
  level: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}> {
  return request("/api/courses", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function updateCourse(courseId: string, data: Partial<CourseCreateRequest>, token: string): Promise<{
  id: string;
  title: string;
  description: string | null;
  provider: string | null;
  source: string;
  external_id: string | null;
  url: string | null;
  duration_minutes: number | null;
  level: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}> {
  return request(`/api/courses/${courseId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteCourse(courseId: string, token: string): Promise<void> {
  return request(`/api/courses/${courseId}`, {
    method: "DELETE",
  }, token);
}

// -------------------------------------------------------------
// QUESTION CRUD (ADMIN)
// -------------------------------------------------------------

export interface QuestionCreateRequest {
  competency_id: string;
  question_text: string;
  question_type?: string;
  difficulty?: string;
  options: Record<string, string>;
  correct_answer: string;
  explanation?: string;
  bloom_tag?: string;
}

export async function createQuestion(data: QuestionCreateRequest, token: string): Promise<{
  id: string;
  competency_id: string;
  question_text: string;
  question_type: string;
  difficulty: string;
  options: Record<string, string>;
  correct_answer: string;
  explanation: string | null;
  source_content_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}> {
  return request("/api/questions", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function updateQuestion(questionId: string, data: Partial<QuestionCreateRequest>, token: string): Promise<{
  id: string;
  competency_id: string;
  question_text: string;
  question_type: string;
  difficulty: string;
  options: Record<string, string>;
  correct_answer: string;
  explanation: string | null;
  source_content_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}> {
  return request(`/api/questions/${questionId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }, token);
}

export async function deleteQuestion(questionId: string, token: string): Promise<void> {
  return request(`/api/questions/${questionId}`, {
    method: "DELETE",
  }, token);
}

// -------------------------------------------------------------
// RECOMMENDATION ACTIONS
// -------------------------------------------------------------

export async function acceptRecommendation(recommendationId: string, token: string): Promise<{ message: string; recommendation_id: string }> {
  return request(`/api/recommendations/${recommendationId}/accept`, {
    method: "POST",
  }, token);
}

export async function dismissRecommendation(recommendationId: string, token: string): Promise<{ message: string; recommendation_id: string }> {
  return request(`/api/recommendations/${recommendationId}/dismiss`, {
    method: "POST",
  }, token);
}

// -------------------------------------------------------------
// ASSESSMENT HISTORY
// -------------------------------------------------------------

export interface AssessmentHistoryItem {
  assessment_id: string;
  assessment_type: string;
  status: string;
  score: number | null;
  total_questions: number;
  answered_questions: number;
  started_at: string;
  completed_at: string | null;
}

export interface AssessmentHistoryResponse {
  total_assessments: number;
  assessments: AssessmentHistoryItem[];
}

export async function getAssessmentHistory(token: string): Promise<AssessmentHistoryResponse> {
  return request("/api/assessments/history", {}, token);
}
