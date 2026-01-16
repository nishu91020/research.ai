# Vercel CI/CD Deployment Guide

This document outlines the CI/CD pipeline setup for deploying Research Agent Pro to Vercel with serverless backend functions.

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   GitHub Repository (main/develop)      │
└─────────────────────────────────────────┘
              │
              ├──> GitHub Actions
              │    ├─ Lint & Build Check
              │    └─ Python Dependency Check
              │
              └──> Vercel Deploy
                   ├─ Frontend (Vite + React)
                   ├─ Serverless Functions
                   │  ├─ /api/research.py
                   │  └─ /api/azure.py
                   └─ Environment Variables
```

## Prerequisites

1. **Vercel Account**: Create one at https://vercel.com
2. **GitHub Repository**: Push code to GitHub
3. **Environment Variables**: Set in Vercel dashboard or GitHub Secrets

## Setup Instructions

### 1. Create Vercel Project

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Link project (from project root)
vercel link
```

### 2. Configure Environment Variables

Add these to Vercel Project Settings → Environment Variables:

```
GEMINI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key_here
```

### 3. Setup GitHub Actions

#### Create GitHub Secret for Vercel Token:

1. Go to Vercel: Settings → Tokens → Create Token
2. Copy the token
3. Go to GitHub: Settings → Secrets and variables → Actions → New repository secret
4. Name: `VERCEL_TOKEN`
5. Value: Paste your Vercel token

#### Configure Environments (Optional):

1. Go to GitHub: Settings → Environments
2. Create `production` and `preview` environments
3. Add protection rules (require approval before deploying to production)

### 4. Project Structure

```
research-agent-pro/
├── pages/
│   └── api/
│       ├── researchService.py
│       └── azure_responses_api.py
├── api/                          # NEW: Serverless function wrappers
│   ├── research.py
│   └── azure.py
├── src/                          # Frontend code
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
├── .github/workflows/deploy.yml  # CI/CD pipeline
└── package.json
```

## Deployment Flow

### On Push to `main` branch:
1. Checkout code
2. Install Node.js and Python dependencies
3. Run build verification
4. Deploy to Vercel Production
5. Create GitHub deployment record

### On Push to `develop` branch:
1. Same steps as above but deploys to Vercel Preview environment

### On Pull Request:
1. Install dependencies
2. Run build check
3. Deploy preview to Vercel
4. Comment on PR with preview URL

## Serverless Functions

### Available Endpoints

#### Research Service
- **Endpoint**: `/api/research`
- **Type**: Serverless Python Function
- **Runtime**: Python 3.9
- **Memory**: 1024 MB
- **Timeout**: 30 seconds

#### Azure OpenAI
- **Endpoint**: `/api/azure`
- **Method**: POST
- **Body**: 
  ```json
  {
    "input_text": "your query",
    "model": "gpt-4.1"
  }
  ```

### Health Checks
- `/api/research/health` - Research service status
- `/api/azure/health` - Azure service status

## Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_KEY` | Yes | Azure OpenAI API key |
| `NODE_ENV` | No | Development/production mode |
| `VITE_API_BASE_URL` | No | API base URL for frontend |

## Monitoring & Logs

### View Deployment Logs
```bash
# Watch logs in real-time
vercel logs <deployment-url>

# View specific function logs
vercel logs <deployment-url> --follow
```

### Vercel Dashboard
- Go to https://vercel.com/dashboard
- Select your project
- View Deployments, Analytics, and Logs tabs

### GitHub Actions Logs
- Go to GitHub: Actions tab
- Select workflow run
- View detailed logs for each step

## Troubleshooting

### Python Module Import Errors
**Problem**: Import errors in serverless functions
**Solution**: 
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility (3.9+)
- Verify relative import paths

### Environment Variable Not Found
**Problem**: `KeyError` when accessing environment variables
**Solution**:
- Add variable to Vercel Project Settings
- Rebuild project after adding variables
- Verify variable name spelling (case-sensitive)

### Build Fails
**Problem**: Build fails during deployment
**Solution**:
- Check `vercel-build.sh` for errors
- Verify `npm run build` works locally
- Check Node.js/npm versions match

### Serverless Function Timeout
**Problem**: Functions exceed 30-second timeout
**Solution**:
- Optimize function performance
- Increase timeout in `vercel.json` (max 300s)
- Consider async/streaming responses

## Local Development

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Run frontend (Vite)
npm run dev

# In another terminal, run backend
python pages/api/researchService.py
```

## CI/CD Pipeline Configuration

### Build Command
```bash
npm run build
```

### Output Directory
```
dist/
```

### Python Runtime Configuration
```json
{
  "runtime": "python3.9",
  "memory": 1024,
  "maxDuration": 30
}
```

## Best Practices

1. **Secrets Management**: Never commit `.env.local` or secrets
2. **Testing**: Run tests before pushing to main branch
3. **Preview Deployments**: Test on preview environment first
4. **Monitoring**: Set up alerts for failed deployments
5. **Rollback**: Use Vercel dashboard to rollback to previous version
6. **Performance**: Monitor function duration and optimize code

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Support](https://vercel.com/docs/functions/serverless-functions/python)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## Support

For issues or questions:
1. Check Vercel Logs: `vercel logs`
2. Review GitHub Actions logs
3. Check function output in Vercel dashboard
4. Consult documentation links above
