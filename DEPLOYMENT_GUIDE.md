# 🚀 LOKAAH - Pre-Launch Checklist & Deployment Guide

## ✅ Pre-Launch Status

### Critical Components
- [x] Backend API (FastAPI)
- [x] Frontend (HTML/CSS/JS)
- [x] Database Integration (Supabase)
- [x] AI Integration (Gemini)
- [x] Environment Configuration
- [x] Health Check Script
- [x] Error Handling

### Pending Items
- [ ] **IMPORTANT:** Create favicon.ico and og-image.png (see `web_lokaah/images/MISSING_ASSETS.md`)
- [ ] Update CORS_ORIGINS in `.env` with your production domain
- [ ] Optional: Set up SSL/HTTPS for production

---

## 🔧 Quick Start Commands

### 1. Start the Backend Server

**Development Mode (with auto-reload):**
```powershell
.\.venv\Scripts\python.exe main.py
```

**Production Mode (multi-worker):**
```powershell
# First, set DEBUG=false in .env
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Background Mode (Windows):**
```powershell
Start-Process -NoNewWindow -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "main.py"
```

### 2. Serve the Frontend

**Option A: Python HTTP Server (Simple)**
```powershell
cd web_lokaah
python -m http.server 5500
```
Then visit: http://localhost:5500

**Option B: Live Server (VSCode Extension)**
1. Install "Live Server" extension in VSCode
2. Right-click `web_lokaah/index.html`
3. Select "Open with Live Server"

**Option C: http-server (Node.js)**
```powershell
cd web_lokaah
npx http-server -p 5500 -c-1
```

### 3. Run Health Checks

**Full System Health Check:**
```powershell
.\.venv\Scripts\python.exe health_check.py
```

**Quick API Test:**
```powershell
# Check if server is running
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"

# Test question generation
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/question/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"chapter": "trigonometry", "concept": "basic_ratios", "difficulty": 0.5}'
```

---

## 🧪 Complete Testing Workflow

### Step 1: Start Backend
```powershell
# Terminal 1
.\.venv\Scripts\python.exe main.py
```
✅ Expected output: "Application startup complete" or similar

### Step 2: Run Health Check
```powershell
# Terminal 2
.\.venv\Scripts\python.exe health_check.py
```
✅ Expected: All tests pass (5/5)

### Step 3: Start Frontend
```powershell
# Terminal 3
cd web_lokaah
python -m http.server 5500
```
✅ Expected: Server running on port 5500

### Step 4: Manual Browser Testing
1. Open http://localhost:5500
2. Click "Get Started Free" → Should open chat interface
3. Try asking: "Can you generate a trigonometry question?"
4. Verify:
   - ✅ Chat interface loads
   - ✅ Messages send/receive
   - ✅ Math rendering works (KaTeX)
   - ✅ No console errors (F12 Developer Tools)

---

## 📋 Pre-Production Checklist

### Environment Configuration
- [ ] `.env` file exists with all required keys
- [ ] `GEMINI_API_KEY` is set and valid
- [ ] `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are configured
- [ ] `DEBUG=false` for production
- [ ] `AI_RATIO` is set (0.5 recommended for cost/quality balance)
- [ ] `CORS_ORIGINS` includes your production domain

### Security
- [ ] All API keys are in `.env` (not hardcoded)
- [ ] `.env` is in `.gitignore`
- [ ] No sensitive data in client-side JavaScript
- [ ] CORS is restricted (not "*" in production)
- [ ] Rate limiting considered (optional, for production scale)

### Frontend
- [ ] All links work (test navigation)
- [ ] Responsive design verified (mobile, tablet, desktop)
- [ ] Favicon displays correctly
- [ ] No broken image references
- [ ] Meta tags for SEO
- [ ] Analytics setup (optional: Google Analytics, Plausible, etc.)

### Backend
- [ ] All API endpoints respond correctly
- [ ] Error handling is in place
- [ ] Logging is configured
- [ ] Database connections stable
- [ ] AI API calls working

### Documentation
- [ ] README.md is up to date
- [ ] API documentation available at `/docs`
- [ ] Terms & Privacy pages exist

---

## 🚨 Troubleshooting

### Server Won't Start
```powershell
# Check if port 8000 is already in use
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

# Kill process if needed
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
```

### Module Import Errors
```powershell
# Reinstall dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --force-reinstall
```

### Database Connection Errors
1. Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`
2. Test connection: `health_check.py` will show database status
3. Check Supabase dashboard for connection issues

### AI API Errors
1. Verify `GEMINI_API_KEY` in `.env`
2. Check API quota at https://makersuite.google.com
3. Try reducing `AI_RATIO` to use more pattern-based generation

### Frontend Can't Connect to Backend
1. Ensure backend is running on port 8000
2. Check browser console (F12) for CORS errors
3. Verify `CORS_ORIGINS` in `.env` includes your frontend URL
4. Try clearing browser cache

---

## 🌐 Production Deployment Options

### Option 1: Cloud Platform (Recommended)
**Backend:**
- Deploy to: Railway, Render, Fly.io, or Google Cloud Run
- Set environment variables in platform dashboard
- Use platform's domain or custom domain

**Frontend:**
- Deploy to: Vercel, Netlify, or Cloudflare Pages
- Update `CORS_ORIGINS` in backend `.env`
- Update `API_BASE` in `web_lokaah/js/app.js` if needed

### Option 2: VPS (Self-Hosted)
1. Use systemd service for backend
2. Use Nginx as reverse proxy
3. Set up SSL with Let's Encrypt
4. Configure firewall rules

### Option 3: Docker (Containerized)
```dockerfile
# Create Dockerfile for backend
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 📊 Monitoring & Maintenance

### Health Checks (Recommended Schedule)
```powershell
# Run daily or after any code changes
.\.venv\Scripts\python.exe health_check.py
```

### Log Files
- Check console output for errors
- Consider setting up log aggregation (e.g., LogTail, Sentry)

### Performance Monitoring
- Monitor API response times
- Track AI API costs (Gemini usage)
- Monitor database query performance

---

## 📞 Support & Next Steps

### If Everything Works
✅ **You're ready to go live!**

### If Issues Persist
1. Review error messages carefully
2. Check all configuration files
3. Verify all dependencies are installed
4. Test each component individually

### Production Recommendations
- Set up monitoring (UptimeRobot, Pingdom, or similar)
- Configure automated backups (Supabase handles this)
- Set up error tracking (Sentry)
- Implement analytics
- Create user feedback mechanism

---

## 🎯 Performance Optimization Tips

### Cost Optimization
- Keep `AI_RATIO` at 0.5 or lower for most use cases
- Monitor Gemini API usage
- Use caching for repeated questions

### Speed Optimization
- Use CDN for static assets
- Enable gzip compression
- Optimize images (favicon, og-image)
- Minimize CSS/JS (for production)

### Scalability
- Increase worker count in production
- Use connection pooling for database
- Consider load balancer for high traffic

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-16  
**Status:** ✅ Ready for Production (pending image assets)
