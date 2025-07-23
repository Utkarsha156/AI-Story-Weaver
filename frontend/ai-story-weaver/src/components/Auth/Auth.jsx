import React, { useState } from 'react';
import apiClient from '../../api'; // Use the configured API client instead of axios directly
import "./auth.css";

const Auth = ({ setToken }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        const endpoint = isLogin ? '/auth/login' : '/auth/register';
        const payload = isLogin ? { username, password } : { username, email, password };

        try {
            if (!isLogin) {
                // Registration
                await apiClient.post(endpoint, payload);
                alert('Registration successful! Please log in.');
                setIsLogin(true);
                setPassword(''); // Clear password field
            } else {
                // Login
                const response = await apiClient.post(endpoint, payload);
                setToken(response.data.access_token);
            }
        } catch (err) {
            console.error('Auth error:', err);
            setError(
                err.response?.data?.msg || 
                err.response?.data?.message || 
                'An error occurred. Please try again.'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-modal-backdrop">
            <div className="auth-container">
                <h2>{isLogin ? 'Login to create stories!' : 'Register to create stories!'}</h2>
                {error && <p className="error-message">{error}</p>}
                <form onSubmit={handleSubmit} className="auth-form">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        disabled={loading}
                    />
                    {!isLogin && (
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            disabled={loading}
                        />
                    )}
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        disabled={loading}
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
                    </button>
                </form>
                <div className="auth-toggle">
                    <button 
                        type="button"
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError('');
                            setPassword('');
                        }}
                        disabled={loading}
                    >
                        {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Auth;