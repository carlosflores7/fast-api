from database import Base
from sqlalchemy import Column,Integer,String,text,Date,ForeignKey
from sqlalchemy.orm import Session, relationship
from schemas import Salida, UsuarioSalida, Usuario, CalificacionesSalida, CalificacionesSalidaMes, EstudianteGrupo, EstudiantesSalida, CursosSalida, CursoDetalles,Ciclo,CiclosSalida
import schemas
from fastapi.encoders import jsonable_encoder

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    idEstudiante = Column(Integer, primary_key=True)
    idUsuario = Column(Integer, nullable=False)
    idTutor = Column(Integer, nullable=False)
    estatus = Column(String, nullable=False)
    detalle_grupos = relationship("DetalleGrupo", back_populates="estudiante")

class Grupo(Base):
    __tablename__ = 'grupos'
    idGrupo = Column(Integer, primary_key=True)
    idProfesor = Column(Integer, ForeignKey('profesores.idProfesor'), nullable=False)
    idCiclo = Column(Integer, nullable=False)
    grado = Column(Integer, nullable=False)
    grupo = Column(String(1), nullable=False)

    profesor = relationship("Profesor", back_populates="grupos")
    cursos = relationship("Curso", back_populates="grupo")
    detalle_grupos = relationship("DetalleGrupo", back_populates="grupo")

class DetalleGrupo(Base):
    __tablename__ = 'detalleGrupos'
    idDetalleGrupo = Column(Integer, primary_key=True)
    idGrupo = Column(Integer, ForeignKey('grupos.idGrupo'), nullable=False)
    idEstudiante = Column(Integer, ForeignKey('estudiantes.idEstudiante'), nullable=False)

    grupo = relationship("Grupo", back_populates="detalle_grupos")
    estudiante = relationship("Estudiante", back_populates="detalle_grupos")

class Curso(Base):
    __tablename__ = 'cursos'
    idCurso = Column(Integer, primary_key=True)
    idGrupo = Column(Integer, ForeignKey('grupos.idGrupo'), nullable=False)
    idMateria = Column(Integer, nullable=False)

    grupo = relationship("Grupo", back_populates="cursos")
    calificaciones = relationship("CalificacionReal", back_populates="curso")

class Profesor(Base):
    __tablename__ = 'profesores'
    idProfesor = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    grupos = relationship("Grupo", back_populates="profesor")

class CalificacionReal(Base):
    __tablename__ = 'calificaciones'
    idCalificacion = Column(Integer, primary_key=True)
    idEstudiante = Column(Integer, nullable=False)
    idCurso = Column(Integer, ForeignKey('cursos.idCurso'), nullable=False)
    mes = Column(Integer, nullable=False)
    valor = Column(Integer, nullable=False)

    # Relación con la tabla Curso (una calificación pertenece a un curso)
    curso = relationship("Curso", back_populates="calificaciones")
    
    def agregar(self, db: Session):
            salida = Salida()
            # Verificar si ya existe una calificación para el mismo curso y mes
            existe_calificacion = db.query(CalificacionReal).filter(
                CalificacionReal.idCurso == self.idCurso,
                CalificacionReal.idEstudiante == self.idEstudiante,
                CalificacionReal.mes == self.mes
            ).first()
            
            if existe_calificacion:
                salida.estatus = "Error"
                salida.mensaje = "Ya existe una calificación para este estudiante en este curso y mes."
                return salida.dict()

            try:
                db.add(self)
                db.commit()
                salida.estatus = "OK"
                salida.mensaje = "Calificación agregada con éxito."
            except Exception as e:
                db.rollback()
                salida.estatus = "Error"
                salida.mensaje = f"Error al agregar la calificación: {str(e)}"
            
            return salida.dict()
    
    def modificar(self, db: Session):
        salida = Salida()
        try:
            db.commit()  # Solo se necesita commit ya que modificamos el objeto directamente
            db.refresh(self)  # Refrescamos la instancia para obtener los datos actualizados
            salida.estatus = "OK"
            salida.mensaje = "Calificación editada con éxito."
        except Exception as e:
            db.rollback()
            salida.estatus = "Error"
            salida.mensaje = f"Error al editar la calificación: {str(e)}"
        
        return salida.dict()
    
    def eliminar(self, db: Session):
        salida = Salida()
        try:
            db.delete(self)
            db.commit()
            salida.estatus = "OK"
            salida.mensaje = "Calificación eliminada con éxito."
        except Exception as e:
            db.rollback()  # Asegurarse de revertir en caso de error
            salida.estatus = "Error"
            salida.mensaje = f"Error al eliminar la calificación: {str(e)}"
        return salida.dict()

    
