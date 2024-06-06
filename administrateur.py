import sqlite3 as sql


class Administrator:
    def __init__(self, id, nom, prenom, email, mot_de_passe):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe

    def get_managers(self):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM managers")
        managers = cursor.fetchall()
        conn.close()
        return managers

    def add_manager(self, manager_details):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO managers (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)",
            (
                manager_details["nom"],
                manager_details["prenom"],
                manager_details["email"],
                manager_details["mot_de_passe"],
            ),
        )
        conn.commit()
        conn.close()

    def modify_manager(self, manager_id, manager_details):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE managers SET nom=?, prenom=?, email=?, mot_de_passe=? WHERE id=?",
            (
                manager_details["nom"],
                manager_details["prenom"],
                manager_details["email"],
                manager_details["mot_de_passe"],
                manager_id,
            ),
        )
        conn.commit()
        conn.close()

    def delete_manager(self, manager_id):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM managers WHERE id=?", (manager_id,))
        conn.commit()
        conn.close()
