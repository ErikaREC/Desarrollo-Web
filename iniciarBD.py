from bd.estructura import Admin, Asunto, Municipio, Nivel, Turno, Alumno
import random
admin = Admin(usuario = 'Admin', nombre = 'el admin', contraseña = 'Winmex.1')
admin.create()

asunto = Asunto(nombre = 'inscribir')
asunto.create()
asunto = Asunto(nombre = 'dar de baja')
asunto.create()
asunto = Asunto(nombre = 'pago mantenimiento')
asunto.create()
asunto = Asunto(nombre = 'tramite administrativo')
asunto.create()

municipio = Municipio(nombre = 'Saltillo')
municipio.create()
municipio = Municipio(nombre = 'Parras de la Fuente')
municipio.create()
municipio = Municipio(nombre = 'Ramos Arizpe')
municipio.create()

nivel = Nivel(nombre = '1° de bachillerato')
nivel.create()
nivel = Nivel(nombre = '2° de bachillerato')
nivel.create()
nivel = Nivel(nombre = '3° de bachillerato')
nivel.create()
nivel = Nivel(nombre = '4° de bachillerato')
nivel.create()
nivel = Nivel(nombre = '5° de bachillerato')
nivel.create()
nivel = Nivel(nombre = '6° de bachillerato')
nivel.create()

