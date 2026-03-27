from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from schemas import Curso
from database import get_db
from json import ObjectId
import json
from database import db, redis_client

cursos_router = APIRouter()

@cursos_router.get("/cursos", response_model=List[Curso])
def read_cursos(db = Depends(get_db)):
    cursos = list(db.cursos.find())
    return cursos

@cursos_router.post("/cursos", response_model=Curso)
def create_curso(curso: Curso = Body(...), db = Depends(get_db)):
    curso_dict = curso.dict(exclude={"id"})
    new_curso = db.cursos.insert_one(curso_dict)
    created_curso = db.cursos.find_one({"_id": new_curso.inserted_id})
    return created_curso

@cursos_router.put("/cursos/{codigo_curso}", response_model=Curso)
def update_curso(codigo_curso: str, curso: Curso = Body(...), db = Depends(get_db)):
    db_curso = db.cursos.find_one({"codigo": codigo_curso})
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    curso_dict = {k: v for k, v in curso.dict(exclude_unset=True).items() if k != "id"}
    
    if len(curso_dict) >= 1:
        db.cursos.update_one({"codigo": codigo_curso}, {"$set": curso_dict})

    updated_curso = db.cursos.find_one({"codigo": codigo_curso})
    return updated_curso

@cursos_router.get("/cursos/{codigo_curso}", response_model=Curso)
async def read_curso_por_codigo(codigo_curso: str, db = Depends(get_db)):
    cache_key = f"curso:{codigo_curso}"

    cached_curso = redis_client.get(cache_key)
    if cached_curso:
        return json.loads(cached_curso)

    curso_data = await db.cursos.find_one({"_id": codigo_curso})
    
    if not curso_data:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    curso_data["id"] = str(curso_data.pop("_id"))
    
    redis_client.setex(
        cache_key,
        30,
        json.dumps(curso_data)
    )

    return curso_data