class Calificacion(Base):
    __tablename__='vCalificaciones'
    idCalificacion=Column(Integer,primary_key=True)
    idEstudiante=Column(Integer,nullable=False)
    nombre_completo=Column(String,nullable=False)
    idTutor=Column(Integer,nullable=False)
    idCurso=Column(Integer,nullable=False)
    idGrupo=Column(Integer,nullable=False)
    idProfesor=Column(Integer,nullable=False)
    idCiclo=Column(Integer,nullable=False)
    materia=Column(String,nullable=False)
    mes=Column(Integer,nullable=False)
    calificacion=Column(Integer,nullable=False)
    
    def consultar(self,db:Session):
        salida=CalificacionesSalida()
        try:
            lista=db.query(Calificacion).all()
            listaCalificaciones=[]
            for s in lista:
                objCal=self.to_schema(s)
                listaCalificaciones.append(objCal)
            salida.calificaciones=listaCalificaciones
            salida.estatus='OK'
            salida.mensaje='Listado de Calificaciones'
        except:
            salida.calificaciones = []
            salida.estatus = 'Error'
            salida.mensaje = 'Error al consultar las Calificaciones'
        return salida.dict()
    
    def consultarPorEstudiantePorCursoA(self,db:Session,idEstudiante,idCurso):
        salida=CalificacionesSalida()
        try:
            lista = db.query(Calificacion).filter(Calificacion.idEstudiante == idEstudiante,Calificacion.idCurso == idCurso).all()
            listaCalificaciones=[]
            for s in lista:
                objCal=self.to_schema(s)
                listaCalificaciones.append(objCal)
            salida.calificaciones=listaCalificaciones
            salida.estatus='OK'
            salida.mensaje='Listado de Calificaciones'
        except:
            salida.calificaciones = []
            salida.estatus = 'Error'
            salida.mensaje = 'Error al consultar las Calificaciones'
        return salida.dict()
    
    def to_schema(self, objeto):
        calificacion = schemas.CalificacionSelect()
        
        calificacion.mes = objeto.mes
        calificacion.valor = objeto.calificacion
        calificacion.idCalificacion = objeto.idCalificacion

        return calificacion
    
    def consultarPorEstudiantePorCursoT(self,db:Session,idEstudiante,idCurso,idTutor):
        salida=CalificacionesSalida()
        try:
            lista = db.query(Calificacion).filter(Calificacion.idEstudiante == idEstudiante,Calificacion.idCurso == idCurso, Calificacion.idTutor == idTutor).all()
            listaCalificaciones=[]
            for s in lista:
                objCal=self.to_schema(s)
                listaCalificaciones.append(objCal)
            salida.calificaciones=listaCalificaciones
            salida.estatus='OK'
            salida.mensaje='Listado de Calificaciones'
        except:
            salida.calificaciones = []
            salida.estatus = 'Error'
            salida.mensaje = 'Error al consultar las Calificaciones'
        return salida.dict()
    
    def consultarPorEstudiantePorCursoP(self,db:Session,idEstudiante,idCurso,idProfesor):
        salida=CalificacionesSalida()
        try:
            lista = db.query(Calificacion).filter(Calificacion.idEstudiante == idEstudiante,Calificacion.idCurso == idCurso, Calificacion.idProfesor == idProfesor).all()
            listaCalificaciones=[]
            for s in lista:
                objCal=self.to_schema(s)
                listaCalificaciones.append(objCal)
            salida.calificaciones=listaCalificaciones
            salida.estatus='OK'
            salida.mensaje='Listado de Calificaciones'
        except:
            salida.calificaciones = []
            salida.estatus = 'Error'
            salida.mensaje = 'Error al consultar las Calificaciones'
        return salida.dict()

    def consultarPorEstudiantePorCicloMesA(self,db:Session,idEstudiante,idCiclo,mes):
        salida=CalificacionesSalidaMes()
        try:
            lista = db.query(Calificacion).filter(Calificacion.idEstudiante == idEstudiante,Calificacion.idCiclo == idCiclo,Calificacion.mes == mes).all()
            listaCalificaciones=[]
            for s in lista:
                objCal=self.to_schemaMes(s)
                listaCalificaciones.append(objCal)
            salida.calificaciones=listaCalificaciones
            salida.estatus='OK'
            salida.mensaje='Listado de Calificaciones'
        except:
            salida.calificaciones = []
            salida.estatus = 'Error'
            salida.mensaje = 'Error al consultar las Calificaciones'
        return salida.dict()
    
    def to_schemaMes(self, objeto):
        calificacion = schemas.CalificacionMes()
        curso = schemas.Curso()
        curso.materia = objeto.materia
        curso.idCurso = objeto.idCurso
        calificacion.curso = curso
        calificacion.mes = objeto.mes
        calificacion.valor = objeto.calificacion
        calificacion.idCalificacion = objeto.idCalificacion

        return calificacion
    
