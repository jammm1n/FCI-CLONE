import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import CaseListPage from './pages/CaseListPage';
import InvestigationPage from './pages/InvestigationPage';

export default function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/cases"
        element={
          <ProtectedRoute>
            <CaseListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/investigation/:caseId"
        element={
          <ProtectedRoute>
            <InvestigationPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/cases' : '/login'} replace />}
      />
    </Routes>
  );
}
