from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

Path("data").mkdir(exist_ok=True)

DATABASE_URL = "sqlite:///data/chatbot_memory.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=utc_now)


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=utc_now)


def migrate_conversations_table():
    with engine.begin() as conn:
        columns = conn.execute(text("PRAGMA table_info(conversations)")).mappings().all()

        if not columns:
            return

        primary_key_columns = [column["name"] for column in columns if column["pk"]]

        if primary_key_columns == ["id"]:
            return

        conn.execute(text("DROP INDEX IF EXISTS ix_conversations_id"))
        conn.execute(text("DROP INDEX IF EXISTS ix_conversations_thread_id"))
        conn.execute(text("ALTER TABLE conversations RENAME TO conversations_old"))

        Conversation.__table__.create(bind=conn)

        conn.execute(
            text(
                """
                INSERT INTO conversations (thread_id, title, created_at, updated_at)
                SELECT
                    thread_id,
                    COALESCE(title, 'New Chat'),
                    created_at,
                    updated_at
                FROM conversations_old
                WHERE thread_id IS NOT NULL AND thread_id != ''
                GROUP BY thread_id
                """
            )
        )

        conn.execute(text("DROP TABLE conversations_old"))


def init_db():
    migrate_conversations_table()
    Base.metadata.create_all(bind=engine)


def create_or_update_conversation(thread_id: str, first_message: str | None = None):
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation).filter(Conversation.thread_id == thread_id).first()
        )

        if not conversation:
            title = "New Chat"

            if first_message:
                title = first_message.strip()[:40]
                if len(first_message.strip()) > 40:
                    title += "..."

            conversation = Conversation(
                thread_id=thread_id,
                title=title,
                created_at=utc_now(),
                updated_at=utc_now(),
            )

            db.add(conversation)

        else:
            conversation.updated_at = utc_now()

        db.commit()

    finally:
        db.close()


def list_conversations():
    db = SessionLocal()

    try:
        return db.query(Conversation).order_by(Conversation.updated_at.desc()).all()

    finally:
        db.close()


def save_chat_message(thread_id: str, role: str, content: str):
    db = SessionLocal()

    try:
        msg = ChatMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            created_at=utc_now(),
        )

        db.add(msg)

        conversation = (
            db.query(Conversation).filter(Conversation.thread_id == thread_id).first()
        )

        if conversation:
            conversation.updated_at = utc_now()

        db.commit()

    finally:
        db.close()


def get_chat_history(thread_id: str):
    db = SessionLocal()

    try:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    finally:
        db.close()


def save_memory(thread_id: str, memory: str):
    db = SessionLocal()

    try:
        item = LongTermMemory(
            thread_id=thread_id,
            memory=memory,
            created_at=utc_now(),
        )

        db.add(item)
        db.commit()

        return "Memory saved successfully."

    finally:
        db.close()


def search_memory(thread_id: str, query: str):
    db = SessionLocal()

    try:
        memories = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.thread_id == thread_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(20)
            .all()
        )

        if not memories:
            return "No saved memory found."

        return "\n".join([f"- {m.memory}" for m in memories])

    finally:
        db.close()
