# modulo_gestion_qr/utils/entrega_docs.py
from __future__ import annotations

import os
import base64
from io import BytesIO
from typing import Optional, Iterable

from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings

# --- ReportLab ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# --- SendGrid Web API ---
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Attachment, FileContent, FileName, FileType, Disposition

# --- boto3 (opcional; lo usamos sólo si está disponible) ---
try:
    import boto3
except Exception:
    boto3 = None


# ========= Helpers de imágenes =========

def _debug(msg: str):
    # Cambia a logging si prefieres, pero así queda alineado con tus logs actuales
    print(f"[PDF] {msg}")

def _read_bytes_from_field_storage(path_or_field) -> Optional[bytes]:
    """
    Intenta leer bytes usando el storage propio del ImageFieldFile, si aplica.
    """
    try:
        if hasattr(path_or_field, "storage") and hasattr(path_or_field, "name") and path_or_field.name:
            name = path_or_field.name
            _debug(f"(field.storage) Abriendo: {name}")
            with path_or_field.storage.open(name, "rb") as f:
                return f.read()
    except Exception as e:
        _debug(f"(field.storage) Error '{getattr(path_or_field, 'name', None) or path_or_field}': {e}")
    return None

def _read_bytes_from_default_storage(name: str) -> Optional[bytes]:
    """
    Intenta leer bytes usando default_storage (FileSystemStorage o S3Boto3Storage si lo configuraste).
    """
    try:
        if not name:
            return None
        _debug(f"(default_storage) Abriendo: {name}")
        with default_storage.open(name, "rb") as f:
            return f.read()
    except Exception as e:
        _debug(f"(default_storage) Error '{name}': {e}")
    return None

def _read_bytes_from_local_path(name: str) -> Optional[bytes]:
    """
    Fallback final: intenta resolver una ruta local relativa a BASE_DIR.
    Útil en desarrollo si los archivos están dentro del repo.
    """
    try:
        base_dir = getattr(settings, "BASE_DIR", ".")
        local_path = os.path.join(str(base_dir), name.replace("/", os.sep))
        _debug(f"(local) Abriendo: {local_path}")
        with open(local_path, "rb") as f:
            return f.read()
    except Exception as e:
        _debug(f"(local) Error '{local_path}': {e}")
    return None

def _read_bytes_from_s3(name: str) -> Optional[bytes]:
    """
    Si los dos métodos anteriores fallan y tienes credenciales S3,
    descarga directamente del bucket usando boto3.get_object.
    Esto resuelve el caso en el que default_storage sea FileSystemStorage
    pero los archivos estén en S3 (tu caso actual).
    """
    try:
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
        region = getattr(settings, "AWS_S3_REGION_NAME", None)
        if not bucket or boto3 is None:
            return None

        # Normalizamos la key
        key = name.lstrip("/")
        _debug(f"(s3.get_object) Bucket={bucket}, Key={key}")
        client = boto3.client("s3", region_name=region) if region else boto3.client("s3")
        resp = client.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()
    except Exception as e:
        _debug(f"(s3.get_object) Error '{name}': {e}")
    return None

def _image_reader_from_anywhere(path_or_field) -> Optional[ImageReader]:
    """
    Acepta:
      - ImageFieldFile (ej: solicitud.logo, entrega.foto, entrega.firma)
      - str con la ruta/key (ej: 'entregas/fotos/xxx.png')

    Estrategia de lectura (en este orden):
      1) storage del field (si existe)
      2) default_storage.open(...)
      3) descarga directa desde S3 (boto3)
      4) ruta local relativa a BASE_DIR

    Retorna ImageReader o None si no existe.
    """
    # 1) field.storage
    data = _read_bytes_from_field_storage(path_or_field)
    if data:
        return ImageReader(BytesIO(data))

    # Normaliza a nombre
    if hasattr(path_or_field, "name"):
        name = path_or_field.name or ""
    else:
        name = str(path_or_field or "").strip()

    if not name:
        return None

    # 2) default_storage
    data = _read_bytes_from_default_storage(name)
    if data:
        return ImageReader(BytesIO(data))

    # 3) S3 directo
    data = _read_bytes_from_s3(name)
    if data:
        return ImageReader(BytesIO(data))

    # 4) local fallback
    data = _read_bytes_from_local_path(name)
    if data:
        return ImageReader(BytesIO(data))

    return None


def _scale_to_fit(w: float, h: float, max_w: float, max_h: float) -> tuple[float, float]:
    r = min(max_w / float(w), max_h / float(h))
    return (w * r, h * r)


# ========= PDF =========

