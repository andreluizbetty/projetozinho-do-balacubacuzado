from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    numero: Mapped[str] = mapped_column(String(50))
    serie: Mapped[str] = mapped_column(String(10))
    chave: Mapped[str] = mapped_column(String(44), unique=True)

    data_emissao: Mapped[str] = mapped_column(String(30))
    tipo: Mapped[int] = mapped_column(Integer)

    cnpj_emitente: Mapped[str] = mapped_column(String(14))
    razao_social_emitente: Mapped[str] = mapped_column(String(200))

    cnpj_destinatario: Mapped[str] = mapped_column(String(14))
    razao_social_destinatario: Mapped[str] = mapped_column(String(200))

    valor_produtos: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_frete: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_seguro: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_icms: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_ipi: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_pis: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_cofins: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    protocolo: Mapped[str] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer)
    descricao_status: Mapped[str] = mapped_column(String(200))

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    @classmethod
    def create_table(cls, engine):
        cls.metadata.create_all(engine)