from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from numpy.lib._datasource import Repository

from database import repository
from database import connection
from transform import Transform
from validate import Validator
from utils import leitor_xml
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

from sqlalchemy import select
from database.repository import Base
import database
import os.path
import base64
import binascii
import io
import utils
import xml.etree.ElementTree as ET


logger = utils.get_logger("gmail_extractor")

def oauth_to_service():
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    creds = None

    # tenta reutilizar token existente
    if os.path.exists("config/token.json"):
        creds = Credentials.from_authorized_user_file(
            "config/token.json",
            SCOPES
        )

    # se não existe token ou expirou
    if not creds or not creds.valid:

        # tenta renovar usando refresh token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            # primeiro login OAuth
            flow = InstalledAppFlow.from_client_secrets_file(
                "config/credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0,
                access_type="offline",
                prompt="consent"
            )

        # salva token para próximas execuções
        with open("config/token.json", "w") as token:
            token.write(creds.to_json())

    # conecta ao Gmail
    return build("gmail","v1",credentials=creds)

def get_messages(service):
    """ Adquiri mensagem atravéz do argumento service"""
    try:
        # busca últimos X emails
        results = service.users().messages().list(
            userId="me",
            maxResults=50,
            q="in:inbox has:attachment newer_than:30d"
        ).execute()
    except HttpError as e:
        logger.error(f"Falha ao buscar mensagem {e}")
    return results.get("messages",[])

def walk_parts(part):
    yield part

    for child in part.get("parts", []):
        yield from walk_parts(child)

def extract_xml():
    try:
        service = oauth_to_service()
    except Exception as e:
        logger.error("Erro ao iniciar o oauth google api tentando novamente após 1h" + {e})
        return

    for message in get_messages(service):
        try:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            # metadata = utils.get_metadata_gmail_msg(msg)

        except HttpError as e:
            logger.error(f"Falha ao buscar mensagem {message['id']}: {e}")
            continue

        for part in walk_parts(msg["payload"]):
            filename = part.get("filename")

            if not filename:
                continue

            if filename.lower().endswith(".xml"):
                try:
                    body = part.get("body", {})
                    if "data" in body:
                        file_bytes = base64.urlsafe_b64decode(body["data"])

                    else:
                        attachment_id = part["body"].get("attachmentId")
                        if not attachment_id:
                            continue
                        attachment = (service.users().messages().attachments().get(userId="me", messageId=message["id"],
                                                                                   id=attachment_id).execute())
                        file_bytes = base64.urlsafe_b64decode(attachment["data"])

                except (binascii.Error, ValueError) as e:
                    logger.error(f"Base64 inválido em {filename}: {e}")
                    continue

                except HttpError as e:
                    logger.error(f"Falha ao baixar anexo {filename}: {e}")
                    continue

                buffer = io.BytesIO(file_bytes)

                try:
                    logger.info(f"Extracting {filename}...")
                    yield leitor_xml(file=buffer)

                except ET.ParseError as e:
                    logger.error(f"Erro no ET.Parse {filename}: {e}")
                    continue

            elif filename.lower().endswith(".pdf"):
                ...


if __name__ == '__main__':
    try:
        validator = Validator()
        session = connection.get_session()
        repository.NotaFiscal.create_table(connection.engine)
        for dict_xml in extract_xml():
            result = validator.validate_dict_xml(data=dict_xml)
            if not result:
                logger.warning(f"Arquivo Ignorado devido ao erro anteriores. {dict_xml}")
                continue

            dict_format = Transform.transform_nfe(xml=dict_xml)

            existe = session.scalar(
                select(repository.NotaFiscal).where(
                    repository.NotaFiscal.chave == dict_format["chave"]
                )
            )
            if existe:
                logger.info("Nota já cadastrada no Sistema, Ignorando.")
                continue
            nota = repository.NotaFiscal(**dict_format)
            session.add(nota)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
