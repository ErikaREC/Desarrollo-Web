from bd.estructura import Turno
turnos = Turno.listar()
for turno in turnos:
    turno.delete()
