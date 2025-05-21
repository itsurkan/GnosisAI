"use client";
import { useEffect } from 'react';
import { useRouter ,useSearchParams } from 'next/navigation'; 
import { useAuth } from '../../context/AuthContext';
import { OAuth2Client } from 'google-auth-library';
const GoogleCallbackPage = () => {
 const searchParams = useSearchParams(); // 👈 correct for App Router
  const code = searchParams?.get('code');  // 👈 equivalent of router.query.code

  const { loginWithGoogle } = useAuth(); // 👈 import was missing

  useEffect(() => {
    if (code) {
      loginWithGoogle(code as string);
    }
  }, [code, loginWithGoogle]);

  return <div>Authenticating...</div>;
};

export default GoogleCallbackPage;
