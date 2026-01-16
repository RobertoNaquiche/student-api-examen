import json
from datetime import datetime
from app import app, db, Estudiante
import os

def importar_desde_archivo():
    """Importa datos desde un archivo JSON"""
    
    # Ruta al archivo JSON
    ruta_json = r"C:\Users\LENOVO\Documents\M5_API_DEVELOPER_EXAMEN\estudiante.json"
    
    with app.app_context():
        try:
            # Leer el archivo JSON
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos_mongodb = json.load(f)
            
            print(f"📂 Leyendo archivo: {ruta_json}")
            print(f"📊 Encontrados {len(datos_mongodb)} estudiante\n")
            
            # Limpiar tabla existente (opcional - descomenta si quieres)
            # Estudiante.query.delete()
            # print("🗑️ Tabla limpiada")
            
            contador = 0
            for dato in datos_mongodb:
                try:
                    # Convertir fecha de MongoDB
                    fecha_str = dato["fecha"]["$date"]
                    fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                    
                    # Crear estudiante
                    estudiante = Estudiante(
                        nombre=dato["nombre"],
                        apellido=dato["apellido"],
                        nota=dato["nota"],
                        aprobado=dato["aprobado"],
                        fecha=fecha
                    )
                    
                    db.session.add(estudiante)
                    contador += 1
                    print(f"  ✓ {dato['nombre']} {dato['apellido']}")
                    
                except KeyError as e:
                    print(f"  ✗ Error en {dato.get('nombre', 'desconocido')}: Campo faltante {e}")
                except Exception as e:
                    print(f"  ✗ Error en {dato.get('nombre', 'desconocido')}: {e}")
            
            db.session.commit()
            print(f"\n✅ {contador} estudiantes importados correctamente")
            
            # Mostrar estadísticas
            print("\n📈 Estadísticas finales:")
            total = Estudiante.query.count()
            aprobados = Estudiante.query.filter_by(aprobado=True).count()
            print(f"   Total: {total} estudiantes")
            print(f"   Aprobados: {aprobados} ({aprobados/total*100:.1f}%)")
            print(f"   Reprobados: {total - aprobados} ({(total-aprobados)/total*100:.1f}%)")
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {ruta_json}")
            print("Creando datos de ejemplo...")
            crear_datos_ejemplo()
        except json.JSONDecodeError:
            print(f"❌ Error al leer JSON: {ruta_json}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

def crear_datos_ejemplo():
    """Crea datos de ejemplo si no hay archivo"""
    with app.app_context():
        estudiantes = [
            ("Juan", "Pérez", 7.5),
            ("María", "López", 4.2),
            ("Carlos", "García", 8.9),
            ("Lucía", "Martínez", 9.1),
            ("Sofía", "Fernández", 5.0)
        ]
        
        for nombre, apellido, nota in estudiantes:
            estudiante = Estudiante(
                nombre=nombre,
                apellido=apellido,
                nota=nota,
                aprobado=nota >= 6.0
            )
            db.session.add(estudiante)
            print(f"  ✓ {nombre} {apellido} - Nota: {nota}")
        
        db.session.commit()
        print(f"\n✅ {len(estudiantes)} estudiantes de ejemplo creados")

if __name__ == "__main__":
    importar_desde_archivo()