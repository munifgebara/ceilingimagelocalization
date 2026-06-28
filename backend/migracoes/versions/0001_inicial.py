"""Esquema inicial: extensoes, tabelas (local, planta, foto) e indices.

Revision ID: 0001_inicial
Revises:
Create Date: 2026-06-28
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_inicial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Dimensao dos embeddings (deve bater com configuracao.dimensao_embedding).
DIM = 512


def upgrade() -> None:
    # Extensoes necessarias.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS cube;")
    op.execute("CREATE EXTENSION IF NOT EXISTS earthdistance;")

    op.execute(
        """
        CREATE TABLE local (
            id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            nome         varchar(200) NOT NULL,
            descricao    text,
            criado_em    timestamptz NOT NULL DEFAULT now()
        );
        """
    )

    op.execute(
        """
        CREATE TABLE planta (
            id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            local_id               uuid NOT NULL REFERENCES local(id) ON DELETE CASCADE,
            nome                   varchar(200) NOT NULL DEFAULT 'Pavimento',
            svg                    text NOT NULL,
            largura                double precision,
            altura                 double precision,
            escala_m_por_unidade   double precision,
            criado_em              timestamptz NOT NULL DEFAULT now()
        );
        """
    )

    op.execute(
        f"""
        CREATE TABLE foto (
            id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            local_id      uuid NOT NULL REFERENCES local(id) ON DELETE CASCADE,
            planta_id     uuid REFERENCES planta(id) ON DELETE SET NULL,
            imagem_url    text,
            latitude      double precision,
            longitude     double precision,
            gps_precisao  double precision,
            plan_x        double precision,
            plan_y        double precision,
            embedding     vector({DIM}),
            tipo          varchar(20) NOT NULL DEFAULT 'mapeamento',
            criado_em     timestamptz NOT NULL DEFAULT now()
        );
        """
    )

    # Indice geografico (filtro por raio de GPS) usando earthdistance/cube.
    op.execute("CREATE INDEX idx_foto_geo ON foto USING gist (ll_to_earth(latitude, longitude));")

    # Indice de similaridade de embeddings (pgvector, distancia de cosseno).
    op.execute("CREATE INDEX idx_foto_embedding ON foto USING hnsw (embedding vector_cosine_ops);")

    op.execute("CREATE INDEX idx_foto_local_tipo ON foto (local_id, tipo);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS foto;")
    op.execute("DROP TABLE IF EXISTS planta;")
    op.execute("DROP TABLE IF EXISTS local;")
