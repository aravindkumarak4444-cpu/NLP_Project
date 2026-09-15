import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Attach JWT Bearer Token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 Unauthorized globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const formatApiError = (error: any, context: 'login' | 'general' = 'general'): string => {
  if (!error) return 'An unexpected error occurred.';
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return 'Request timed out while connecting to the FastAPI backend server.';
    }
    return 'Cannot connect to FastAPI backend server (http://127.0.0.1:8000). Please verify backend is running on port 8000.';
  }

  const { status, data } = error.response;
  const customMessage = data?.error?.message || data?.detail || data?.message;

  if (customMessage) {
    if (typeof customMessage === 'string') return customMessage;
    if (Array.isArray(customMessage)) {
      return customMessage.map((e: any) => e.msg || e.detail || JSON.stringify(e)).join(', ');
    }
  }

  switch (status) {
    case 400:
      return 'Bad request. Please check your submitted input.';
    case 401:
      return context === 'login'
        ? 'Invalid username/email or password.'
        : 'Authentication required. Please log in again.';
    case 403:
      return 'Permission denied. Your account role does not have access to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 422:
      return 'Validation error. Please verify input fields and formats.';
    case 500:
      return 'Internal server error occurred in the backend AI pipeline. Please try again later.';
    case 503:
      return 'Database or backend service is temporarily unavailable. Please verify MongoDB is running.';
    default:
      return `Server responded with status code ${status}.`;
  }
};

export const checkHealth = async (): Promise<{ status: string; database: string }> => {
  const rootHealthUrl = BASE_URL.replace('/api/v1', '/health');
  const res = await axios.get(rootHealthUrl);
  return res.data;
};

