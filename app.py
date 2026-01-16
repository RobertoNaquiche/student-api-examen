from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Estudiante
from config import Config
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar base de datos
db.init_app(app)
migrate = Migrate(app, db)

# Crear tablas (en desarrollo)
with app.app_context():
    db.create_all()

# Middleware para logging
@app.before_request
def log_request_info():
    logger.info('Petición: %s %s', request.method, request.path)

# Ruta de prueba
@app.route('/')
def index():
    return jsonify({
        'mensaje': 'API de Gestión de Estudiantes',
        'endpoints': {
            'GET /estudiantes': 'Listar todos los estudiantes',
            'GET /estudiantes/<id>': 'Obtener un estudiante por ID',
            'POST /estudiantes': 'Crear nuevo estudiante',
            'PUT /estudiantes/<id>': 'Actualizar estudiante',
            'DELETE /estudiantes/<id>': 'Eliminar estudiante',
            'GET /estudiantes/buscar?nombre=X&apellido=Y': 'Buscar por nombre/apellido',
            'GET /estudiantes/buscar/<termino>': 'Buscar por término',
            'GET /estudiantes/aprobados': 'Listar estudiantes aprobados',
            'GET /estudiantes/reprobados': 'Listar estudiantes reprobados',
            'GET /estudiantes/estadisticas': 'Estadísticas académicas'
        }
    })

