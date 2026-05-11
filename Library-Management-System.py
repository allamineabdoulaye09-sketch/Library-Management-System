import json
import string


FILENAME = "libraries.json"

RED = "\033[31m" #For serious messages and errors      
YELLOW = "\033[33m" #For alerts and salts
GREEN = "\033[32m"  #for success messages
RESET = "\033[0m" #To return the color to normal after printing

# 1------------------- Presentation Layer -------------------------

def get_message():
    MESSAGES = {
    "too_long": f"{RED} Title is too long. Please keep it under 255 characters {RESET}",
    
    "title": {
        "empty": f"{RED}Title cannot be empty. Please enter a valid book title {RESET}",
        "symbol": f"{RED}Invalid title. Please enter a valid book title with letters {RESET}",
        "digit": f"{RED} Invalid title. Numbers are not allowed {RESET}",
        "book_title": f"⚠ Special characters were removed. Clean title:"
    },
    "author": {
        "empty": f"{RED} Input cannot be empty. Please enter a valid author name to proceed {RESET}",
        "symbol": f"{RED} Invalid name. Author's name cannot be only symbols {RESET}",
        "digit": f"{RED} Invalid name. Numbers are not allowed in the author's name {RESET}",
        "name_author": f"​⚠ Special characters were removed from the author's name. Clean name:"
    }
 
}
    return MESSAGES

def notify_about_trimming(user_input, message):
    if user_input:
        print(f"{YELLOW}{message}{RESET}")
               
# 2------------------- Data Lyer --------------------

def load_all_data():
    try:
        with open(FILENAME, "r") as file:
            return json.load(file)
    except (FileNotFoundError,json.decoder.JSONDecodeError):
        return {}
    except Exception as e:
        print(e)
        return {}

def save_all_data(library):
    with open(FILENAME, "w") as file:
        json.dump(library, file, indent=4)

def get_next_id(library):
    if not library:
         return "1001"
        
    return str(max(map(int, library.keys())) + 1)

# 3----------------------- Validation ----------------------

def is_empty(value):
    return not str(value).strip()


def is_too_long(name):
    return len(name) >=  255
    
def is_all_digits(raw_input):
    return raw_input.isdigit() 
  
def should_exit(user_input):
    return user_input.lower() in ["exit", "quit", "خروج"]

def id_exists(id, library):
    return id in library
      
def is_all_punctuation(text):
    return all(char in string.punctuation for char in text)

def check_error(text):
       if is_empty(text):
            return "empty"
       if is_all_punctuation(text):
            return "symbol_error"
       if is_all_digits(text):
            return "digit_error"
       if is_too_long(text):
            return "too_long"
            
       return None

def validate_text(raw_input, empty, digit, symbol):
    message = get_message()
    error = check_error(raw_input)

    if error:
        if error == "empty": return empty
        elif error == "digit_error": return digit
        elif error == "symbol_error": return symbol
        elif error == "too_long": return message["too_long"]
        
    return None
    
def validate_copies(number_copies):
    if is_empty(number_copies):
        return f" {RED} The number of copies cannot be empty. Please enter a valid number to continue {RESET}"
    
    try:
        copies = int(number_copies)

        if copies >= 1000:
            return f"{RED}Too many copies. Please enter a number less than or equal to 1000{RESET}"           
        elif copies >= 0:
            return None 
        
        return f"{RED}Invalid number. The number of copies cannot be negative{RESET}"

    except ValueError:
        return f"{RED}Invalid input. Please enter a numeric value for the number of copies {RESET}"    

def is_valid_id(library, id): 
    if is_empty(id):
        return f"{RED}Input cannot be empty. Please enter a valid book ID{RESET}"
    
    elif not id_exists(id, library):
        return f"{RED}Book not found {RESET}"

    return None

def is_valid_delete_input(user_input):
    if is_empty(user_input):
        print(f"{RED}Input cannot be empty. Please enter a valid book ID or title {RESET}")
        return False
    
    return True
    

# 3---------------------------- Logic --------------------------------

def add_books(library, book_title, author_name, number_copies):
    new_id = get_next_id(library)
    
    library[new_id] = {
    "title": book_title,
    "author": author_name, 
    "copies": number_copies,
    }
    return new_id

def delete_book(library, book):
    del library[book]
    return f"{GREEN}✅ Book deleted successfully {RESET}"
 
def update_book_filed(library, id, new_value, val):
    library[id][val] = new_value

def handle_update_logic(action, library, id, new_value):
    if get_user_confirmation("⚠ Are you sure you want to update this?"):

        action["update_func"](library, id, new_value)
        save_all_data(library)
        print(f"\n✅{GREEN} {action["success"]}{RESET}")
        print(library)

    else:
        print(f"🛑{RED} Operation cancelled by user{RESET}")

def handle_deletion_logic(library, id):
    if id: 
        if get_user_confirmation("⚠ Are you sure you want to delete this book?"):
            print(delete_book(library, id))
            save_all_data(library)
    else: 
        print(f"{RED}❌ Book not found{RESET}")

# 4---------------- Processing Layer ----------------

def normalize_whitespace(text):
    normalized_Input = " ".join(text.split())
    
    return normalized_Input, (normalized_Input != text)
 
def strip_symbols(text, important_symbol="+#"):
    all_symbols = string.punctuation

    symbols_to_remove = "".join([char for char in all_symbols if char not in important_symbol])
    clean_text = text.strip(symbols_to_remove)
    
    return clean_text, (clean_text != text)

