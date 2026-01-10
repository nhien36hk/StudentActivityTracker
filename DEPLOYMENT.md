# 🚀 Deployment Guide - NRL Tracker

## Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account
- Your repository pushed to GitHub

### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit: NRL Tracker v1.0"
git remote add origin https://github.com/nhien36hk/StudentActivityTracker.git
git push -u origin main
```

2. **Visit Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with GitHub

3. **Deploy**
- Click "New app"
- Select your repository: `nhien36hk/StudentActivityTracker`
- Branch: `main`
- Main file path: `app.py`
- Click "Deploy!"

4. **Done! 🎉**
- Your app will be live at: `https://nrl-tracker.streamlit.app`
- Streamlit auto-updates on git push

### Important Notes

⚠️ **Data Files Required:**
Make sure these files exist before deploying:
- `data/students.json` - Main student database
- `data/raw_activities.json` - Raw activity records

If missing, run:
```bash
python scripts/build_data.py
```

## Deploy to Heroku (Alternative)

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create `setup.sh`**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. **Create `Procfile`**
```
web: sh setup.sh && streamlit run app.py
```

4. **Deploy**
```bash
heroku create nrl-tracker
git push heroku main
heroku open
```

## Deploy to Docker

1. **Create `Dockerfile`**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

2. **Build & Run**
```bash
docker build -t nrl-tracker .
docker run -p 8501:8501 nrl-tracker
```

## Environment Variables (Optional)

No environment variables required! App works out of the box.

## Performance Tips

### For Large Datasets
- Enable Streamlit caching (already implemented)
- Consider splitting `students.json` by class/year
- Use database (PostgreSQL/MongoDB) for 10k+ students

### Monitoring
- Streamlit Cloud provides built-in analytics
- Check `data/search_logs.json` for usage stats

## Security Checklist

✅ No sensitive data in code  
✅ `.gitignore` configured properly  
✅ No API keys required  
✅ HTTPS enabled by default (Streamlit Cloud)  
✅ No user authentication (privacy-first)  

## Cost

| Platform | Cost | Notes |
|----------|------|-------|
| Streamlit Cloud | **FREE** | 1 app, unlimited users |
| Heroku | $7/month | Hobby tier |
| Docker (VPS) | $5-20/month | DigitalOcean, Linode |

## Troubleshooting

### App crashes on startup
**Solution**: Check `data/students.json` exists

### Slow loading
**Solution**: Enable caching with `@st.cache_data`

### Out of memory
**Solution**: Reduce data size or upgrade plan

## Post-Deployment

1. **Share URL** with students
2. **Monitor** usage in Streamlit Cloud dashboard
3. **Update** code via git push (auto-deploys)
4. **Analyze** `search_logs.json` for insights

---

Need help? Open an issue on [GitHub](https://github.com/nhien36hk/StudentActivityTracker/issues)





