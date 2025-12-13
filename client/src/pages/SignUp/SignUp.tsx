import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Eye, EyeOff, Sparkles, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { signupSchema} from "@/validation/userSchema";
import type{ signupUser } from "@/validation/userSchema";
import { useForm, Controller } from "react-hook-form";
import type{ SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import SocialButtons from "@/components/Auth/SocialButtons";
import { signUp } from "@/api/authService";
import type{ ErrorResponse } from "@/types/auth";
import { AxiosError } from "axios";
import PhoneInput from "react-phone-number-input";
import "react-phone-number-input/style.css";

type signupFields = signupUser;

const SignUpForm: React.FC = () => {

  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    setError,
    control,
    formState: { errors, isSubmitting },
  } = useForm<signupFields>({ resolver: zodResolver(signupSchema) });

  const onSubmit: SubmitHandler<signupFields> = async (data) => {
    try {
      const response = await signUp(data);

      if(response.data.success && !response.data.isVerified){
        navigate(`/verifymail?email=${data.email}`);
      }

    } catch (error) {
      const axiosError = error as AxiosError<ErrorResponse>;
      if (axiosError.response && axiosError.response.data) {
        const backendError = axiosError.response.data.message;
        console.error("Error:", backendError);
        setError("root", { message: backendError });
      }
    }
  };

  const [showPassword, setShowPassword] = useState<boolean>(false);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-background">
      {/* Background decorations */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-xl z-10 flex items-center justify-center">
        <Card className="w-full h-full backdrop-blur-sm bg-card shadow-xl border border-border">
          <CardHeader className="space-y-1 flex flex-col items-center pt-8">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center shadow-lg">
                <Sparkles className="text-primary-foreground w-6 h-6" />
              </div>
              <CardTitle className="text-3xl font-bold text-foreground">
                CareerPath
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 px-8 py-5">
            <div className="space-y-2 text-center">
              <h2 className="text-3xl font-semibold tracking-tight text-foreground">
                Sign Up
              </h2>
              <p className="text-sm text-muted-foreground">
                Enter your information to create an account
              </p>
              {errors.root && (
                <div className="flex items-center bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md">
                  <AlertCircle className="w-5 h-5 mr-3" />

                  <span>{errors.root.message}</span>
                </div>
              )}
            </div>
            <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
              <div className="space-y-2">
                <Label
                  htmlFor="username"
                  className="text-sm font-medium text-foreground"
                >
                  Username
                </Label>
                <Input
                  {...register("username")}
                  id="username"
                  placeholder="John Doe"
                  required
                  className="transition-all duration-200 focus:ring-2 focus:ring-primary"
                />
                {errors.username && (
                  <p className="text-red-500">{errors.username.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="email"
                  className="text-sm font-medium text-foreground"
                >
                  Email
                </Label>
                <Input
                  {...register("email")}
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  className="transition-all duration-200 focus:ring-2 focus:ring-primary"
                />
                {errors.email && (
                  <p className="text-red-500">{errors.email.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="phone"
                  className="text-sm font-medium text-foreground"
                >
                  Phone Number
                </Label>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field: { onChange, value } }) => (
                    <PhoneInput
                      international
                      defaultCountry="US"
                      value={value}
                      onChange={onChange}
                      className="phone-input-custom transition-all duration-200 focus:ring-2 focus:ring-primary rounded-md border border-border px-3 py-2"
                    />
                  )}
                />
                {errors.phone && (
                  <p className="text-red-500">{errors.phone.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="password"
                  className="text-sm font-medium text-foreground"
                >
                  Password
                </Label>

                <div className="space-y-2">
                <div className="relative">
                  <Input
                    {...register("password")}
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Your password"
                    required
                    className="transition-all duration-200 focus:ring-2 focus:ring-primary pr-10"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
                {errors.password && (
                    <p className="text-red-500">{errors.password.message}</p>
                  )}

              </div>
              </div>
              <Button
                disabled={isSubmitting}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition-all duration-200 hover:shadow-xl"
                type="submit"
              >
                {isSubmitting && <Loader2 className="h-5 w-5 animate-spin" />}{" "}
                Sign Up
              </Button>
            </form>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <SocialButtons/>
            </div>
            <div className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-medium text-primary hover:text-primary/80 hover:underline"
              >
                Log In
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SignUpForm;
