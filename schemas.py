from pydantic import BaseModel,Field
from typing import List
from datetime import date

class Salida(BaseModel):
    estatus:str=Field(default="")
    mensaje:str=Field(default="")
    
class Usuario(BaseModel):
    idUsuario:int|None=None
    nombreCompleto:str|None=None
    telefono:str|None=None
    usuario:str|None=None
    contrasena:str|None=None
    tipo:str|None=None
    id:int|None=None

class UsuarioSalida(Salida):
    usuario:Usuario|None=None

class Estudiante(BaseModel):
    idEstudiante:int|None=None
    idTutor:int|None=None
    nombre:str|None=None

class Curso(BaseModel):
    idCurso:int|None=None
    materia:str|None=None

class CalificacionSelect(BaseModel):
    idCalificacion:int|None=None
    mes:int|None=None
    valor:int|None=None

class CalificacionMes(CalificacionSelect):
    curso:Curso|None=None

class CalificacionesSalida(Salida):
    calificaciones:List[CalificacionSelect]|None=[]

class CalificacionesSalidaMes(Salida):
    calificaciones:List[CalificacionMes]|None=[]

class Calificacion(BaseModel):
    idCalificacion:int
    idEstudiante:int
    idCurso:int
    mes:int
    valor:int
    class Config:
        orm_mode=True

class CalificacionInsert(BaseModel):
    idEstudiante:int
    idCurso:int
    mes:int
    valor:int

class CalificacionEdit(BaseModel):
    idCalificacion : int
    valor: int

# Modelo para representar un estudiante en el resultado
class EstudianteGrupo(BaseModel):
    idGrupo: int|None=None
    idCiclo: int|None=None
    grado: int|None=None
    grupo: str|None=None
    idEstudiante: int|None=None
    nombre: str|None=None
    curp: str|None=None
    correo: str|None=None

# Modelo que extiende Salida para incluir una lista de estudiantes
class EstudiantesSalida(Salida):
    datos: List[EstudianteGrupo]|None=None

class CursoDetalles(BaseModel):
    idCurso: int
    materia: str

class CursosSalida(Salida):
    datos: List[CursoDetalles] | None = None

class Ciclo(BaseModel):
    idCiclo: int | None = None
    nombre: str | None = None

class CiclosSalida(Salida):
    datos: List[Ciclo] | None = None