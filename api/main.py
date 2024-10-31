from fastapi import FastAPI,Depends,HTTPException,status
import uvicorn
from fastapi import FastAPI
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import Any
from database import get_db
from schemas import UsuarioSalida, CalificacionesSalida, CalificacionesSalidaMes, Calificacion, CalificacionInsert, Salida, CalificacionEdit, EstudiantesSalida, CursosSalida, CiclosSalida
import models

app = FastAPI()
security=HTTPBasic()

@app.get("/")
def home():
    return {"mensaje":"¡Bienvenido a SolicitudesREST!"}

async def autenticar(credenciales:HTTPBasicCredentials=Depends(security),
               db:Session=Depends(get_db))->UsuarioSalida:
    return models.autenticar(credenciales.username,credenciales.password,db)

@app.get("/calificaciones/estudiantes/",tags=["Calificaciones"],summary="Consultar calificaciones",response_model=CalificacionesSalida)
async def consultarCalificaciones(db:Session=Depends(get_db),
                       salida:UsuarioSalida=Depends(autenticar))->Any:
    if salida.estatus == 'OK' and salida.usuario.tipo == "A":
        calificacion=models.Calificacion()
        return calificacion.consultar(db)
    else:
        return salida.dict()

@app.get("/calificaciones/estudiantes/{idEstudiante}/cursos/{idCurso}",tags=["Calificaciones"],summary="Consultar calificaciones por estudiante por curso",response_model=CalificacionesSalida)
async def consultarCalificacionesEstudianteCurso(idEstudiante:int,idCurso:int,db:Session=Depends(get_db),
                       salida:UsuarioSalida=Depends(autenticar))->Any:
    if salida.estatus == 'OK':
        if salida.usuario.tipo == "A":
            calificacion=models.Calificacion()
            return calificacion.consultarPorEstudiantePorCursoA(db,idEstudiante,idCurso)
        else:
            if salida.usuario.tipo == "T":
                calificacion=models.Calificacion()
                id = int(salida.usuario.id)
                return calificacion.consultarPorEstudiantePorCursoT(db,idEstudiante,idCurso,id)
            else:
                if salida.usuario.tipo == "P":
                    calificacion=models.Calificacion()
                    id = int(salida.usuario.id)
                    return calificacion.consultarPorEstudiantePorCursoP(db,idEstudiante,idCurso,id)
                else:
                    if salida.usuario.tipo == "E":
                        calificacion=models.Calificacion()
                        id = int(salida.usuario.id)
                        if idEstudiante == salida.usuario.id:
                            return calificacion.consultarPorEstudiantePorCursoA(db,idEstudiante,idCurso)
                        else:
                            return calificacion.consultarPorEstudiantePorCursoA(db,0,0)
    else:
        return salida.dict()

@app.get("/calificaciones/estudiantes/{idEstudiante}/ciclos/{idCiclo}/mes/{mes}",tags=["Calificaciones"],summary="Consultar calificaciones por estudiante por mes en un ciclo",response_model=CalificacionesSalidaMes)
async def consultarCalificacionesEstudianteCicloMes(idEstudiante:int,idCiclo:int,mes:int,db:Session=Depends(get_db),
                       salida:UsuarioSalida=Depends(autenticar))->Any:
    if salida.estatus == 'OK':
        if salida.usuario.tipo == "A":
            calificacion=models.Calificacion()
            return calificacion.consultarPorEstudiantePorCicloMesA(db,idEstudiante,idCiclo,mes)
        else:
            if salida.usuario.tipo == "T":
                calificacion=models.Calificacion()
                id = int(salida.usuario.id)
                return calificacion.consultarPorEstudiantePorCicloMesA(db,idEstudiante,idCiclo,mes)
            else:
                if salida.usuario.tipo == "P":
                    calificacion=models.Calificacion()
                    id = int(salida.usuario.id)
                    return calificacion.consultarPorEstudiantePorCicloMesA(db,idEstudiante,idCiclo,mes)
                else:
                    if salida.usuario.tipo == "E":
                        calificacion=models.Calificacion()
                        id = int(salida.usuario.id)
                        if idEstudiante == salida.usuario.id:
                            return calificacion.consultarPorEstudiantePorCicloMesA(db,idEstudiante,idCiclo,mes)
                        else:
                            return calificacion.consultarPorEstudiantePorCicloMesA(db,0,0,0)
    else:
        return salida.dict()

