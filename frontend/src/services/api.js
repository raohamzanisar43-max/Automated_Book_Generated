import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// Book API endpoints
export const bookAPI = {
  // Get all books
  getBooks: async (params = {}) => {
    const response = await api.get('/books', { params });
    return response.data;
  },

  // Get single book
  getBook: async (id) => {
    const response = await api.get(`/books/${id}`);
    return response.data;
  },

  // Create new book
  createBook: async (bookData) => {
    const response = await api.post('/books', bookData);
    return response.data;
  },

  // Update book
  updateBook: async (id, bookData) => {
    const response = await api.put(`/books/${id}`, bookData);
    return response.data;
  },

  // Update outline
  updateOutline: async (id, outlineData) => {
    const response = await api.put(`/books/${id}/outline`, outlineData);
    return response.data;
  },

  // Regenerate outline
  regenerateOutline: async (id) => {
    const response = await api.post(`/books/${id}/regenerate-outline`);
    return response.data;
  },

  // Get book chapters
  getBookChapters: async (id) => {
    const response = await api.get(`/books/${id}/chapters`);
    return response.data;
  },

  // Generate chapter
  generateChapter: async (id, chapterNumber, chapterData) => {
    const response = await api.post(`/books/${id}/chapters/${chapterNumber}`, chapterData);
    return response.data;
  },

  // Final review
  finalReview: async (id, reviewData) => {
    const response = await api.put(`/books/${id}/final-review`, reviewData);
    return response.data;
  },

  // Export book
  exportBook: async (id, format) => {
    const response = await api.post(`/books/${id}/export`, { format });
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health', { baseURL: 'http://localhost:8000' });
  return response.data;
};

export default api;