# 1. GET /estudiantes: Listar todos
@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    """Obtener todos los estudiantes"""
    try:
        estudiantes = Estudiante.query.all()
        return jsonify({
            'total': len(estudiantes),
            'estudiantes': [estudiante.to_dict() for estudiante in estudiantes]
        })
    except Exception as e:
        logger.error(f'Error al obtener estudiantes: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# 2. GET /estudiantes/<id>: Obtener por ID
@app.route('/estudiantes/<int:id>', methods=['GET'])
def get_estudiante(id):
    """Obtener un estudiante por ID"""
    try:
        estudiante = Estudiante.query.get_or_404(id)
        return jsonify(estudiante.to_dict())
    except Exception as e:
        logger.error(f'Error al obtener estudiante {id}: {e}')
        return jsonify({'error': 'Estudiante no encontrado'}), 404

# 3. POST /estudiantes: Crear nuevo
@app.route('/estudiantes', methods=['POST'])
def create_estudiante():
    """Crear un nuevo estudiante"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'nota']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Validar que nota sea número
        try:
            nota = float(data['nota'])
            if nota < 0 or nota > 10:
                return jsonify({'error': 'La nota debe estar entre 0 y 10'}), 400
        except ValueError:
            return jsonify({'error': 'La nota debe ser un número válido'}), 400
        
        # Crear estudiante
        estudiante = Estudiante(
            nombre=data['nombre'].strip(),
            apellido=data['apellido'].strip(),
            nota=nota,
            aprobado=nota >= 6.0
        )
        
        db.session.add(estudiante)
        db.session.commit()
        
        logger.info(f'Estudiante creado: {estudiante.id}')
        return jsonify({
            'mensaje': 'Estudiante creado exitosamente',
            'estudiante': estudiante.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al crear estudiante: {e}')
        return jsonify({'error': 'Error al crear estudiante'}), 500

# 4. PUT /estudiantes/<id>: Actualizar
@app.route('/estudiantes/<int:id>', methods=['PUT'])
def update_estudiante(id):
    """Actualizar un estudiante existente"""
    try:
        estudiante = Estudiante.query.get_or_404(id)
        data = request.get_json()
        
        cambios = False
        
        # Actualizar campos si están presentes
        if 'nombre' in data and data['nombre'].strip():
            estudiante.nombre = data['nombre'].strip()
            cambios = True
            
        if 'apellido' in data and data['apellido'].strip():
            estudiante.apellido = data['apellido'].strip()
            cambios = True
            
        if 'nota' in data:
            try:
                nota = float(data['nota'])
                if nota < 0 or nota > 10:
                    return jsonify({'error': 'La nota debe estar entre 0 y 10'}), 400
                estudiante.nota = nota
                estudiante.aprobado = nota >= 6.0
                cambios = True
            except ValueError:
                return jsonify({'error': 'La nota debe ser un número válido'}), 400
        
        if not cambios:
            return jsonify({'mensaje': 'No se realizaron cambios', 'estudiante': estudiante.to_dict()})
        
        db.session.commit()
        
        logger.info(f'Estudiante actualizado: {id}')
        return jsonify({
            'mensaje': 'Estudiante actualizado exitosamente',
            'estudiante': estudiante.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al actualizar estudiante {id}: {e}')
        return jsonify({'error': 'Error al actualizar estudiante'}), 500

# 5. DELETE /estudiantes/<id>: Eliminar
@app.route('/estudiantes/<int:id>', methods=['DELETE'])
def delete_estudiante(id):
    """Eliminar un estudiante"""
    try:
        estudiante = Estudiante.query.get_or_404(id)
        
        nombre_completo = f"{estudiante.nombre} {estudiante.apellido}"
        
        db.session.delete(estudiante)
        db.session.commit()
        
        logger.info(f'Estudiante eliminado: {id}')
        return jsonify({
            'mensaje': f'Estudiante "{nombre_completo}" eliminado correctamente',
            'id_eliminado': id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al eliminar estudiante {id}: {e}')
        return jsonify({'error': 'Error al eliminar estudiante'}), 500

# 6. GET /estudiantes/buscar: Búsqueda por nombre y apellido
@app.route('/estudiantes/buscar', methods=['GET'])
def buscar_estudiantes():
    """Buscar estudiantes por nombre y/o apellido (case-insensitive)"""
    try:
        nombre = request.args.get('nombre', '').strip()
        apellido = request.args.get('apellido', '').strip()
        
        # Iniciar consulta
        query = Estudiante.query
        
        # Filtrar por nombre si se proporciona
        if nombre:
            query = query.filter(Estudiante.nombre.ilike(f'%{nombre}%'))
        
        # Filtrar por apellido si se proporciona
        if apellido:
            query = query.filter(Estudiante.apellido.ilike(f'%{apellido}%'))
        
        # Si no hay parámetros, devolver todos
        if not nombre and not apellido:
            estudiantes = Estudiante.query.all()
        else:
            estudiantes = query.all()
        
        return jsonify({
            'busqueda': {
                'nombre': nombre if nombre else 'cualquiera',
                'apellido': apellido if apellido else 'cualquiera'
            },
            'total_resultados': len(estudiantes),
            'estudiantes': [estudiante.to_dict() for estudiante in estudiantes]
        })
        
    except Exception as e:
        logger.error(f'Error en búsqueda: {e}')
        return jsonify({'error': 'Error en la búsqueda'}), 500

# Búsqueda alternativa por término único
@app.route('/estudiantes/buscar/<string:termino>', methods=['GET'])
def buscar_estudiantes_termino(termino):
    """Buscar estudiantes por término en nombre o apellido"""
    try:
        termino = termino.strip()
        
        estudiantes = Estudiante.query.filter(
            db.or_(
                Estudiante.nombre.ilike(f'%{termino}%'),
                Estudiante.apellido.ilike(f'%{termino}%')
            )
        ).all()
        
        return jsonify({
            'termino_busqueda': termino,
            'total_resultados': len(estudiantes),
            'estudiantes': [estudiante.to_dict() for estudiante in estudiantes]
        })
        
    except Exception as e:
        logger.error(f'Error en búsqueda por término: {e}')
        return jsonify({'error': 'Error en la búsqueda'}), 500

# 7. GET /estudiantes/aprobados: Filtrar aprobados
@app.route('/estudiantes/aprobados', methods=['GET'])
def get_aprobados():
    """Obtener todos los estudiantes aprobados"""
    try:
        aprobados = Estudiante.query.filter_by(aprobado=True).all()
        
        total_aprobados = len(aprobados)
        total_estudiantes = Estudiante.query.count()
        
        return jsonify({
            'total_aprobados': total_aprobados,
            'total_estudiantes': total_estudiantes,
            'porcentaje_aprobacion': round((total_aprobados / total_estudiantes * 100), 2) if total_estudiantes > 0 else 0,
            'estudiantes': [estudiante.to_dict() for estudiante in aprobados]
        })
    except Exception as e:
        logger.error(f'Error al obtener aprobados: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# Endpoint adicional: reprobados
@app.route('/estudiantes/reprobados', methods=['GET'])
def get_reprobados():
    """Obtener todos los estudiantes reprobados"""
    try:
        reprobados = Estudiante.query.filter_by(aprobado=False).all()
        
        total_reprobados = len(reprobados)
        total_estudiantes = Estudiante.query.count()
        
        return jsonify({
            'total_reprobados': total_reprobados,
            'total_estudiantes': total_estudiantes,
            'porcentaje_reprobacion': round((total_reprobados / total_estudiantes * 100), 2) if total_estudiantes > 0 else 0,
            'estudiantes': [estudiante.to_dict() for estudiante in reprobados]
        })
    except Exception as e:
        logger.error(f'Error al obtener reprobados: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# Estadísticas de estudiantes
@app.route('/estudiantes/estadisticas', methods=['GET'])
def get_estadisticas():
    """Obtener estadísticas de los estudiantes"""
    try:
        total = Estudiante.query.count()
        aprobados = Estudiante.query.filter_by(aprobado=True).count()
        reprobados = Estudiante.query.filter_by(aprobado=False).count()
        
        # Calcular promedio de notas
        from sqlalchemy import func
        promedio = db.session.query(func.avg(Estudiante.nota)).scalar() or 0
        
        # Calcular nota más alta y más baja
        max_nota = db.session.query(func.max(Estudiante.nota)).scalar() or 0
        min_nota = db.session.query(func.min(Estudiante.nota)).scalar() or 0
        
        return jsonify({
            'total_estudiantes': total,
            'aprobados': aprobados,
            'reprobados': reprobados,
            'porcentaje_aprobacion': round((aprobados / total * 100), 2) if total > 0 else 0,
            'promedio_notas': round(promedio, 2),
            'nota_maxima': round(max_nota, 2),
            'nota_minima': round(min_nota, 2)
        })
    except Exception as e:
        logger.error(f'Error al obtener estadísticas: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método no permitido'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)