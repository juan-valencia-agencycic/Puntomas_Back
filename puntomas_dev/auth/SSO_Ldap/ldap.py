import ldap3

def authenticate_ldap(username: str, password: str) -> bool:
    server = ldap3.Server('ldap://10.31.0.4:389')
    try:
        print("Conectando al servidor LDAP...")
        conn = ldap3.Connection(server, user=username, password=password, auto_bind=True)
        print("Conexión establecida:", conn.bound)
        return conn.bound
    except Exception as e:
        print(f"LDAP error: {e}")
        return False