@app.post("/calificaciones", tags=["Calificaciones"], summary="Registrar calificación", response_model=Salida)
async def registrarCalificacion(calificacionInsert: CalificacionInsert, db: Session = Depends(get_db),
                                salida: UsuarioSalida = Depends(autenticar)) -> Any:
    if salida.estatus == 'OK' and salida.usuario.tipo == 'P':  # Verificamos que sea profesor
        # Verificamos si el profesor tiene acceso al curso
        curso_asignado = db.query(models.Curso).join(models.Grupo).filter(
            models.Grupo.idProfesor == salida.usuario.id,  # Verificamos que el profesor está asignado al curso
            models.Curso.idCurso == calificacionInsert.idCurso  # Curso donde quiere insertar
        ).first()
        
        if curso_asignado:
            # Verificamos si el estudiante está en el grupo correspondiente
            estudiante_en_grupo = db.query(models.DetalleGrupo).filter(
                models.DetalleGrupo.idGrupo == curso_asignado.idGrupo,
                models.DetalleGrupo.idEstudiante == calificacionInsert.idEstudiante
            ).first()

            if estudiante_en_grupo:
                # Si el estudiante pertenece al grupo, se permite la inserción de la calificación
                calificacion = models.CalificacionReal(
                    idEstudiante=calificacionInsert.idEstudiante,
                    idCurso=calificacionInsert.idCurso,
                    mes=calificacionInsert.mes,
                    valor=calificacionInsert.valor
                )
                return calificacion.agregar(db)
            else:
                salida.estatus = 'Error'
                salida.mensaje = 'El estudiante no está inscrito en el grupo correspondiente.'
                return salida.dict()
        else:
            salida.estatus = 'Error'
            salida.mensaje = 'El profesor no tiene permiso para insertar calificaciones en este curso.'
            return salida.dict()
    else:
        if salida.estatus == 'OK':
            salida.estatus = 'Error'
            salida.mensaje = 'El usuario no tiene autorización.'
            return salida.dict()
        else:
            return salida.dict()

@app.put("/calificaciones", tags=["Calificaciones"], summary="Editar calificación", response_model=Salida)
async def editarCalificacion(calificacionEdit: CalificacionEdit, db: Session = Depends(get_db),
                              salida: UsuarioSalida = Depends(autenticar)) -> Any:
    if salida.estatus == 'OK' and salida.usuario.tipo == 'P':  # Verificamos que sea profesor
        # Buscamos la calificación que queremos editar
        calificacion = db.query(models.CalificacionReal).filter(models.CalificacionReal.idCalificacion == calificacionEdit.idCalificacion).first()
        
        if not calificacion:
            salida.estatus = 'Error'
            salida.mensaje = 'La calificación no existe.'
            return salida.dict()

        # Verificamos si el profesor tiene acceso al curso de esta calificación
        curso_asignado = db.query(models.Curso).join(models.Grupo).filter(
            models.Grupo.idProfesor == salida.usuario.id,
            models.Curso.idCurso == calificacion.idCurso
        ).first()

        if curso_asignado:
            # Verificamos si el estudiante está en el grupo correspondiente
            estudiante_en_grupo = db.query(models.DetalleGrupo).filter(
                models.DetalleGrupo.idGrupo == curso_asignado.idGrupo,
                models.DetalleGrupo.idEstudiante == calificacion.idEstudiante
            ).first()

            if estudiante_en_grupo:
                # Actualizamos el valor
                calificacion.valor = calificacionEdit.valor
                return calificacion.modificar(db)  # Llamamos al método modificar
            else:
                salida.estatus = 'Error'
                salida.mensaje = 'El estudiante no está inscrito en el grupo correspondiente.'
                return salida.dict()
        else:
            salida.estatus = 'Error'
            salida.mensaje = 'El profesor no tiene permiso para editar esta calificación.'
            return salida.dict()
    else:
        salida.estatus = 'Error'
        salida.mensaje = 'El usuario no tiene autorización.'
        return salida.dict()


        
