import os
import json
from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from google.protobuf.json_format import MessageToDict

# Configura tus variables
project_id = "xxxx"
location = "us"
processor_id = "xxxx"
file_path = "C:/Users/renee/OneDrive/Personal/eIntegrity-Documents/Test/pdf/W2_XL_input_clean_2950.pdf"  # Asegúrate de que este archivo exista
mime_type = "application/pdf"
field_mask = "text,entities,pages.pageNumber"
processor_version_id = "xxxxxxx"

def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> None:
    # Verificar si el archivo existe
    if not os.path.isfile(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return
    
    # Configuración de la opción del cliente para usar un endpoint específico.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    # Creación de un cliente para el servicio Document AI.
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if processor_version_id:
        # Construcción del nombre completo del recurso de la versión del procesador.
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # Construcción del nombre completo del recurso del procesador.
        name = client.processor_path(project_id, location, processor_id)

    # Leer el archivo en memoria.
    try:
        with open(file_path, "rb") as image:
            image_content = image.read()
    except PermissionError:
        print(f"Error: Permiso denegado al intentar leer el archivo {file_path}.")
        return

    # Cargar datos binarios.
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # Configuración de opciones adicionales de procesamiento (opcional).
    process_options = documentai.ProcessOptions(
        # Procesar solo páginas específicas.
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=[1]
        )
    )

    # Configuración de la solicitud de procesamiento.
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    # Ejecución de la solicitud de procesamiento.
    result = client.process_document(request=request)

    # Acceso al documento resultante.
    document = result.document

    # Imprimir el texto reconocido en el documento.
    print("The document contains the following text:")
    print(document.text)

    # Convertir el documento a un diccionario usando MessageToDict
    document_dict = MessageToDict(document._pb)

    # Preparar la ruta del archivo de salida
    output_dir = "C:/Users/renee/OneDrive/Personal/eIntegrity-Documents/"
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{base_filename}.json")

    # Guardar el documento resultante en un archivo JSON
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(document_dict, json_file, ensure_ascii=False, indent=4)

    print(f"Resultados guardados en {output_path}")

# Llamada a la función para probar el procesamiento del documento.
process_document_sample(project_id, location, processor_id, file_path, mime_type, field_mask, processor_version_id)
