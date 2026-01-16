from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Estudiante(db.Model):
    """Modelo de Estudiante"""
    __tablename__ = 'estudiantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    aprobado = db.Column(db.Boolean, default=False)
    nota = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'aprobado': self.aprobado,
            'nota': self.nota,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    def __repr__(self):
        return f'<Estudiante {self.nombre} {self.apellido}>'    