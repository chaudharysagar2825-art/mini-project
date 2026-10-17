import axios, { AxiosError } from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('manas_setu_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Custom API Error class with parsed details
export class ApiError extends Error {
  statusCode: number;
  details: unknown;

  constructor(statusCode: number, message: string, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

// Response interceptor for unified error formatting
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as { detail?: unknown } | undefined;

      let message = 'An unexpected error occurred';

      if (data && data.detail) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          // Pydantic validation error array
          message = data.detail
            .map((item: { loc?: (string | number)[]; msg?: string }) => {
              const loc = item.loc ? item.loc.filter((l) => l !== 'body').join(' -> ') : '';
              return loc ? `${loc}: ${item.msg}` : item.msg;
            })
            .join('; ');
        } else {
          message = JSON.stringify(data.detail);
        }
      } else if (error.message) {
        message = error.message;
      }

      // Handle 401 Unauthorized token expiry or invalid token
      if (status === 401 && !window.location.pathname.includes('/login')) {
        localStorage.removeItem('manas_setu_token');
        localStorage.removeItem('manas_setu_user');
        window.dispatchEvent(new Event('auth:unauthorized'));
      }

      return Promise.reject(new ApiError(status, message, data));
    } else if (error.request) {
      return Promise.reject(
        new ApiError(
          503,
          `Cannot connect to backend server at ${baseURL}. Please verify the FastAPI service is running.`
        )
      );
    } else {
      return Promise.reject(new ApiError(500, error.message));
    }
  }
);
