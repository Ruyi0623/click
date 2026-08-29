"""Add WeChat login fields to users

Revision ID: a1b2c3d4e5f6
Revises: c253d2c89570
Create Date: 2026-06-06 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c253d2c89570'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加微信登录相关字段
    op.add_column('users', sa.Column('wx_openid', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=100), nullable=True))

    # 添加唯一索引
    op.create_index(op.f('ix_users_wx_openid'), 'users', ['wx_openid'], unique=True)
    op.create_unique_constraint(None, 'users', ['username'])
    op.create_unique_constraint(None, 'users', ['email'])

    # phone 字段改为可空（微信用户可能没有手机号）
    op.alter_column('users', 'phone', existing_type=sa.String(length=20), nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'phone', existing_type=sa.String(length=20), nullable=False)
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_index(op.f('ix_users_wx_openid'), table_name='users')
    op.drop_column('users', 'email')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'username')
    op.drop_column('users', 'wx_openid')
