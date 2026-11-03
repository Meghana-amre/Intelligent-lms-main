import express from 'express';
import { runAnalyticsEngine } from '../controllers/analyticsController.js';

const router = express.Router();

router.post('/run', runAnalyticsEngine);
router.get('/run', runAnalyticsEngine);

export default router;