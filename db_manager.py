import os
import logging
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestore della connessione al database PostgreSQL e delle operazioni CRUD per il bot Calvenzano.
    Utilizza connection pooling per una gestione efficiente delle connessioni multiple.
    """
    
    def __init__(self, database_url=None):
        """
        Inizializza il connection pool per PostgreSQL.
        
        Args:
            database_url (str, optional): URL di connessione al database PostgreSQL.
                                        Se non specificato, viene utilizzata la variabile d'ambiente DATABASE_URL.
        """
        # Usa DATABASE_URL dall'ambiente se non fornito esplicitamente
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            logger.error("DATABASE_URL non configurato. Impossibile connettersi al database.")
            raise ValueError("URL del database non specificato")
        
        # Crea un connection pool
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.database_url
            )
            logger.info("Connection pool PostgreSQL inizializzato con successo")
            
            # Crea la tabella users se non esiste
            self._create_tables()
            
        except Exception as e:
            logger.error(f"Errore nella creazione del connection pool: {e}")
            raise
    
    def _create_tables(self):
        """Crea la tabella utenti se non esiste."""
        create_users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            address VARCHAR(255),
            notification_time TIME DEFAULT '20:00',
            notifications_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_users_table_query)
                conn.commit()
                logger.info("Tabella 'users' verificata/creata con successo")
    
    def _get_connection(self):
        """
        Ottiene una connessione dal pool.
        
        Returns:
            Connection: Una connessione al database dal pool.
        """
        conn = self.connection_pool.getconn()
        return conn
    
    def _return_connection(self, conn):
        """
        Restituisce una connessione al pool.
        
        Args:
            conn (Connection): La connessione da restituire al pool.
        """
        self.connection_pool.putconn(conn)
    
    def get_user(self, user_id):
        """
        Recupera i dati di un utente dal database.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            
        Returns:
            dict: Dati dell'utente o None se non trovato.
        """
        query = "SELECT * FROM users WHERE user_id = %s"
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    user_data = dict(zip(columns, result))
                    # Converti il time in stringa HH:MM per compatibilità
                    if user_data.get('notification_time'):
                        user_data['notification_time'] = user_data['notification_time'].strftime('%H:%M')
                    return user_data
                return None
        finally:
            self._return_connection(conn)
    
    def create_user(self, user_id, username=None, first_name=None, last_name=None):
        """
        Crea un nuovo utente nel database.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            username (str, optional): Username Telegram.
            first_name (str, optional): Nome dell'utente.
            last_name (str, optional): Cognome dell'utente.
            
        Returns:
            bool: True se l'utente è stato creato con successo.
        """
        query = """
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
        RETURNING user_id
        """
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, username, first_name, last_name))
                result = cursor.fetchone()
                conn.commit()
                return result is not None
        finally:
            self._return_connection(conn)
    
    def update_user(self, user_id, **kwargs):
        """
        Aggiorna i dati di un utente.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            **kwargs: Coppie chiave-valore dei campi da aggiornare.
            
        Returns:
            bool: True se l'aggiornamento è avvenuto con successo.
        """
        # Costruisci la query di aggiornamento in modo dinamico
        fields = []
        values = []
        
        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)
        
        # Aggiungi sempre updated_at
        fields.append("updated_at = NOW()")
        
        # Aggiungi l'ID utente alla lista dei valori
        values.append(user_id)
        
        query = f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE user_id = %s
        """
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                updated = cursor.rowcount > 0
                conn.commit()
                return updated
        finally:
            self._return_connection(conn)
    
    def set_address(self, user_id, address):
        """
        Imposta l'indirizzo di un utente.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            address (str): Indirizzo dell'utente.
            
        Returns:
            bool: True se l'indirizzo è stato aggiornato con successo.
        """
        return self.update_user(user_id, address=address)
    
    def set_notification_time(self, user_id, notification_time):
        """
        Imposta l'orario di notifica di un utente.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            notification_time (str): Orario di notifica nel formato HH:MM.
            
        Returns:
            bool: True se l'orario è stato aggiornato con successo.
        """
        return self.update_user(user_id, notification_time=notification_time)
    
    def set_notifications_enabled(self, user_id, enabled):
        """
        Abilita o disabilita le notifiche per un utente.
        
        Args:
            user_id (int): ID Telegram dell'utente.
            enabled (bool): True per abilitare, False per disabilitare.
            
        Returns:
            bool: True se lo stato delle notifiche è stato aggiornato con successo.
        """
        return self.update_user(user_id, notifications_enabled=enabled)
    
    def get_all_users_for_notification(self):
        """
        Recupera tutti gli utenti con notifiche abilitate.
        
        Returns:
            list: Lista di dizionari contenenti i dati degli utenti.
        """
        query = "SELECT * FROM users WHERE notifications_enabled = TRUE"
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
                if results:
                    columns = [desc[0] for desc in cursor.description]
                    users = []
                    for result in results:
                        user_data = dict(zip(columns, result))
                        # Converti il time in stringa HH:MM per compatibilità
                        if user_data.get('notification_time'):
                            user_data['notification_time'] = user_data['notification_time'].strftime('%H:%M')
                        users.append(user_data)
                    return users
                return []
        finally:
            self._return_connection(conn)
    
    def close(self):
        """Chiude il connection pool."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()
            logger.info("Connection pool PostgreSQL chiuso")

# Esempio di utilizzo
if __name__ == "__main__":
    # Test di funzionamento
    db = DatabaseManager()
    
    # Crea un utente di test
    test_user_id = 12345
    db.create_user(test_user_id, "test_user", "Test", "User")
    
    # Aggiorna alcuni dati
    db.set_address(test_user_id, "Via Roma 123")
    db.set_notification_time(test_user_id, "18:30")
    
    # Recupera l'utente
    user = db.get_user(test_user_id)
    print(f"Utente: {user}")
    
    # Chiudi il connection pool
    db.close()