@app.delete("/calificaciones/{idCalificacion}", tags=["Calificaciones"], summary="Eliminar calificación", response_model=Salida)
async def eliminarCalificacion(idCalificacion: int, db: Session = Depends(get_db),
                                salida: UsuarioSalida = Depends(autenticar)) -> Any:
    if salida.estatus == 'OK' and salida.usuario.tipo == 'P':  # Verificamos que sea profesor
        # Buscamos la calificación que queremos eliminar
        calificacion = db.query(models.CalificacionReal).filter(models.CalificacionReal.idCalificacion == idCalificacion).first()
        
        if not calificacion:
            salida.estatus = 'Error'
            salida.mensaje = 'La calificación no existe.'
            return salida.dict()

        # Verificamos si el profesor tiene acceso al curso de esta calificación
        curso_asignado = db.query(models.Curso).join(models.Grupo).filter(
            models.Grupo.idProfesor == salida.usuario.id,
            models.Curso.idCurso == calificacion.idCurso
        ).first()

        if curso_asignado:
            # Verificamos si el estudiante está en el grupo correspondiente
            estudiante_en_grupo = db.query(models.DetalleGrupo).filter(
                models.DetalleGrupo.idGrupo == curso_asignado.idGrupo,
                models.DetalleGrupo.idEstudiante == calificacion.idEstudiante
            ).first()

            if estudiante_en_grupo:
                # Se puede eliminar la calificación
                return calificacion.eliminar(db)  # Llamamos al método de eliminación
            else:
                salida.estatus = 'Error'
                salida.mensaje = 'El estudiante no está inscrito en el grupo correspondiente.'
                return salida.dict()
        else:
            salida.estatus = 'Error'
            salida.mensaje = 'El profesor no tiene permiso para eliminar esta calificación.'
            return salida.dict()
    else:
        if salida.estatus == 'OK':
            salida.estatus = 'Error'
            salida.mensaje = 'El usuario no tiene autorización.'
            return salida.dict()
        else:
            return salida.dict()

@app.get("/estudiantes", response_model=EstudiantesSalida, tags=["Estudiantes"])
async def obtener_estudiantes(db: Session = Depends(get_db), salida: UsuarioSalida = Depends(autenticar)):
    if salida.estatus == "OK":
        if salida.usuario.tipo == 'P':  # Verificamos que sea un profesor
        # Llamamos a la función que ejecuta el procedimiento almacenado
            return models.estudiantesPorProfesor(salida.usuario.id, db)
        else:
            if salida.usuario.tipo == 'T':
                return models.estudiantesPorTutor(salida.usuario.id, db)
            else:
                if salida.usuario.tipo == 'A':
                     return models.obtenerTodosLosAlumnos(db)
    else:
        return EstudiantesSalida(estatus="Error", mensaje="Usuario no autorizado.")
    
@app.get('/cursos/estudiante/{idEstudiante}', tags=["Cursos"], response_model=CursosSalida)
async def obtenerCursosEstudiante(idEstudiante:int,db: Session = Depends(get_db),
                                   salida: UsuarioSalida = Depends(autenticar)) -> Any:
    if salida.estatus == 'OK':  # Verificamos que sea alumno
        cursos_salida = models.cursosPorEstudiante(idEstudiante, db)
        return cursos_salida  # Devolvemos la salida con los cursos
    else:
        return {"estatus": "Error", "mensaje": "El usuario no tiene autorización."}

@app.get('/ciclos/estudiante/{idEstudiante}', tags=["Ciclos"], response_model=CiclosSalida)
async def obtenerCiclosEstudiante(idEstudiante: int, db: Session = Depends(get_db),
                                    salida: UsuarioSalida = Depends(autenticar)) -> Any:
    if salida.estatus == 'OK':  # Verificamos que sea alumno
        ciclos_salida = models.obtenerCiclosPorEstudiante(idEstudiante, db)
        return ciclos_salida  # Devolvemos la salida con los ciclos
    else:
        return {"estatus": "Error", "mensaje": "El usuario no tiene autorización."}
    
@app.get('/usuarios/autenticar',tags=["Usuarios"],
         summary='Autenticacion de un Usuario',response_model=UsuarioSalida)
async def login(usuario:UsuarioSalida=Depends(autenticar))->Any:
    return usuario

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)