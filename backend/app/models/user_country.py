from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


# Per-user allow-list of country codes (no rows and not admin/all-access = no access).
class UserCountry(Base):
    __tablename__ = "user_countries"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    country_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("countries.code"), primary_key=True
    )
