import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';

const GoogleCallbackPage = () => {
  const router = useRouter();
  const { code } = router.query;
  const { loginWithGoogle } = useAuth();

  useEffect(() => {
    if (code) {
      loginWithGoogle(code as string);
    }
  }, [code, loginWithGoogle]);

  return <div>Authenticating...</div>;
};

export default GoogleCallbackPage;
