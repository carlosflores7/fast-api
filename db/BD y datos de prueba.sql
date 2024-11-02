create database CDB;
use CDB;

create table materias(
	idMateria int auto_increment not null,
    nombre varchar(50) not null,
    constraint pk_materias primary key(idMateria)
);

create table usuarios(
	idUsuario int auto_increment not null,
    usuario varchar(20) not null,
    contrasena varchar(256) not null,
    nombre varchar(30) not null,
    apellido_p varchar(20) not null,
    apellido_m varchar(20) not null,
    curp varchar(18) not null,
    fecha_nacimiento date not null,
    domicilio varchar(100) not null,
    telefono varchar(12),
    correo varchar(50),
    tipo char(1) not null,
    constraint pk_usuarios primary key(idUsuario),
    constraint uk_usuario_usuario unique(usuario),
    constraint uk_curp_usuario unique(curp),
    constraint uk_telefono_usuario unique(telefono),
    constraint uk_correo_usuario unique(correo)
);

create table administradores(
	idAdministrador int auto_increment not null,
    idUsuario int not null,
    constraint pk_administradores primary key(idAdministrador),
    constraint fk_administradores_usuarios foreign key(idUsuario) references usuarios(idUsuario)
);

create table profesores(
	idProfesor int auto_increment not null,
    idUsuario int not null,
    estatus char(1) not null,
    identificacion mediumblob null,
    constraint pk_profesores primary key(idProfesor),
    constraint fk_profesores_usuarios foreign key(idUsuario) references usuarios(idUsuario)
);

create table tutores(
	idTutor int auto_increment not null,
    idUsuario int not null,
    identificacion mediumblob null,
    constraint pk_tutores primary key(idTutor),
    constraint fk_tutores_usuarios foreign key(idUsuario) references usuarios(idUsuario)
);

create table estudiantes(
	idEstudiante int auto_increment not null,
    idUsuario int not null,
    idTutor int not null,
    idTutor2 int null,
    estatus char(1) not null,
    constraint pk_estudiantes primary key(idEstudiante),
    constraint fk_estudiantes_usuarios foreign key(idUsuario) references usuarios(idUsuario),
    constraint fk_estudiantes_tutores foreign key(idTutor) references tutores(idTutor),
    constraint fk_estudiantes_tutores2 foreign key(idTutor2) references tutores(idTutor)
);

create table ciclos(
	idCiclo int auto_increment not null,
    nombre varchar(100) not null,
    fecha_inicio date not null,
    fecha_final date not null,
    constraint pk_ciclos primary key(idCiclo)
);

create table grupos(
	idGrupo int auto_increment not null,
    idProfesor int not null,
    idCiclo int not null,
    grado int not null,
    grupo char(1) not null,
    constraint pk_grupos primary key(idGrupo),
    constraint fk_grupos_profesores foreign key(idProfesor) references profesores(idProfesor),
    constraint fk_grupos_ciclos foreign key(idCiclo) references ciclos(idCiclo)
);

create table detalleGrupos(
	idDetalleGrupo int auto_increment not null,
    idGrupo int not null,
    idEstudiante int not null,
    constraint pk_detalleGrupos primary key(idDetalleGrupo),
    constraint fk_detalleGrupos_grupos foreign key(idGrupo) references grupos(idGrupo),
    constraint fk_detalleGrupos_estudiantes foreign key(idEstudiante) references estudiantes(idEstudiante)
);

create table cursos(
	idCurso int auto_increment not null,
    idGrupo int not null,
    idMateria int not null,
    constraint pk_cursos primary key(idCurso),
    constraint fk_cursos_grupos foreign key(idGrupo) references grupos(idGrupo),
    constraint fk_cursos_materias foreign key(idMateria) references materias(idMateria)
);

create table calificaciones(
	idCalificacion int auto_increment not null,
    idEstudiante int not null,
    idCurso int not null,
    mes int not null,
    valor int not null,
    constraint pk_calificaciones primary key(idCalificacion),
    constraint fk_calificaciones_estudiantes foreign key(idEstudiante) references estudiantes(idEstudiante),
    constraint fk_calificaciones_cursos foreign key(idCurso) references cursos(idCurso)
);

/*
*********************para uso local****************************

create user user_cdb identified by 'CDB.123';

grant insert,update,delete,select on administradores to user_cdb;
grant insert,update,delete,select on calificaciones to user_cdb;
grant insert,update,delete,select on ciclos to user_cdb;
grant insert,update,delete,select on cursos to user_cdb;
grant insert,update,delete,select on detalleGrupos to user_cdb;
grant insert,update,delete,select on estudiantes to user_cdb;
grant insert,update,delete,select on grupos to user_cdb;
grant insert,update,delete,select on materias to user_cdb;
grant insert,update,delete,select on profesores to user_cdb;
grant insert,update,delete,select on tutores to user_cdb;
grant insert,update,delete,select on usuarios to user_cdb;

*/

