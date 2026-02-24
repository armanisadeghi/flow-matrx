from dotenv import load_dotenv

load_dotenv()

from matrx_orm import register_database_from_env

register_database_from_env(
    name="flow_matrx",
    env_prefix="DB",
    additional_schemas=[],
)
