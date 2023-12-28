import uvicorn
import json
import uuid
import datetime
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException, Form, Query, Request, File, UploadFile, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, headers_enabled=True, in_memory_fallback_enabled=True)

app = FastAPI(docs_url=None, redoc_url=None,)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
@limiter.limit("5000/minute")
async def root(request: Request):
    response_data = {"status": "Server is alive ❤ ( ´･･)ﾉ(._.`)",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "IP": get_remote_address(request)}
    
    json_compatible_item_data = jsonable_encoder(response_data)
    return JSONResponse(content=json_compatible_item_data)

@app.post("/compare")
@limiter.limit("10/day")
async def compare_code( request: Request, code1: str, code2: str):
    try:
        import difflib

        # Split code snippets into lines
        lines1 = code1.splitlines()
        lines2 = code2.splitlines()

        # Perform unified diff
        differ = difflib.unified_diff(lines1, lines2)
        diff_result = '\n'.join(differ)

        # Calculate similarity percentage
        similarity_percentage = difflib.SequenceMatcher(None, code1, code2).ratio() * 100

        # Determine if the code snippets are the same
        same_code = code1 == code2

        # Determine if there are differences in the code
        different_code = not same_code

        if diff_result == "":
            diff_result = {"code1": code1,
                           "code2": code2}

        # Prepare response
        response_data = {
            "similarity_percentage": similarity_percentage,
            "same_code": same_code,
            "different_code": different_code,
            "diff_result": diff_result,  # Include the unified diff result in the response
        }

        json_compatible_item_data = jsonable_encoder(response_data)
        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/format")
def format_code(request: Request,code: str):
    try:
        import autopep8

        # Format the code
        formatted_code = autopep8.fix_code(code)

        # Prepare response
        response_data = {"formatted_code": formatted_code}

        json_compatible_item_data = jsonable_encoder(response_data)
        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dummy storage for saved code pairs
saved_code_pairs = []
pair_id_counter = 1  # Counter for generating unique IDs

class CodePair:
    def __init__(self, pair_id, title, description, tags, code1, code2, shareable_code_id=None):
        self.pair_id = pair_id
        self.title = title
        self.description = description
        self.tags = tags
        self.code1 = code1
        self.code2 = code2
        self.shareable_code_id = shareable_code_id 

    def to_dict(self):
        return {
            "pair_id": self.pair_id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "code1": self.code1,
            "code2": self.code2,
            "shareable_code_id": self.shareable_code_id
        }

@app.post("/save/{pair_id}")
def save_code_pair(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    tags: list = Query([], alias="tags[]"),
    code1: str = Form(...),
    code2: str = Form(...),
):
    global pair_id_counter

    try:
        # Check if a new pair_id needs to be generated
        if pair_id_counter not in {pair.pair_id for pair in saved_code_pairs}:
            pair_id = pair_id_counter
            pair_id_counter += 1
        else:
            # Use the existing pair_id if it has already been assigned
            pair_id = max(pair.pair_id for pair in saved_code_pairs) + 1

        # Create a new CodePair instance
        new_code_pair = CodePair(pair_id=pair_id, title=title, description=description, tags=tags, code1=code1, code2=code2)

        # Add the code pair to the list
        saved_code_pairs.append(new_code_pair)

        # Return success response
        response_data = {"success": True, "message": f"Code pair with ID {pair_id} saved successfully"}

        # Update browser storage with the new data
        serialized_code_pairs = [pair.to_dict() for pair in saved_code_pairs]
        response = JSONResponse(content=response_data)
        response.set_cookie(key="saved_code_pairs", value=json.dumps(serialized_code_pairs))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/saved")
def get_all_saved_code_pairs(request: Request):
    # Retrieve data from the user's browser storage
    saved_pairs_cookie = request.cookies.get("saved_code_pairs")
    if saved_pairs_cookie:
        saved_code_pairs_data = json.loads(saved_pairs_cookie)
        saved_code_pairs = [CodePair(**pair_data) for pair_data in saved_code_pairs_data]
    else:
        saved_code_pairs = []

    # Return a list of all saved code pairs
    return saved_code_pairs