CREATE VIEW vCalificaciones AS
SELECT c.idCalificacion,
       e.idEstudiante, 
       CONCAT(u.nombre, ' ', u.apellido_p, ' ', u.apellido_m) AS nombre_completo, 
       e.idTutor,
       cu.idCurso,
       cu.idGrupo,
       g.idProfesor,
       g.idCiclo,
       m.nombre AS materia,
       c.mes AS mes,
       c.valor AS calificacion
FROM calificaciones c
JOIN estudiantes e ON c.idEstudiante = e.idEstudiante
JOIN usuarios u ON e.idUsuario = u.idUsuario
JOIN cursos cu ON c.idCurso = cu.idCurso
JOIN materias m ON cu.idMateria = m.idMateria
JOIN grupos g ON cu.idGrupo = g.idGrupo;


DELIMITER $$

CREATE PROCEDURE sp_autenticar_usuario(p_usuario VARCHAR(100), p_password VARCHAR(256))
BEGIN
    DECLARE v_tipo CHAR(1);

    -- Verifica si el usuario existe y tiene tipo válido
    IF EXISTS (SELECT * FROM usuarios WHERE usuario = p_usuario AND contrasena = p_password AND tipo IN ('A', 'E', 'P', 'T')) THEN
        
        -- Obtiene el tipo de usuario
        SELECT tipo INTO v_tipo FROM usuarios WHERE usuario = p_usuario AND contrasena = p_password;

        -- Si el tipo es 'A' (administrador)
        IF v_tipo = 'A' THEN
            BEGIN
                SELECT u.idUsuario, u.nombre, u.apellido_p, u.apellido_m, u.telefono, u.usuario, u.contrasena, u.tipo, a.idAdministrador AS id
                FROM usuarios u
                JOIN administradores a ON a.idUsuario = u.idUsuario
                WHERE u.usuario = p_usuario AND u.contrasena = p_password;
            END;

        -- Si el tipo es 'E' (estudiante), se verifica el estatus dentro de la tabla 'estudiantes'
        ELSEIF v_tipo = 'E' THEN
            BEGIN
                SELECT u.idUsuario, u.nombre, u.apellido_p, u.apellido_m, u.telefono, u.usuario, u.contrasena, u.tipo, e.idEstudiante AS id
                FROM usuarios u
                JOIN estudiantes e ON e.idUsuario = u.idUsuario
                WHERE u.usuario = p_usuario AND u.contrasena = p_password AND e.estatus = 'A';
            END;

        -- Si el tipo es 'P' (profesor), se verifica el estatus dentro de la tabla 'profesores'
        ELSEIF v_tipo = 'P' THEN
            BEGIN
                SELECT u.idUsuario, u.nombre, u.apellido_p, u.apellido_m, u.telefono, u.usuario, u.contrasena, u.tipo, p.idProfesor AS id
                FROM usuarios u
                JOIN profesores p ON p.idUsuario = u.idUsuario
                WHERE u.usuario = p_usuario AND u.contrasena = p_password AND p.estatus = 'A';
            END;

        -- Si el tipo es 'T' (tutor), no se verifica el estatus
        ELSEIF v_tipo = 'T' THEN
            BEGIN
                SELECT u.idUsuario, u.nombre, u.apellido_p, u.apellido_m, u.telefono, u.usuario, u.contrasena, u.tipo, t.idTutor AS id
                FROM usuarios u
                JOIN tutores t ON t.idUsuario = u.idUsuario
                WHERE u.usuario = p_usuario AND u.contrasena = p_password;
            END;

        END IF;

    END IF;

END $$

DELIMITER ;


DELIMITER //

CREATE PROCEDURE ObtenerAlumnosPorProfesor(
    IN p_idProfesor INT
)
BEGIN
    SELECT 
        g.idGrupo, g.idCiclo, g.grado, g.grupo, 
        e.idEstudiante, u.nombre, u.apellido_p, u.apellido_m, u.curp, u.correo
    FROM 
        grupos g
    INNER JOIN detalleGrupos dg ON g.idGrupo = dg.idGrupo
    INNER JOIN estudiantes e ON dg.idEstudiante = e.idEstudiante
    INNER JOIN usuarios u ON e.idUsuario = u.idUsuario
    WHERE 
        g.idProfesor = p_idProfesor
    ORDER BY 
        g.idGrupo, g.idCiclo, u.apellido_p, u.apellido_m, u.nombre;
    
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE ObtenerCursosPorEstudiante(
    IN p_idEstudiante INT
)
BEGIN
    SELECT 
        c.idCurso, 
        m.nombre AS materia
    FROM 
        cursos c
    INNER JOIN 
        detalleGrupos dg ON c.idGrupo = dg.idGrupo
    INNER JOIN 
        estudiantes e ON dg.idEstudiante = e.idEstudiante
    INNER JOIN 
        materias m ON c.idMateria = m.idMateria
    WHERE 
        e.idEstudiante = p_idEstudiante;
