export type UserRole = 'WORKER' | 'SAFETY_OFFICER' | 'MANAGER' | 'ADMIN';

export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  department: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserRegisterPayload {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  department: string;
}

export type ReportType = 'UNSAFE_ACT' | 'UNSAFE_CONDITION' | 'NEAR_MISS';

export type ReportStatus =
  | 'SUBMITTED'
  | 'AI_ANALYZED'
  | 'REVIEW_REQUIRED'
  | 'ACTION_ASSIGNED'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'VERIFIED'
  | 'CLOSED';

export type SIFRiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ActionStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';

export interface AIAnalysis {
  sif_precursor: boolean;
  confidence: number;
  hazard_category: string;
  unsafe_act?: string;
  unsafe_condition?: string;
  severity: number;
  evidence: string[];
  model_source: string;
  raw_prediction?: boolean;
  raw_confidence?: number;
  context_type?: string;
  context_adjustment_reason?: string;
  training_familiarity?: number;
  is_novel?: boolean;
}

export interface RiskAssessment {
  score: number;
  level: SIFRiskLevel;
  likelihood: number;
  severity: number;
}

export interface LifeSavingRule {
  rule_id: string;
  rule_name: string;
  description: string;
}

export interface Recommendations {
  immediate_actions: string[];
  preventive_actions: string[];
  verification_actions: string[];
}

export interface PatternData {
  sif_potential: boolean;
  confidence: number;
  activity: string;
  location: string;
  barrier_failure: string;
  precursor_patterns: string[];
  hazard_pattern?: string;
  location_pattern?: string;
  department_pattern?: string;
}

export interface ActionItem {
  action_id: string;
  description: string;
  assigned_to?: string;
  status: ActionStatus;
  due_date?: string;
  completed_at?: string;
  created_at: string;
}

export interface SafetyReport {
  report_id: string;
  report_type: ReportType;
  description: string;
  location: string;
  department: string;
  submitted_by: string;
  created_at: string;
  updated_at: string;
  status: ReportStatus;

  analysis?: AIAnalysis;
  risk?: RiskAssessment;
  life_saving_rule?: LifeSavingRule;
  recommendations?: Recommendations;
  pattern_data?: PatternData;
  actions: ActionItem[];
}

export interface ReportListResponse {
  items: SafetyReport[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ReportCreatePayload {
  report_type: ReportType;
  description: string;
  location: string;
  department: string;
}

export interface CategoryCount {
  name: string;
  count: number;
}

export interface TrendPoint {
  period: string;
  total_reports: number;
  sif_count: number;
  sif_percentage: number;
}

export interface RepeatPattern {
  pattern_type: string;
  description: string;
  affected_entity: string;
  occurrence_count: number;
}

export interface PatternAnalysisResult {
  top_hazards: CategoryCount[];
  top_unsafe_acts: CategoryCount[];
  top_unsafe_conditions: CategoryCount[];
  high_risk_locations: CategoryCount[];
  high_risk_departments: CategoryCount[];
  sif_trends: TrendPoint[];
  repeated_patterns: RepeatPattern[];
}

export interface DashboardSummaryResponse {
  total_reports: number;
  sif_precursor_count: number;
  sif_precursor_percentage: number;
  risk_breakdown: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  actions: {
    open_actions: number;
    in_progress_actions: number;
    resolved_actions: number;
  };
  reports_by_type: Record<string, number>;
  reports_by_department: CategoryCount[];
  reports_by_location: CategoryCount[];
}

export interface RuleResponse {
  rule_id: string;
  rule_name: string;
  description: string;
  hazard_categories: string[];
  unsafe_acts: string[];
  unsafe_conditions: string[];
}

export interface AIStatusResponse {
  mode: string;
  model_loaded: boolean;
  model_path?: string;
  reason?: string;
}

export interface AnalysisResponse {
  report_id: string;
  analysis: AIAnalysis;
  risk: RiskAssessment;
  life_saving_rule: LifeSavingRule;
  recommendations: Recommendations;
  status: string;
}

export interface NotificationItem {
  notification_id: string;
  recipient_role?: UserRole;
  recipient_user_id?: string;
  title: string;
  message: string;
  report_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface ReviewItem {
  review_id: string;
  report_id: string;
  officer_id: string;
  officer_name: string;
  decision: 'ACCEPT' | 'REJECT' | 'CORRECT';
  raw_prediction?: boolean;
  raw_confidence?: number;
  corrected_sif?: boolean;
  corrected_risk?: SIFRiskLevel;
  corrected_hazard?: string;
  corrected_unsafe_act?: string;
  corrected_unsafe_condition?: string;
  correction_reason?: string;
  created_at: string;
}

export interface FeedbackItem {
  feedback_id: string;
  report_id: string;
  report_text: string;
  original_ai_prediction?: boolean;
  original_confidence?: number;
  familiarity_score: number;
  safety_context: string;
  officer_final_label: boolean;
  final_risk: SIFRiskLevel;
  hazard_category?: string;
  unsafe_act?: string;
  unsafe_condition?: string;
  review_reason?: string;
  reviewed_by: string;
  reviewed_at: string;
  status: string;
}

export interface AuditLogItem {
  log_id: string;
  event: string;
  user_id: string;
  user_name: string;
  user_role: UserRole;
  report_id?: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface AssignedAction {
  action_id: string;
  report_id: string;
  description: string;
  assigned_to?: string;
  status: ActionStatus;
  due_date?: string;
  completed_at?: string;
  created_at: string;
  report_description?: string;
  location?: string;
  department?: string;
}
