import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://ai-story-weaver.onrender.com/api',
  timeout: 30000, // 30 second timeout for hosted services
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Log the request for debugging
    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.baseURL + config.url,
      data: config.data
    });
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log successful responses
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    // Log error responses
    console.error('API Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.response?.data?.msg || error.response?.data?.message || error.message
    });
    
    // If we get a 401 error, the token is bad.
    // Log the user out and redirect to the login page.
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/auth'; 
    }
    return Promise.reject(error);
  }
);

export default apiClient;