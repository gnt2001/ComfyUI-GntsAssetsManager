import os
import folder_paths
from aiohttp import web
from server import PromptServer

# --- 1. 配置与路径 ---
INPUT_DIR = folder_paths.get_input_directory()
OUTPUT_DIR = folder_paths.get_output_directory()
ALLOWED_IMG = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
WEB_DIRECTORY = "./web"

# --- 2. 辅助函数 ---
def get_sorted_files(directory, extensions):
    if not os.path.exists(directory):
        return []
    files = [f for f in os.listdir(directory) if any(f.lower().endswith(ext) for ext in extensions)]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    return files

# --- 3. 路由处理逻辑 ---

async def list_input(request):
    return web.json_response(get_sorted_files(INPUT_DIR, ALLOWED_IMG))

async def upload_input(request):
    reader = await request.multipart()
    count = 0
    while True:
        part = await reader.next()
        if part is None: break
        if part.name == 'files':
            filename = part.filename
            if any(filename.lower().endswith(ext) for ext in ALLOWED_IMG):
                filepath = os.path.join(INPUT_DIR, filename)
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk: break
                        f.write(chunk)
                count += 1
    return web.json_response({"success": True, "count": count})

async def delete_input(request):
    data = await request.json()
    filenames = data.get('filenames', [])
    for name in filenames:
        try: os.remove(os.path.join(INPUT_DIR, name))
        except: continue
    return web.json_response({"success": True})

async def list_output(request):
    return web.json_response(get_sorted_files(OUTPUT_DIR, ['.mp4']))

async def delete_output(request):
    filename = request.match_info.get('filename')
    try:
        os.remove(os.path.join(OUTPUT_DIR, filename))
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def delete_all_output(request):
    files = get_sorted_files(OUTPUT_DIR, ['.mp4'])
    for f in files:
        try: os.remove(os.path.join(OUTPUT_DIR, f))
        except: continue
    return web.json_response({"success": True})

async def delete_others_output(request):
    filename = request.match_info.get('filename')
    files = get_sorted_files(OUTPUT_DIR, ['.mp4'])
    for f in files:
        if f != filename:
            try: os.remove(os.path.join(OUTPUT_DIR, f))
            except: continue
    return web.json_response({"success": True})

# --- 4. 路由注册逻辑 ---

# 包装在函数中，确保 PromptServer.instance 已存在
def setup_routes():
    server = PromptServer.instance
    routes = server.app.router
    
    # 业务路由
    routes.add_get("/gnts-assets-manager/input/list", list_input)
    routes.add_post("/gnts-assets-manager/input/upload", upload_input)
    routes.add_post("/gnts-assets-manager/input/delete", delete_input)
    routes.add_static("/gnts-assets-manager/input/view/", INPUT_DIR)
    
    routes.add_get("/gnts-assets-manager/output/list", list_output)
    routes.add_delete("/gnts-assets-manager/output/delete/{filename}", delete_output)
    routes.add_delete("/gnts-assets-manager/output/delete_all", delete_all_output)
    routes.add_delete("/gnts-assets-manager/output/delete_others/{filename}", delete_others_output)
    routes.add_static("/gnts-assets-manager/output/view/", OUTPUT_DIR)
    
    # UI 页面服务
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    
    # 这里改用 add_get 而不是装饰器，更稳定
    async def get_ui(request):
        index_path = os.path.join(curr_dir, "web", "index.html")
        return web.FileResponse(index_path)
        
    routes.add_get("/gnts-assets-manager", get_ui)


setup_routes()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]