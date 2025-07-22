import axios from 'axios';
import axios from 'axios';

const apiClient = axios.create({
  
  baseURL: import.meta.env.VITE_API_URL,
});


// This is an "interceptor" that runs before every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// This interceptor runs after a response is received
apiClient.interceptors.response.use(
  (response) => response, // Simply return the response if it's successful
  (error) => {
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