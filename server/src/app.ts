import express, { Request, Response } from 'express';
import { config } from 'dotenv';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import http, { Server } from 'http';
import globalErrorHandler from './middleware/globalErrorHandler';
import passport from 'passport'
import passportConfig from './config/passport';
import authRouter from './auth/authRoute';
import industryInsightsRouter from './routes/industryInsights';
import mongoose from 'mongoose';

config();

const app = express();
mongoose.connect(process.env.DATABASE_URL || 'dfgh')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

const server = http.createServer(app);



app.use(
  cors({
    credentials: true,
    origin: process.env.FRONTEND_URL,
  })
);

app.use(express.json());
app.use(cookieParser());

app.use(passport.initialize());
passportConfig(passport);


app.get('/', (req: Request, res: Response) => {
  res.json({
    message: 'DSU DevHack Server is running',
  });
});

app.use('/api/v1/auth', authRouter);
app.use('/api/v1/industry', industryInsightsRouter);



app.use(globalErrorHandler);

export { server };
