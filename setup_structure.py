import os

structure = {
    "backend": [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/logging.py",
        "app/core/exceptions.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/router.py",
        "app/api/v1/endpoints/__init__.py",
        "app/api/v1/endpoints/market.py",
        "app/schemas/__init__.py",
        "app/schemas/request.py",
        "app/schemas/response.py",
        "app/services/__init__.py",
        "app/services/pipeline_service.py",
        "app/engine/__init__.py",
        "app/engine/features.py",
        "app/engine/hmm_model.py",
        "app/adapters/__init__.py",
        "app/adapters/fmp_client.py",
        ".env",
        "requirements.txt",
    ],
    "frontend": [
        "src/components/ui/.gitkeep",
        "src/components/charts/.gitkeep",
        "src/hooks/.gitkeep",
        "src/services/.gitkeep",
        "src/types/.gitkeep",
        "src/pages/.gitkeep",
    ]
}

main_py_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Market Regime Detection API")

# Cấu hình CORS để Frontend gọi được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello Bro! Backend structure is ready 🚀"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
"""

def create_structure():
    base_dir = os.getcwd()
    print(f"🚀 Đang tạo cấu trúc tại: {base_dir}")

    for root_folder, files in structure.items():
        for file_path in files:
            full_path = os.path.join(base_dir, root_folder, file_path)
            directory = os.path.dirname(full_path)
            
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Created dir: {directory}")
            
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    if file_path == "app/main.py":
                        f.write(main_py_content)
                    elif file_path == ".env":
                        f.write("FMP_API_KEY=your_api_key_here")
                    else:
                        pass 
                print(f"📄 Created file: {full_path}")
            else:
                print(f"⚠️ File existed: {full_path}")

    print("\n✅ XONG.")

if __name__ == "__main__":
    create_structure()