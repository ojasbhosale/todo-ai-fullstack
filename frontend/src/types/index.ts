export interface Task {
  id: string;
  title: string;
  description: string;
  category: string;
  priority_score: number;
  deadline: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  ai_enhanced_description: string;
  ai_suggested_tags: string[];
  context_references: string[];
  is_overdue: boolean;
  priority_label: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  category?: string;
  priority_score?: number;
  deadline?: string | null;
  status?: string;
}

export interface TaskUpdate extends Partial<TaskCreate> {
  ai_enhanced_description?: string;
  ai_suggested_tags?: string[];
  context_references?: string[];
}

import React from 'react';

export interface ContextEntry {
  id: string;
  content: string;
  source_type: 'email' | 'whatsapp' | 'notes' | 'calendar';
  processed_insights: Record<string, React.ReactNode>;
  metadata: Record<string, React.ReactNode>;
  is_processed: boolean;
  relevance_score: number;
  extracted_keywords: string[];
  content_preview: string;
  created_at: string;
}

export interface ContextEntryCreate {
  content: string;
  source_type: 'email' | 'whatsapp' | 'notes' | 'calendar';
  metadata?: Record<string, React.ReactNode>;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  usage_frequency: number;
  color: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  color?: string;
  is_active?: boolean;
}

export interface AITaskSuggestion {
  priority_score: number;
  suggested_deadline: string | null;
  enhanced_description: string;
  suggested_category: string;
  ai_suggested_tags: string[];
  reasoning: string;
  estimated_duration: string;
  context_insights: string[];
}

export interface TaskStatistics {
  total_tasks: number;
  pending_tasks: number;
  in_progress_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  high_priority_tasks: number;
  categories: string[];
  average_priority: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}