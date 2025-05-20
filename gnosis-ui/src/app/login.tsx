import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const { loginWithGoogle } = useAuth();

  const handleGoogleLogin = () => {
    window.location.href = '/api/auth/google';
  };

  return (
    <div>
      <h1>Login</h1>
      <button onClick={handleGoogleLogin}>Login with Google</button>
    </div>
  );
};

export default LoginPage;
