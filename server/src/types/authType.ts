import { Request } from "express";

interface User{
    id: string
}

interface resetToken{
    id: string;
    userId: string;
    token: string;
    expireAt: Date;
    isUsed: Boolean;
    createdAt: Date;
}

export interface AuthRequest extends Request {
    id: string;
    user: User;
    resetToken: resetToken; 
}