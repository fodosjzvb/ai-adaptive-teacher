def type_file_checking(user_file_path, expected_file_type):
    if not user_file_path.endswith(expected_file_type):
        print(f"Invalid file type. Expected {expected_file_type}")
        return False
    return True
    