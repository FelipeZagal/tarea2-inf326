"""Genera un certificado autofirmado (cert.pem + key.pem) en la carpeta certs/.

Uso: python gen_cert.py
"""
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CERTS_DIR = Path(__file__).parent / "certs"
CERTS_DIR.mkdir(exist_ok=True)

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
nombre = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "INF326 Tarea 2"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])
ahora = datetime.datetime.now(datetime.timezone.utc)
cert = (
    x509.CertificateBuilder()
    .subject_name(nombre)
    .issuer_name(nombre)  # autofirmado: emisor = sujeto
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(ahora)
    .not_valid_after(ahora + datetime.timedelta(days=365))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]),
        critical=False,
    )
    .sign(key, hashes.SHA256())
)

(CERTS_DIR / "key.pem").write_bytes(
    key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
)
(CERTS_DIR / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
print("Certificados creados en", CERTS_DIR)
