import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  apiRequest,
  getToken,
  removeToken,
  setToken,
} from "../services/api/client";

type User = {
  id: number;
  name: string;
  email: string;
  role?: string;
  is_active?: boolean;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setAuthToken] = useState<string | null>(getToken());
  const [loading, setLoading] = useState(true);

  async function refreshUser() {
    const currentToken = getToken();

    if (!currentToken) {
      setUser(null);
      setAuthToken(null);
      return;
    }

    try {
      const data = await apiRequest<User>("/api/auth/me", {
        token: currentToken,
      });

      setUser(data);
      setAuthToken(currentToken);
    } catch {
      removeToken();
      setUser(null);
      setAuthToken(null);
    }
  }

  async function login(email: string, password: string) {
    const data = await apiRequest<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    });

    setToken(data.access_token);
    setAuthToken(data.access_token);

    const loggedInUser = await apiRequest<User>("/api/auth/me", {
      token: data.access_token,
    });

    setUser(loggedInUser);
  }

  function logout() {
    removeToken();
    setUser(null);
    setAuthToken(null);
  }

  useEffect(() => {
    refreshUser().finally(() => {
      setLoading(false);
    });
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}