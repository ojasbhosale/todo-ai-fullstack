import axios from 'axios';
import { Task, TaskCreate, TaskUpdate, ContextEntry, ContextEntryCreate, Category, CategoryCreate, AITaskSuggestion, TaskStatistics } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth (if needed later)
api.interceptors.request.use((config) => {
  // Add auth token if available
  // const token = localStorage.getItem('token');
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Tasks API
export const tasksApi = {
  getAll: async (params?: {
    status?: string;
    category?: string;
    priority?: number;
    overdue?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const response = await api.get<Task[]>('/tasks/', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  create: async (task: TaskCreate) => {
    const response = await api.post<Task>('/tasks/', task);
    return response.data;
  },

  update: async (id: string, task: TaskUpdate) => {
    const response = await api.put<Task>(`/tasks/${id}`, task);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/tasks/${id}`);
    return response.data;
  },

  getAISuggestions: async (data: {
    title: string;
    description?: string;
    category?: string;
    context_data?: any[];
    user_preferences?: Record<string, any>;
    current_workload?: number;
  }) => {
    const response = await api.post<AITaskSuggestion>('/tasks/ai-suggestions/', data);
    return response.data;
  },

  getStatistics: async () => {
    const response = await api.get<TaskStatistics>('/tasks/statistics/');
    return response.data;
  },
};

// Context API
export const contextApi = {
  getAll: async (params?: {
    source_type?: string;
    is_processed?: boolean;
    min_relevance?: number;
    skip?: number;
    limit?: number;
  }) => {
    const response = await api.get<ContextEntry[]>('/context/', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<ContextEntry>(`/context/${id}`);
    return response.data;
  },

  create: async (entry: ContextEntryCreate) => {
    const response = await api.post<ContextEntry>('/context/', entry);
    return response.data;
  },

  update: async (id: string, entry: Partial<ContextEntryCreate>) => {
    const response = await api.put<ContextEntry>(`/context/${id}`, entry);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/context/${id}`);
    return response.data;
  },

  analyze: async (data: {
    content: string;
    source_type: string;
    analyze_sentiment?: boolean;
    extract_keywords?: boolean;
    calculate_relevance?: boolean;
  }) => {
    const response = await api.post('/context/analyze/', data);
    return response.data;
  },
};

// Categories API
export const categoriesApi = {
  getAll: async (params?: {
    is_active?: boolean;
    min_usage?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }) => {
    const response = await api.get<Category[]>('/categories/', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<Category>(`/categories/${id}`);
    return response.data;
  },

  create: async (category: CategoryCreate) => {
    const response = await api.post<Category>('/categories/', category);
    return response.data;
  },

  update: async (id: string, category: Partial<CategoryCreate>) => {
    const response = await api.put<Category>(`/categories/${id}`, category);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/categories/${id}`);
    return response.data;
  },

  getPopular: async (limit?: number) => {
    const response = await api.get<Category[]>('/categories/popular/', {
      params: { limit },
    });
    return response.data;
  },

  getStatistics: async () => {
    const response = await api.get('/categories/statistics/');
    return response.data;
  },
};

export default api;