from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any
import json

class DeploymentFilesGeneratorInput(BaseModel):
    """Input schema for Deployment Files Generator Tool."""
    app_name: str = Field(
        default="whatsapp-bot",
        description="Name of the Flask application (default: whatsapp-bot)"
    )
    python_version: str = Field(
        default="3.11",
        description="Python version for deployment (default: 3.11)"
    )
    port: int = Field(
        default=5000,
        description="Port number for the Flask application (default: 5000)"
    )

class DeploymentFilesGeneratorTool(BaseTool):
    """Tool for generating complete deployment configuration files for Flask WhatsApp bot on Render.com."""

    name: str = "deployment_files_generator"
    description: str = (
        "Generates all necessary deployment files for a Flask WhatsApp bot including "
        "requirements.txt, Procfile, .env template, and deployment instructions for Render.com. "
        "Returns structured JSON with file contents ready for deployment."
    )
    args_schema: Type[BaseModel] = DeploymentFilesGeneratorInput

    def _run(self, app_name: str = "whatsapp-bot", python_version: str = "3.11", port: int = 5000) -> str:
        try:
            # Generate requirements.txt content
            requirements_content = """flask==2.3.3
requests==2.31.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
gunicorn==21.2.0
"""

            # Generate Procfile content
            procfile_content = f"web: gunicorn app:app --bind 0.0.0.0:$PORT"

            # Generate .env template content
            env_template_content = """# WhatsApp Business API Configuration
WHATSAPP_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_ID=your_whatsapp_phone_number_id_here
WHATSAPP_BUSINESS_ID=your_whatsapp_business_account_id_here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=False
"""

            # Generate runtime.txt content for Python version
            runtime_content = f"python-{python_version}"

            # Generate deployment instructions
            deployment_instructions = f"""# Deployment Instructions for {app_name}

## Prerequisites
- Render.com account
- WhatsApp Business API access
- PostgreSQL database (can be created on Render.com)

## Deployment Steps

### 1. Prepare Your Repository
- Ensure your main Flask application file is named 'app.py'
- Add all generated files to your repository root
- Commit and push to your Git repository

### 2. Database Setup (if needed)
- Create a PostgreSQL database on Render.com
- Copy the DATABASE_URL from your database dashboard

### 3. Deploy on Render.com
- Connect your repository to Render.com
- Select "Web Service" deployment type
- Configure the following settings:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
  - Python Version: {python_version}

### 4. Environment Variables Configuration
Set the following environment variables in Render.com dashboard:
- WHATSAPP_TOKEN: Your WhatsApp Business API access token
- WHATSAPP_PHONE_ID: Your WhatsApp phone number ID
- WHATSAPP_BUSINESS_ID: Your WhatsApp Business Account ID
- DATABASE_URL: Your PostgreSQL connection string (if using database)
- FLASK_ENV: production
- FLASK_DEBUG: False

### 5. Webhook Configuration
- After deployment, copy your Render.com app URL
- Configure your WhatsApp webhook URL to: https://your-app-name.onrender.com/webhook
- Set webhook verification token in your WhatsApp Business API settings

## Important Notes
- Render.com automatically detects Python version from runtime.txt
- Free tier apps may sleep after inactivity - consider upgrading for production
- Monitor logs through Render.com dashboard for debugging
- SSL is automatically provided by Render.com

## File Structure
Your repository should contain:
- app.py (your main Flask application)
- requirements.txt (Python dependencies)
- Procfile (deployment configuration)
- runtime.txt (Python version specification)
- .env.example (environment variables template)
"""

            # Create structured response
            deployment_files = {
                "files": {
                    "requirements.txt": {
                        "content": requirements_content.strip(),
                        "description": "Python package dependencies for Flask WhatsApp bot"
                    },
                    "Procfile": {
                        "content": procfile_content,
                        "description": "Process configuration for Render.com deployment"
                    },
                    ".env.example": {
                        "content": env_template_content.strip(),
                        "description": "Environment variables template (rename to .env locally)"
                    },
                    "runtime.txt": {
                        "content": runtime_content,
                        "description": f"Python version specification for Render.com"
                    }
                },
                "configuration": {
                    "app_name": app_name,
                    "python_version": python_version,
                    "port": port,
                    "platform": "Render.com",
                    "deployment_type": "Flask WhatsApp Bot"
                },
                "instructions": deployment_instructions,
                "next_steps": [
                    "Create the main Flask application file (app.py)",
                    "Add all generated files to your repository",
                    "Set up WhatsApp Business API credentials",
                    "Create PostgreSQL database (optional)",
                    "Deploy to Render.com",
                    "Configure environment variables",
                    "Set up WhatsApp webhook URL"
                ]
            }

            return json.dumps(deployment_files, indent=2)

        except Exception as e:
            return f"Error generating deployment files: {str(e)}"