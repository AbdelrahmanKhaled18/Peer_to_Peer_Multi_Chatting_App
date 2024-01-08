import time

from db import DB


# Includes database operations
def stress_register_users(user_count):
    start_time = time.time()
    db = DB()  # Instantiate DB class
    for i in range(user_count):
        username = f'test_user_{i}'
        password = f'test_password_{i}'
        db.register(username, password)  # Call register method in DB class
    total_time = time.time() - start_time
    return total_time


def stress_login_users(user_count):
    start_time = time.time()
    db = DB()  # Instantiate DB class
    for i in range(user_count):
        username = f'test_user_{i}'
        ip = '127.0.0.1'
        port = 12340 + i
        db.user_login(username, ip, port)  # Call user_login method in DB class
    total_time = time.time() - start_time
    return total_time


# Stress testing
register_users_time = stress_register_users(10000)
login_users_time = stress_login_users(10000)
# Call other stress testing methods here if uncommented and modified

# Print results
print(f"Register Users Time: {register_users_time} seconds")
print(f"Login Users Time: {login_users_time} seconds")
# Print other stress testing results if applicable
