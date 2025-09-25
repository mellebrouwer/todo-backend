from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(title="Todo API", description="A simple todo management API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoCreate(BaseModel):
    text: str

class Todo(BaseModel):
    id: int
    text: str
    completed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None

# In-memory storage with some sample data
todos = [
    Todo(id=1, text="Welcome to your Todo App! 🎉", completed=False, created_at=datetime.now()),
    Todo(id=2, text="Try adding a new todo", completed=False, created_at=datetime.now())
]
next_id = 3

@app.get("/")
async def root():
    return {
        "message": "Todo API v1.0.0 is running! 🚀",
        "endpoints": {
            "GET /todos": "Get all todos",
            "POST /todos": "Create a new todo",
            "PUT /todos/{id}": "Toggle todo completion",
            "DELETE /todos/{id}": "Delete a todo",
            "GET /stats": "Get todo statistics"
        }
    }

@app.get("/todos", response_model=List[Todo])
async def get_todos():
    return sorted(todos, key=lambda x: x.created_at, reverse=True)

@app.post("/todos", response_model=Todo)
async def create_todo(todo_data: TodoCreate):
    global next_id
    new_todo = Todo(
        id=next_id, 
        text=todo_data.text.strip(),
        created_at=datetime.now()
    )
    todos.append(new_todo)
    next_id += 1
    return new_todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            todo.completed_at = datetime.now() if todo.completed else None
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    global todos
    original_length = len(todos)
    todos = [todo for todo in todos if todo.id != todo_id]
    if len(todos) == original_length:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

@app.get("/stats")
async def get_stats():
    total = len(todos)
    completed = sum(1 for todo in todos if todo.completed)
    return {
        "total": total,
        "completed": completed,
        "remaining": total - completed,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