def autenticar(email:str,password:str,db:Session):
    entrada={"p_usuario":email,"p_password":password}
    salida = UsuarioSalida()
    try:
        respuesta=db.execute(text('call sp_autenticar_usuario(:p_usuario,'
                                  ':p_password)'),entrada).fetchone()
        salida.estatus="OK"
        salida.mensaje="Listado del Usuario"
        objU=Usuario()
        objU.idUsuario=respuesta[0]
        objU.nombreCompleto=f"{respuesta[1]} {respuesta[2]} {respuesta[3]}"
        objU.telefono=respuesta[4]
        objU.usuario=respuesta[5]
        objU.contrasena=respuesta[6]
        objU.tipo=respuesta[7]
        objU.id=respuesta[8]
        salida.usuario=objU
    except:
        salida.estatus="Error"
        salida.mensaje="Credenciales incorrectas"
    return salida

def estudiantesPorProfesor(idProfesor: int, db: Session):
    salida = EstudiantesSalida()
    try:
        # Ejecutamos el procedimiento almacenado para obtener los alumnos por profesor
        entrada = {"p_idProfesor": idProfesor}
        respuesta = db.execute(text('CALL ObtenerAlumnosPorProfesor(:p_idProfesor)'), entrada).fetchall()
        
        # Verificamos si hay datos
        if respuesta:
            alumnos = []
            for row in respuesta:
                # Crear un objeto para cada alumno y agregarlo a la lista de alumnos
                alumno = EstudianteGrupo(
                    idGrupo=row[0],
                    idCiclo=row[1],
                    grado=row[2],
                    grupo=row[3],
                    idEstudiante=row[4],
                    nombre=f"{row[5]} {row[6]} {row[7]}",
                    curp=row[8],
                    correo=row[9]
                )
                alumnos.append(alumno)

            salida.estatus = "OK"
            salida.mensaje = "Listado de alumnos por profesor obtenido con éxito."
            salida.datos = alumnos  # Asignar la lista de alumnos al campo datos
        else:
            salida.estatus = "Error"
            salida.mensaje = "No se encontraron alumnos para este profesor."

    except Exception as e:
        salida.estatus = "Error"
        salida.mensaje = f"Error al ejecutar el procedimiento almacenado: {str(e)}"
    
    return salida.dict()

def cursosPorEstudiante(idEstudiante: int, db: Session):
    salida = CursosSalida()  # Asegúrate de haber definido esta clase en schemas
    try:
        # Ejecutamos el procedimiento almacenado para obtener los cursos por estudiante
        entrada = {"p_idEstudiante": idEstudiante}
        respuesta = db.execute(text('CALL ObtenerCursosPorEstudiante(:p_idEstudiante)'), entrada).fetchall()
        
        # Verificamos si hay datos
        if respuesta:
            cursos = []
            for row in respuesta:
                # Crear un objeto para cada curso y agregarlo a la lista de cursos
                curso = CursoDetalles(
                    idCurso=row[0],
                    materia=row[1]
                )
                cursos.append(curso)

            salida.estatus = "OK"
            salida.mensaje = "Listado de cursos obtenido con éxito."
            salida.datos = cursos  # Asignar la lista de cursos al campo datos
        else:
            salida.estatus = "Error"
            salida.mensaje = "No se encontraron cursos para este estudiante."

    except Exception as e:
        salida.estatus = "Error"
        salida.mensaje = f"Error al ejecutar el procedimiento almacenado: {str(e)}"
    return salida.dict()


