import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import SignupPage from "./pages/SignupPage";
import LoginPage from "@/pages/LoginPage";
import About from "@/pages/About";
import AnalyzePage from "@/pages/AnalyzePage";
import HistoryPage from "@/pages/HistoryPage"; 
import AnalyzeDetailPage from "@/pages/AnalyzeDetailPage";
// import FeedbackPage from "@/pages/FeedbackPage"; // <-- Décommente quand tu crées FeedbackPage
import { Layout } from "@/components/Layout";
import PrivateRoute from "@/components/Auth/PrivateRoute";

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/about" element={<About />} />

          {/* Bloc routes protégées */}
          <Route element={<PrivateRoute />}>
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/analyze/:id" element={<AnalyzeDetailPage />} />
            {/* Décommente la ligne suivante quand la page feedback existe */}
            {/* <Route path="/feedback" element={<FeedbackPage />} /> */}
          </Route>
        </Routes>
      </Layout>
    </Router>
  );
}
