from bd.estructura import Admin, Asunto, Municipio, Nivel, Turno, Alumno
import random

nombres = ['Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Elena', 'Jose', 'Laura']
apellidos_paterno = ['Perez', 'Lopez', 'Sanchez', 'Gomez', 'Rodriguez', 'Fernandez']
apellidos_materno = ['Garcia', 'Martinez', 'Hernandez', 'Gonzalez', 'Diaz', 'Ramirez']
curps = [
    'JUAP880101HDFRRL01', 'MARL900203MDFRRL02', 'CARS850104HDFRRL03',
    'ANAL930507MDFRRL04', 'LUIS950408HDFRRL05', 'ELER850209MDFRRL06',
    'JOSE960310HDFRRL07', 'LAUR970511MDFRRL08'
]

for i in range(len(nombres)):
    alumno = Alumno(
        curp=curps[i],
        nombre=nombres[i],
        paterno=random.choice(apellidos_paterno),
        materno=random.choice(apellidos_materno)
    )
    alumno.create()

municipios = Municipio.list_all()
niveles = Nivel.list_all()
asuntos = Asunto.list_all()
alumnos = Alumno.list_all()

estados = ['pendiente', 'resuelto']
telefonos = [
    '5551234567', '5559876543', '5555671234', '5552345678', '5556781234', 
    '5558765432', '5555432167', '5556785432', '5559871234', '5557654321'
]
celulares = [
    '5552345678', '5558765432', '5556782345', '5553456789', '5559876543', 
    '5554321987', '5556789123', '5555432768', '5556781234', '5558761234'
]
correos = [
    'test1@example.com', 'test2@example.com', 'test3@example.com', 'test4@example.com',
    'test5@example.com', 'test6@example.com', 'test7@example.com', 'test8@example.com',
    'test9@example.com', 'test10@example.com'
]
nombres = [
    'Juan Perez', 'Maria Lopez', 'Carlos Sanchez', 'Ana Gomez', 'Luis Rodriguez', 
    'Elena Fernandez', 'Jose Gonzalez', 'Laura Ramirez', 'Miguel Torres', 'Carmen Reyes'
]


for municipio in municipios:
    for nivel in niveles:
        for asunto in asuntos:
            for estado in estados:
                for i in range(random.randint(1, 4)):  # Crear 10 turnos por combinación
                    turno = Turno(
                        municipio_id=municipio.id,
                        nombre=random.choice(nombres),
                        telefono=random.choice(telefonos),
                        celular=random.choice(celulares),
                        correo=random.choice(correos),
                        estado=estado,
                        asunto_id=asunto.id,
                        nivel_id=nivel.id,
                        alumno_curp=random.choice(alumnos).curp
                    )
                    turno.create()