@app.get("/saved/{pair_id}")
def get_saved_code_pair(pair_id: int, request: Request):
# Retrieve data from the user's browser storage
    saved_pairs_cookie = request.cookies.get("saved_code_pairs")
    if saved_pairs_cookie:
        saved_code_pairs_data = json.loads(saved_pairs_cookie)
        saved_code_pairs = [CodePair(**pair_data) for pair_data in saved_code_pairs_data]
    else:
        saved_code_pairs = []

    # Find the code pair with the specified ID
    code_pair = next((pair for pair in saved_code_pairs if pair.pair_id == pair_id), None)

    if code_pair:
        return code_pair.to_dict()
    else:
        raise HTTPException(status_code=404, detail=f"Code pair with ID {pair_id} not found")


@app.get("/share/{pair_id}")
def get_shareable_link(pair_id: int, request: Request):
    # Retrieve data from the user's browser storage
    saved_pairs_cookie = request.cookies.get("saved_code_pairs")
    if saved_pairs_cookie:
        saved_code_pairs_data = json.loads(saved_pairs_cookie)
        saved_code_pairs = [CodePair(**pair_data) for pair_data in saved_code_pairs_data]
    else:
        saved_code_pairs = []

    # Find the code pair with the specified ID
    code_pair = next((pair for pair in saved_code_pairs if pair.pair_id == pair_id), None)

    if code_pair:
        # Check if the code pair already has a shareable_code_id
        if not code_pair.shareable_code_id:
            # Generate a unique shareable code id (UUID)
            shareable_code_id = str(uuid.uuid4())
            shareable_link = f"/share/{shareable_code_id}"

            # Store the shareable code id with the code pair
            code_pair.shareable_code_id = shareable_code_id

            # Update browser storage with the new data
            serialized_code_pairs = [pair.to_dict() for pair in saved_code_pairs]
            response = JSONResponse(content={"shareable_link": shareable_link})
            response.set_cookie(key="saved_code_pairs", value=json.dumps(serialized_code_pairs))
            return response
        else:
            # Return the existing shareable link if one is already assigned
            return {"shareable_link": f"/public/{code_pair.shareable_code_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"Code pair with ID {pair_id} not found")

@app.get("/public/{shareable_code_id}")
def get_saved_code_by_shareable_link(shareable_code_id: str, request: Request):
    # Retrieve data from the user's browser storage
    saved_pairs_cookie = request.cookies.get("saved_code_pairs")
    if saved_pairs_cookie:
        saved_code_pairs_data = json.loads(saved_pairs_cookie)
        saved_code_pairs = [CodePair(**pair_data) for pair_data in saved_code_pairs_data]
    else:
        saved_code_pairs = []

    # Find the code pair with the specified shareable_code_id
    code_pair = next((pair for pair in saved_code_pairs if pair.shareable_code_id == shareable_code_id), None)

    if code_pair:
        return code_pair.to_dict()
    else:
        raise HTTPException(status_code=404, detail=f"Code pair with shareable code ID {shareable_code_id} not found")

def extract_code_from_file(file: UploadFile) -> str:
    """
    Extracts code from a file and returns it as a string.
    """
    try:
        # Read the contents of the file
        contents = file.file.read()
        
        # Convert bytes to string (assuming the file contains text)
        code = contents.decode('utf-8')

        return code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting code from file: {str(e)}")

# @app.post("/upload")
# async def upload_files(request: Request, file1: UploadFile = File(...), file2: UploadFile = File(...)):
#     try:
#         # Extract code from the uploaded files
#         code1 = extract_code_from_file(file1)
#         code2 = extract_code_from_file(file2)

#         # Prepare response
#         response_data = {
#             "code1": code1,
#             "code2": code2
#         }

#         return response_data

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)