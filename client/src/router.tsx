import { createBrowserRouter } from "react-router-dom";
import Home from "@/pages/Home/Home";
import RootWrapper from "@/layout/RootWrapper";
import MainLayout from "@/layout/Mainlayout";
import LoginForm from "@/pages/Login/Login";
import SignUpForm from "@/pages/SignUp/SignUp";
import ProtectedRoute from "@/components/ProtectedRoute/ProtectedRoute";
import VerificationEmailSent from "@/pages/EmailVerification/VerificationEmailSent";
import VerificationStatus from "@/pages/EmailVerification/VerificationStatus";
import ForgotPassword from "@/pages/ForgotPassword/ForgotPassword";
import PasswordResetForm from "@/pages/ForgotPassword/PasswordResetForm";
import SimulatePage from "./pages/SimulatePage/SimulatePage";
import CareerFitsPage from "./pages/CareerFitsPage/CareerFitsPage";
import DashboardPage from "./pages/DashboardPage/DashboardPage";
import IndustryInsightsPage from "./pages/IndustryInsightsPage/IndustryInsightsPage";

const mainLayoutRoutes = [
    {
        path: "/",
        index: true,
        element: <Home />,
    }
];

const router = createBrowserRouter([
    {
        path: "/",
        element: <RootWrapper />,
        children: [
            {
                path: "/",
                element: <ProtectedRoute />,
                
            },
            {
                path: "/",
                element: <MainLayout />,
                children: mainLayoutRoutes,
            },
            {
                path: "/Login",
                element: <LoginForm />,
            },
            {
                path: "/SignUp",
                element: <SignUpForm />,
            },
            {
                path: "/verifymail",
                element: <VerificationEmailSent />,
            },
            {
                path: "/verifymail/:verificationToken",
                element: <VerificationStatus />,
            },
            {
                path: "/forgot-password",
                element: <ForgotPassword />,
            },
            {
                path: "/reset-password/:resetToken",
                element: <PasswordResetForm />,
            },
            {
                path: "/simulate",
                element: <SimulatePage />
            },
            {
                path: "/career-fits",
                element: <CareerFitsPage />,
            },
            {
                path: "/dashboard",
                element: <DashboardPage />,
            },
            {
                path: "/industry-insights",
                element: <IndustryInsightsPage />,
            }

        ],
    },
]);

export default router;