END //

DELIMITER ;


CREATE VIEW VistaEstudiantes AS
SELECT 
    e.idEstudiante,
    e.idTutor,
    CONCAT(u.nombre, ' ', u.apellido_p, ' ', u.apellido_m) AS nombreCompleto
FROM 
    estudiantes e
INNER JOIN 
    usuarios u ON e.idUsuario = u.idUsuario;


DELIMITER //

CREATE PROCEDURE ObtenerAlumnosPorTutor(
    IN p_idTutor INT
)
BEGIN
    SELECT 
        g.idGrupo, g.idCiclo, g.grado, g.grupo, 
        e.idEstudiante, u.nombre, u.apellido_p, u.apellido_m, u.curp, u.correo
    FROM 
        grupos g
    INNER JOIN detalleGrupos dg ON g.idGrupo = dg.idGrupo
    INNER JOIN estudiantes e ON dg.idEstudiante = e.idEstudiante
    INNER JOIN usuarios u ON e.idUsuario = u.idUsuario
    WHERE 
        e.idTutor = p_idTutor  -- Filtramos por idTutor
    ORDER BY 
        g.idGrupo, g.idCiclo, u.apellido_p, u.apellido_m, u.nombre;
    
END //

DELIMITER ;


DELIMITER ;

DELIMITER //

CREATE PROCEDURE ObtenerTodosLosAlumnos()
BEGIN
    SELECT 
        g.idGrupo, g.idCiclo, g.grado, g.grupo, 
        e.idEstudiante, u.nombre, u.apellido_p, u.apellido_m, u.curp, u.correo
    FROM 
        grupos g
    INNER JOIN detalleGrupos dg ON g.idGrupo = dg.idGrupo
    INNER JOIN estudiantes e ON dg.idEstudiante = e.idEstudiante
    INNER JOIN usuarios u ON e.idUsuario = u.idUsuario
    ORDER BY 
        g.idGrupo, g.idCiclo, u.apellido_p, u.apellido_m, u.nombre;
END //

DELIMITER //


DELIMITER //

CREATE PROCEDURE ObtenerCiclosPorEstudiante(
    IN p_idEstudiante INT
)
BEGIN
    SELECT 
        c.idCiclo, 
        c.nombre
    FROM 
        ciclos c
    INNER JOIN grupos g ON c.idCiclo = g.idCiclo
    INNER JOIN detalleGrupos dg ON g.idGrupo = dg.idGrupo
    WHERE 
        dg.idEstudiante = p_idEstudiante
    GROUP BY 
        c.idCiclo, c.nombre;
END //

DELIMITER ;

/*
***************para uso local solamente*********************

grant select on vCalificaciones to user_cdb;
grant execute on procedure sp_autenticar_usuario to user_cdb;
grant execute on procedure ObtenerAlumnosPorProfesor to user_cdb;
grant execute on procedure ObtenerCursosPorEstudiante to user_cdb;   
grant select on VistaEstudiantes to user_cdb;
GRANT EXECUTE ON PROCEDURE ObtenerAlumnosPorTutor TO user_cdb;
GRANT EXECUTE ON PROCEDURE ObtenerTodosLosAlumnos TO user_cdb;
GRANT EXECUTE ON PROCEDURE ObtenerCiclosPorEstudiante TO user_cdb;


*/

---------------------------------------------------------------------------------
---------------------------------DATOS DE PRUEBA---------------------------------
---------------------------------------------------------------------------------

INSERT INTO `materias` (`idMateria`,`nombre`) VALUES (1,'Matematicas');
INSERT INTO `materias` (`idMateria`,`nombre`) VALUES (2,'Ciencias');
INSERT INTO `materias` (`idMateria`,`nombre`) VALUES (3,'Español');

INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (1,'carlosflores7','Hola.123','Carlos Eduardo','Flores','Ayala','FOAC000225HMNLYRA1','2000-02-25','Los Espinos #89','351-185-1543','cflores381@accitesz.com','A');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (2,'profesor1','Hola.123','Juan','Diaz','Martinez','FOAC000225HMNLYRA2','1990-03-05','Galeana 23','100-200-1234','profesor1@es.es','P');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (3,'profesor2','Hola.123','Pablo','Muñiz','Lopez','FOAC000225HMNLYRA3','1999-12-20','Circunvalacion 23','999-999-9898','profesor2@es.es','P');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (4,'tutor1','Hola.123','Diego','Anaya','Beltran','FOAC000225HMNLYRA4','1999-12-21','Nacional 12','111-123-1254','tutor1@es.es','T');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (5,'tutor2','Hola.123','Oscar','Ramirez','Montes','OOAC000225HMNLYRA4','1970-10-28','Pino Suarez 343','900-876-3444','tutor2@es.es','T');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (6,'estudiante1','Hola.123','Mariana','Garcia','Gutierrez','MOAC000225HMNLYRA4','2000-04-17','Sevilla 23','351-987-3422','estudiante1@es.es','E');
INSERT INTO `usuarios` (`idUsuario`,`usuario`,`contrasena`,`nombre`,`apellido_p`,`apellido_m`,`curp`,`fecha_nacimiento`,`domicilio`,`telefono`,`correo`,`tipo`) VALUES (7,'estudiante2','Hola.123','Omar','Plascencia','Ayala','POAC000225HMNLYRA4','1997-03-10','Rinconada 25','123-111-1111','estudiante2@es.es','E');

INSERT INTO `administradores` (`idAdministrador`,`idUsuario`) VALUES (1,1);

INSERT INTO `profesores` (`idProfesor`,`idUsuario`,`estatus`,`identificacion`) VALUES (1,2,'A',null);
INSERT INTO `profesores` (`idProfesor`,`idUsuario`,`estatus`,`identificacion`) VALUES (2,3,'A',null);

INSERT INTO `tutores` (`idTutor`,`idUsuario`,`identificacion`) VALUES (1,4,null);
INSERT INTO `tutores` (`idTutor`,`idUsuario`,`identificacion`) VALUES (2,5,null);

INSERT INTO `estudiantes` (`idEstudiante`,`idUsuario`,`idTutor`,`idTutor2`,`estatus`) VALUES (1,6,1,NULL,'A');
INSERT INTO `estudiantes` (`idEstudiante`,`idUsuario`,`idTutor`,`idTutor2`,`estatus`) VALUES (2,7,2,NULL,'A');

INSERT INTO `ciclos` (`idCiclo`,`nombre`,`fecha_inicio`,`fecha_final`) VALUES (1,'Ciclo 2023-2024','2023-09-01','2024-08-01');
INSERT INTO `ciclos` (`idCiclo`,`nombre`,`fecha_inicio`,`fecha_final`) VALUES (2,'Ciclo 2024-2025','2024-09-01','2025-08-01');

INSERT INTO `grupos` (`idGrupo`,`idProfesor`,`idCiclo`,`grado`,`grupo`) VALUES (1,1,1,4,'A');
INSERT INTO `grupos` (`idGrupo`,`idProfesor`,`idCiclo`,`grado`,`grupo`) VALUES (2,2,2,5,'B');
INSERT INTO `grupos` (`idGrupo`,`idProfesor`,`idCiclo`,`grado`,`grupo`) VALUES (3,1,2,6,'C');

INSERT INTO `detalleGrupos` (`idDetalleGrupo`,`idGrupo`,`idEstudiante`) VALUES (1,1,1);
INSERT INTO `detalleGrupos` (`idDetalleGrupo`,`idGrupo`,`idEstudiante`) VALUES (2,2,2);
INSERT INTO `detalleGrupos` (`idDetalleGrupo`,`idGrupo`,`idEstudiante`) VALUES (3,3,1);

INSERT INTO `cursos` (`idCurso`,`idGrupo`,`idMateria`) VALUES (1,1,1);
INSERT INTO `cursos` (`idCurso`,`idGrupo`,`idMateria`) VALUES (2,2,2);
INSERT INTO `cursos` (`idCurso`,`idGrupo`,`idMateria`) VALUES (3,1,2);
INSERT INTO `cursos` (`idCurso`,`idGrupo`,`idMateria`) VALUES (4,2,1);
INSERT INTO `cursos` (`idCurso`,`idGrupo`,`idMateria`) VALUES (5,3,3);

INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (2,1,1,2,7);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (3,2,2,1,9);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (4,2,2,2,7);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (5,1,3,1,9);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (6,1,3,2,6);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (7,2,4,1,10);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (8,2,4,2,9);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (21,2,4,4,9);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (24,2,2,5,10);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (25,1,1,3,7);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (28,1,1,1,10);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (29,2,4,3,10);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (30,1,5,1,10);
INSERT INTO `calificaciones` (`idCalificacion`,`idEstudiante`,`idCurso`,`mes`,`valor`) VALUES (31,2,2,3,10);
