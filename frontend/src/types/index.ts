export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'therapist' | 'staff' | string;
}

export interface Guardian {
  name: string;
  phone: string;
  email: string;
  relationship: string;
}

export interface RamReport {
  reportNumber: string;
  issuingRam: string;
  issueDate: string;
  expiryDate: string;
}

export interface AllocatedModule {
  moduleId: string;
  quotaHours: number;
}

export interface Student {
  id: string;
  firstName: string;
  lastName: string;
  tcKimlik: string;
  birthDate: string;
  gender: string;
  disabilityType: string;
  status: 'active' | 'inactive' | string;
  notes?: string;
  guardian?: Guardian;
  ramReport?: RamReport;
  allocatedModules?: AllocatedModule[];
}

export interface TherapistSpecialization {
  moduleId: string;
}

export interface TherapistAvailability {
  dayOfWeek: number;
  startTime: string;
  endTime: string;
}

export interface Therapist {
  id: string;
  firstName: string;
  lastName: string;
  title?: string;
  phone?: string;
  email?: string;
  specializations?: TherapistSpecialization[];
  availabilities?: TherapistAvailability[];
  weeklyHours?: number;
  currentWorkload?: number;
  status?: 'active' | 'inactive' | string;
}

export interface TherapyModule {
  id: string;
  name: string;
  code?: string;
  color?: string;
  duration?: number;
  isGroupEligible?: boolean;
}

export interface Room {
  id: string;
  name: string;
  code: string;
  capacity: number;
  supportedModules?: string[];
  status: 'active' | 'maintenance' | string;
}

export interface SessionParticipant {
  studentId: string;
  studentName?: string;
  attendanceStatus?: 'present' | 'absent' | 'excused' | 'planned' | string;
  isTelafiEligible?: boolean;
}

export interface TherapySession {
  id: string;
  moduleId: string;
  moduleName?: string;
  therapistId: string;
  therapistName?: string;
  roomId: string;
  roomName?: string;
  date: string;
  startTime: string;
  endTime: string;
  status: 'planned' | 'completed' | 'student_absent' | 'cancelled' | string;
  participants: SessionParticipant[];
}

export interface IepGoal {
  id: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'achieved' | 'acquired' | 'maintained' | string;
}

export interface IepPlan {
  id: string;
  studentId: string;
  moduleId: string;
  startDate: string;
  endDate: string;
  goals: IepGoal[];
}

export interface ProgressRecord {
  id: string;
  sessionId: string;
  goalId: string;
  notes: string;
  rating: number;
}

export interface DashboardStats {
  totalStudents: number;
  totalTherapists: number;
  todaySessions: number;
  attendanceRate: number;
  expiredReports: number;
  weeklyOccupancy: number;
  pendingMakeups: number;
  therapistDistribution: { name: string; count: number }[];
}

export interface Alert {
  id: string;
  message: string;
  type: 'warning' | 'error' | 'info';
  date?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page?: number;
  limit?: number;
  items?: T[];
}
