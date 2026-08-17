# utils/helpers.py
from bson import ObjectId

def convertir_objectid(documento):
    """
    Recorre recursivamente un diccionario o lista y convierte todos los ObjectId a string.
    """
    if isinstance(documento, list):
        return [convertir_objectid(item) for item in documento]
    if isinstance(documento, dict):
        resultado = {}
        for clave, valor in documento.items():
            if isinstance(valor, ObjectId):
                resultado[clave] = str(valor)
            elif isinstance(valor, (list, dict)):
                resultado[clave] = convertir_objectid(valor)
            else:
                resultado[clave] = valor
        return resultado
    return documento