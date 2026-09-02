"""
Seeds the 3 "Fresh Fork Restaurant Group" locations this demo is built
around, plus one gerente account per restaurant, so there's something to log
into immediately without registering by hand. Safe to re-run — skips a
restaurant/user that already exists.

    python -m app.seed_demo_data
"""

from app.database import SessionLocal
from app.models import Restaurante, Usuario
from app.security.passwords import hash_password

RESTAURANTES = ["fresh-fork-downtown", "fresh-fork-uptown", "fresh-fork-riverside"]
DEMO_PASSWORD = "Segura123!"


def seed() -> None:
    db = SessionLocal()
    try:
        for nombre in RESTAURANTES:
            restaurante = db.query(Restaurante).filter(Restaurante.nombre == nombre).first()
            if restaurante is None:
                restaurante = Restaurante(nombre=nombre)
                db.add(restaurante)
                db.flush()

            email = f"gerente@{nombre}.com"
            if db.query(Usuario).filter(Usuario.email == email).first() is None:
                db.add(
                    Usuario(
                        email=email,
                        password_hash=hash_password(DEMO_PASSWORD),
                        rol="gerente",
                        restaurante_id=restaurante.id,
                    )
                )
                print(f"Created {email} / {DEMO_PASSWORD} for {nombre}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed complete: 3 restaurants, 1 gerente each.")
