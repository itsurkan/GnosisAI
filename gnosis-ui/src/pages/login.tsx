import React from "react";
import { useRouter } from "next/router";

const LoginPage = () => {
  const router = useRouter();

  const handleGoogleLogin = () => {
    router.push("/auth/login");
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Welcome to Gnosis</h1>
        <p style={styles.subtitle}>Please sign in to continue</p>
        <button style={styles.button} onClick={handleGoogleLogin}>
          Sign in with Google
        </button>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f5f5f5",
  },
  card: {
    padding: "2rem",
    borderRadius: "8px",
    backgroundColor: "#fff",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    textAlign: "center",
  },
  title: {
    marginBottom: "0.5rem",
    fontSize: "2rem",
    color: "#333",
  },
  subtitle: {
    marginBottom: "1.5rem",
    fontSize: "1rem",
    color: "#666",
  },
  button: {
    padding: "0.75rem 1.5rem",
    fontSize: "1rem",
    color: "#fff",
    backgroundColor: "#4285F4",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default LoginPage;
