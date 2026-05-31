from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import boto3
from botocore.exceptions import ClientError
from jinja2 import TemplateNotFound
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
BUCKET_NAME = os.getenv("BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    files = []
    if "Contents" in response:
        files = [obj["Key"] for obj in response["Contents"]]
    content = ""
    src, _, _ = templates.env.loader.get_source(templates.env, "index.html")
    rendered = templates.env.from_string(src).render(request=request, files=files, content=content)
    return HTMLResponse(content=rendered)



@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)
    upload_msg = f"{file.filename} uploaded successfully"
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    files = []
    if "Contents" in response:
        files = [obj["Key"] for obj in response["Contents"]]
    src, _, _ = templates.env.loader.get_source(templates.env, "index.html")
    rendered = templates.env.from_string(src).render(request=request, files=files, content=upload_msg)
    return HTMLResponse(content=rendered)
  

@app.post("/parse", response_class=HTMLResponse)
async def parse_file(request: Request, filename: str = Form(...)):
    selected = filename
    response = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    content = response["Body"].read().decode("utf-8")
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    files = []
    if "Contents" in response:
        files = [obj["Key"] for obj in response["Contents"]]
    src, _, _ = templates.env.loader.get_source(templates.env, "index.html")
    rendered = templates.env.from_string(src).render(request=request, files=files, content=content, selected=selected)
    return HTMLResponse(content=rendered)
    