def clean_text(text):
    clean_text, has_spaces = normalize_whitespace(text)

    if has_spaces:
        print(f"{YELLOW}⚠ Note: Extra spaces were removed for better formatting {RESET}")
    
    final_text, has_symbol = strip_symbols(clean_text)

    return final_text, (has_symbol)

def resolve_user_identifier(user_id, library):
    target_key = None
    if id_exists(user_id, library):
        target_key = user_id            
    else:
        for key , info in library.items():
            if info.get("title", "").lower() == user_id.lower():
                target_key = key
                break

    return target_key

    
def get_validated_input(prompt, validated_fun):
    while True:
        user_in = input(f"{prompt} (or type 'exit' to cancel): ")
        if should_exit(user_in):
            raise ValueError("exit_clicked")
            
        result = validated_fun(user_in)
        if result is None:
            return user_in
        
        print(result)
           
def get_update_mapping():
    MESSAGE = get_message()
    return {
        "1": {
            "prompt": "Enter new title",
            "validator": lambda text: validate_text(
                text, MESSAGE["title"]["empty"],
                MESSAGE["title"]["digit"],
                MESSAGE["title"]["symbol"]
            ),
              "update_func": lambda library, id, new_value: update_book_filed(
                  library, id, new_value, "title"
            ),          
              "trim_message": MESSAGE["title"]["book_title"],
              "success": "Title updated successfully"
              },

        "2": {
            "prompt": "Enter new author",
            "validator": lambda text: validate_text(
                text, MESSAGE ["author"]["empty"],
                    MESSAGE["author"]["digit"],
                    MESSAGE["author"]["symbol"]
            ),
            "update_func": lambda library, id, new_value: update_book_filed(
                library, id, new_value, "author"
            ),
            "trim_message": MESSAGE["author"]["name_author"],
            "success": "Author updated successfully"
            },

        "3": {
            "prompt": "Enter new number of copies",
            "validator": lambda digit: validate_copies(digit),
            "update_func": lambda library, id, new_value: update_book_filed(
                library, id, new_value, "copies"
            ),
            "success": "Copies updated successfully"
            },
    }

# 4--------------------------- UI (Input / Output) ------------------------------

def get_user_input(prompt):
    return input(prompt).strip()
    
def get_user_confirmation(prompt_message):
    answer = get_user_input(f"{YELLOW}{prompt_message} (yes/no): {RESET}").lower()
    return answer == "yes"

def handle_adding_book(library):
    print("\n--- Add Book ---\n")
    MESSAGE = get_message()
    
    title_validation = get_validated_input(
        "Enter book title",
        lambda text: validate_text(
            text, MESSAGE["title"]["empty"],
            MESSAGE["title"]["digit"],
            MESSAGE["title"]["symbol"]
            ))
    
    clean_title, found_title = clean_text(title_validation)

    author_validation = get_validated_input(
        "Enter author name",
        lambda text: validate_text(
            text, MESSAGE["author"]["empty"], 
            MESSAGE["author"]["digit"],
            MESSAGE["author"]["symbol"]
            ))
     
    clean_author, found_author = clean_text(author_validation)

    copies = int(get_validated_input(
        "Enter number of copies",
        lambda digit: validate_copies(digit)
        ))

    new_id = add_books(library, clean_title, clean_author, copies)
    save_all_data(library)
    print(f"\n{GREEN}✅ Book added successfully{RESET}")
    print(f"Book ID: {new_id}")
    print(f"Book Title: {clean_title}")
    print(f"Author Name: {clean_author}")
    print(f"Copies: {copies}")
    
    notify_about_trimming(found_title, MESSAGE["title"]["book_title"])
    notify_about_trimming(found_author, MESSAGE["author"]["name_author"])


def handle_deleting_book(library):
    print("\n---- Delete Book ----\n")
    
    if is_empty(library):
        print(f"{YELLOW}No books available to delete{RESET}")
        return
    
    user_id = get_user_input("Enter book ID or title (or type 'exit' to cancel): ")

    if is_valid_delete_input(user_id):

        id = resolve_user_identifier(user_id, library)
        handle_deletion_logic(library, id)      
     
#5 ------------------- UI (Disply Main menu) ----------------
 
def display_menu():
    print("\nChoose what you want to edit:")
    main_menu = ["Title", "Author", "Copies", "Cancel"]

    for number, menu in enumerate(main_menu, 1):
        print(f"{number}- {menu}")


def handle_edit_book(library):
    print("\n---- Edit book ----\n")
    if is_empty(library):
        print(f"{YELLOW}No books available to edit{RESET}")
        return

    id = get_validated_input("Enter book ID to edit", lambda id: is_valid_id(library, id))

    while True:
        display_menu()
        choose = get_user_input("\nChoose an option: ")

        UPDATE_ACTIONS = get_update_mapping()
 
        if choose in UPDATE_ACTIONS: 
            action = UPDATE_ACTIONS[choose]
 
            raw_input =  get_validated_input(action["prompt"], action["validator"])

            clean_val, was_trimmed = clean_text(raw_input)
            try:
                notify_about_trimming(was_trimmed, action["trim_message"])
            except KeyError:
                pass
            
            if is_all_digits(clean_val):
                clean_val = int(clean_val)

            handle_update_logic(action, library, id, clean_val)
            
        elif choose == "4":
            return
          
        else:
            pass
  


library = {"101": {"title": "c++", "author": "Robert", "copies": 5}, "102": {"title": "Python", "copies": 5}}
handle_deleting_book(library)
#print(library)
#library = {}

#handle_adding_book(library)
print(library)