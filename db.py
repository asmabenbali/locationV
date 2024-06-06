import sqlite3 as sql

connexion = sql.connect("loc.db")
cursor = connexion.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS client (
                id_client INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT NOT NULL,
                telephone TEXT NOT NULL)""")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS voiture (
                id_voiture INTEGER PRIMARY KEY AUTOINCREMENT,
                marque TEXT NOT NULL,
                modele TEXT NOT NULL,
                immatriculation TEXT NOT NULL,
                categorie TEXT NOT NULL,
                prix TEXT NOT NULL,
                disponibilite TEXT NOT NULL,
                image_url TEXT)"""
)

cursor.execute("""CREATE TABLE IF NOT EXISTS manager (
   idManager  INTEGER PRIMARY KEY AUTOINCREMENT,
   nom TEXT NOT NULL,
   prenom TEXT NOT NULL,
   email TEXT NOT NULL,
   mot_de_passe TEXT NOT NULL,
   id_client INTEGER,
   FOREIGN KEY (id_client) REFERENCES client (id_client)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS administrateur (
               idAdministrateur  INTEGER PRIMARY KEY AUTOINCREMENT,
               nom TEXT NOT NULL,
               prenom TEXT NOT NULL,
               email TEXT NOT NULL,
               mot_de_passe TEXT  NOT NULL) """)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS reservation (
    id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
    id_client INTEGER,
    id_voiture INTEGER,
    status TEXT NOT NULL DEFAULT 'Pending',
    id_manager INTEGER,
    FOREIGN KEY (id_client) REFERENCES client (id_client),
    FOREIGN KEY (id_voiture) REFERENCES voiture (id_voiture),
    FOREIGN KEY (id_manager) REFERENCES manager (idManager)
)"""
)


cars_data = [
    (
        "Toyota",
        "Corolla",
        "1234 AB 56",
        "Compacte",
        "25000",
        "Disponible",
        "/static/photo/image2.png",
    ),
    (
        "Honda",
        "Civic",
        "5678 CD 90",
        "Compacte",
        "27000",
        "Disponible",
        "/static/photo/image3.png",
    ),
    (
        "Ford",
        "Focus",
        "2468 EF 12",
        "Compacte",
        "23000",
        "Non disponible",
        "/static/photo/pppp.png",
    ),
    (
        "BMW",
        "X5",
        "1357 GH 34",
        "SUV",
        "50000",
        "Disponible",
        "/static/photo/image5.png",
    ),
    (
        "Mercedes",
        "C-Class",
        "9876 IJ 78",
        "Berline",
        "40000",
        "Non disponible",
        "/static/photo/image6.png",
    ),
     (
        "Dacia",
        "Logan",
        "7898 KI 13",
        "Compacte",
        "20000",
        "Disponible",
        "/static/photo/image1.png",
    ),
]

cursor.executemany(
    "INSERT INTO voiture (marque, modele, immatriculation, categorie, prix, disponibilite, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
    cars_data,
)
                          #managerrrs just login 
users = [
   
        ("alia","alaoui","alia@gmail.com","22"),

]
      
cursor.executemany(
    "INSERT INTO manager (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)", users
)
                                      #admiiiin
admins = [
    ("Admin", "Admin", "admin@example.com", "admin123"),
    ("Super", "User", "superuser@example.com", "superuser123"),
]

cursor.executemany(
    "INSERT INTO administrateur (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)", admins
)

                                     #POUR RESERVER CAAAAR
users = [
   
    ("asma","benbali","aa@gmail.com","1234"),
]

# Insert the users into the client table
cursor.executemany(
    "INSERT INTO client (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)", users
)

# Commit changes and close the connection
connexion.commit()
connexion.close()