def estudiantesPorTutor(idTutor: int, db: Session):
    salida = EstudiantesSalida()  # Asegúrate de haber definido esta clase en schemas
    try:
        # Ejecutamos el procedimiento almacenado para obtener los alumnos por tutor
        entrada = {"p_idTutor": idTutor}
        respuesta = db.execute(text('CALL ObtenerAlumnosPorTutor(:p_idTutor)'), entrada).fetchall()
        
        # Verificamos si hay datos
        if respuesta:
            alumnos = []
            for row in respuesta:
                # Crear un objeto para cada alumno y agregarlo a la lista de alumnos
                alumno = EstudianteGrupo(
                    idGrupo=row[0],
                    idCiclo=row[1],
                    grado=row[2],
                    grupo=row[3],
                    idEstudiante=row[4],
                    nombre=f"{row[5]} {row[6]} {row[7]}",
                    curp=row[8],
                    correo=row[9]
                )
                alumnos.append(alumno)

            salida.estatus = "OK"
            salida.mensaje = "Listado de alumnos por tutor obtenido con éxito."
            salida.datos = alumnos  # Asignar la lista de alumnos al campo datos
        else:
            salida.estatus = "Error"
            salida.mensaje = "No se encontraron alumnos para este tutor."

    except Exception as e:
        salida.estatus = "Error"
        salida.mensaje = f"Error al ejecutar el procedimiento almacenado: {str(e)}"
    
    return salida.dict()

def obtenerTodosLosAlumnos(db: Session):
    salida = EstudiantesSalida()  # Asegúrate de haber definido esta clase en schemas
    try:
        # Ejecutamos el procedimiento almacenado para obtener todos los alumnos
        respuesta = db.execute(text('CALL ObtenerTodosLosAlumnos()')).fetchall()
        
        # Verificamos si hay datos
        if respuesta:
            alumnos = []
            for row in respuesta:
                # Crear un objeto para cada alumno y agregarlo a la lista de alumnos
                alumno = EstudianteGrupo(
                    idGrupo=row[0],
                    idCiclo=row[1],
                    grado=row[2],
                    grupo=row[3],
                    idEstudiante=row[4],
                    nombre=f"{row[5]} {row[6]} {row[7]}",
                    curp=row[8],
                    correo=row[9]
                )
                alumnos.append(alumno)

            salida.estatus = "OK"
            salida.mensaje = "Listado de alumnos obtenido con éxito."
            salida.datos = alumnos  # Asignar la lista de alumnos al campo datos
        else:
            salida.estatus = "Error"
            salida.mensaje = "No se encontraron alumnos."

    except Exception as e:
        salida.estatus = "Error"
        salida.mensaje = f"Error al ejecutar el procedimiento almacenado: {str(e)}"
    
    return salida.dict()

def obtenerCiclosPorEstudiante(idEstudiante: int, db: Session):
    salida = CiclosSalida()  # Usar la clase CiclosSalida
    try:
        # Ejecutamos el procedimiento almacenado para obtener los ciclos por estudiante
        entrada = {"p_idEstudiante": idEstudiante}
        respuesta = db.execute(text('CALL ObtenerCiclosPorEstudiante(:p_idEstudiante)'), entrada).fetchall()

        # Verificamos si hay datos
        if respuesta:
            ciclos = []
            for row in respuesta:
                # Crear un objeto para cada ciclo y agregarlo a la lista de ciclos
                ciclo = Ciclo(
                    idCiclo=row[0],
                    nombre=row[1]
                )
                ciclos.append(ciclo)

            salida.estatus = "OK"
            salida.mensaje = "Listado de ciclos obtenido con éxito."
            salida.datos = ciclos  # Asignar la lista de ciclos al campo datos
        else:
            salida.estatus = "Error"
            salida.mensaje = "No se encontraron ciclos para este estudiante."

    except Exception as e:
        salida.estatus = "Error"
        salida.mensaje = f"Error al ejecutar el procedimiento almacenado: {str(e)}"
    
    return salida.dict()