def generar_pdf_entrega(entrega) -> tuple[str, bytes]:
    """
    Genera el PDF con:
      - Logo arriba izquierda (solicitud.logo)
      - Fecha/hora (fecha_entrega) arriba derecha
      - Título centrado 'Prueba de entrega' en negrita
      - Nombre, correo, teléfono
      - Foto y firma (si existen)

    Retorna: (filename, pdf_bytes)
    """
    W, H = A4
    margin = 40
    y_top = H - margin

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # Logo (si existe)
    logo_field = getattr(entrega.solicitud, "logo", None)
    if logo_field:
        logo_reader = _image_reader_from_anywhere(logo_field)
        if logo_reader:
            try:
                lw, lh = logo_reader.getSize()
                nw, nh = _scale_to_fit(lw, lh, 120, 60)
                c.drawImage(logo_reader, margin, y_top - nh, width=nw, height=nh,
                            preserveAspectRatio=True, mask='auto')
            except Exception as e:
                _debug(f"Error dibujando logo: {e}")
        else:
            _debug("No se pudo resolver el logo desde ninguna fuente.")
    else:
        _debug("Solicitud sin logo; se omite.")

    # Fecha/hora (local)
    fecha = entrega.fecha_entrega or timezone.now()
    fecha_str = timezone.localtime(fecha).strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 10)
    txt_w = c.stringWidth(fecha_str, "Helvetica", 10)
    c.drawString(W - margin - txt_w, y_top - 12, fecha_str)

    # Título centrado
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, y_top - 80, "Prueba de entrega")

    # Datos
    y = y_top - 120

    def label_val(lbl, val):
        nonlocal y
        c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, f"{lbl}:")
        c.setFont("Helvetica", 12);      c.drawString(margin + 100, y, val or "")
        y -= 18

    label_val("Nombre", getattr(entrega, "nombre", "") or "")
    label_val("Correo", getattr(entrega, "correo", "") or "")
    label_val("Teléfono", getattr(entrega, "telefono", "") or "")
    y -= 16

    # Foto
    foto_field = getattr(entrega, "foto", None)
    if foto_field:
        foto_reader = _image_reader_from_anywhere(foto_field)
        if foto_reader:
            try:
                fw, fh = foto_reader.getSize()
                max_w, max_h = (W - 2 * margin), 280
                dw, dh = _scale_to_fit(fw, fh, max_w, max_h)
                if y - dh < 120:
                    c.showPage(); y = H - margin
                c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, "Foto de evidencia:")
                y -= 18
                c.drawImage(foto_reader, margin, y - dh, width=dw, height=dh,
                            preserveAspectRatio=True, mask='auto')
                y -= (dh + 24)
            except Exception as e:
                _debug(f"Error dibujando foto: {e}")
        else:
            _debug("No se pudo resolver la foto desde ninguna fuente.")
    else:
        _debug("Entrega sin foto; se omite.")

    # Firma
    firma_field = getattr(entrega, "firma", None)
    if firma_field:
        firma_reader = _image_reader_from_anywhere(firma_field)
        if firma_reader:
            try:
                fw, fh = firma_reader.getSize()
                max_w, max_h = (W - 2 * margin), 180
                dw, dh = _scale_to_fit(fw, fh, max_w, max_h)
                if y - dh < 80:
                    c.showPage(); y = H - margin
                c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, "Firma:")
                y -= 18
                c.drawImage(firma_reader, margin, y - dh, width=dw, height=dh,
                            preserveAspectRatio=True, mask='auto')
                y -= (dh + 12)
            except Exception as e:
                _debug(f"Error dibujando firma: {e}")
        else:
            _debug("No se pudo resolver la firma desde ninguna fuente.")
    else:
        _debug("Entrega sin firma; se omite.")

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()

    filename = f"prueba_entrega_{entrega.serial.serial}.pdf"
    return filename, pdf_bytes


# ========= EMAIL (SendGrid Web API) =========

def _sendgrid_send_email_with_pdf(*, to_email: str, subject: str, body: str,
                                  pdf_filename: str, pdf_bytes: bytes,
                                  from_email: Optional[str] = None,
                                  reply_to: Optional[str] = None,
                                  cc: Optional[Iterable[str]] = None):
    """
    Envía correo vía SendGrid Web API con un adjunto PDF en memoria.
    Si no hay SENDGRID_API_KEY, guarda el PDF en MEDIA_ROOT/tmp y no lanza excepción (modo dev).
    """
    api_key = os.environ.get("SENDGRID_API_KEY")
    sender = from_email or os.environ.get("DEFAULT_FROM_EMAIL", "cintainteligente@gmail.com")

    if not api_key:
        # --- Modo desarrollo: no envía, solo guarda el PDF para inspección ---
        print("[DEV] SENDGRID_API_KEY no configurada. No se enviará correo.")
        tmp_dir = os.path.join(getattr(settings, "MEDIA_ROOT", "."), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, pdf_filename)
        with open(tmp_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"[DEV] PDF guardado en: {tmp_path}")
        return

    message = Mail(
        from_email=Email(sender),
        to_emails=[To(to_email)],
        subject=subject,
        plain_text_content=body,
    )
    if reply_to:
        message.reply_to = Email(reply_to)
    if cc:
        message.add_cc([To(addr) for addr in cc])

    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    attachment = Attachment(
        FileContent(b64_pdf),
        FileName(pdf_filename),
        FileType("application/pdf"),
        Disposition("attachment"),
    )
    message.attachment = attachment

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    print(f"📤 SendGrid status: {response.status_code} — {response.body.decode() if response.body else 'OK'}")


def enviar_correo_entrega_sendgrid(entrega, *, from_email: Optional[str] = None, cc_usuario: bool = False):
    """
    Genera el PDF y lo envía al correo de la Solicitud.
    - Asunto: 'notificacion prueba de entrega {serial}'
    - Body:   'Confirmación de recepción; adjunto encontrará el comprobante de entrega relacionado'
    - CC opcional al correo digitado por el usuario (entrega.correo)
    """
    subject = f"notificacion prueba de entrega {entrega.serial.serial}"
    body = "Confirmación de recepción; adjunto encontrará el comprobante de entrega relacionado"

    filename, pdf_bytes = generar_pdf_entrega(entrega)
    cc_list = [entrega.correo] if (cc_usuario and getattr(entrega, "correo", None)) else None

    _sendgrid_send_email_with_pdf(
        to_email=entrega.solicitud.correo,
        subject=subject,
        body=body,
        pdf_filename=filename,
        pdf_bytes=pdf_bytes,
        from_email=from_email or "cintainteligente@gmail.com",
        reply_to=from_email or "cintainteligente@gmail.com",
        cc=cc_list,
    )
