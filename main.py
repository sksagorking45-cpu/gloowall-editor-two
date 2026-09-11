from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import UnityPy
import io
from PIL import Image
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-gloowall/")
async def process_gloowall(
    file: UploadFile = File(...),
    target_name: str = Form(...),
    path_id: int = Form(...),
    github_url: str = Form(...)
):
    try:
        # GitHub Blob URL-কে Raw URL-এ কনভার্ট করা (যাতে কোড ফাইলটি ডাউনলোড করতে পারে)
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        # ১. গিটহাব থেকে অরিজিনাল গেম ফাইল ডাউনলোড
        r = requests.get(raw_url)
        bundle_data = r.content

        # ২. ইউজারের ছবি রিসিভ করা
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))

        # ৩. UnityPy দিয়ে টেক্সচার রিপ্লেস করা
        env = UnityPy.load(bundle_data)
        modified = False
        
        for obj in env.objects:
            if obj.type.name == "Texture2D" and obj.path_id == path_id:
                data = obj.read()
                data.image = img
                data.name = target_name
                data.save()
                modified = True
                break
                
        if not modified:
            return {"error": "Path ID পাওয়া যায়নি!"}

        # ৪. LZMA কম্প্রেশন
        out_file = io.BytesIO()
        out_file.write(env.file.save(packer="lzma"))
        out_file.seek(0)

        # ৫. রেডি করা ফাইলটি অ্যাপে ফেরত পাঠানো
        return Response(content=out_file.read(), media_type="application/octet-stream")
    except Exception as e:
        return {"error": str(e)}
