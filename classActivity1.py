from datetime import datetime
import json
import os


class Base:
    def __init__(self, id, created_at=None, updated_at=None):
        self.id = id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def save(self, **obj):
        self.updated_at = datetime.now()
        filename = obj.get('title') or obj.get('name')
        
        os.makedirs(f'{self.folder_type}', exist_ok=True)
        with open(f'{self.folder_type}/{filename}.json', 'w') as f:
            json.dump(obj, f, default=str)
            
    @classmethod
    def load(cls, filename):
        try: 
            with open(f'{cls.folder_type}/{filename}.json', 'r') as f:
                data = json.load(f)
                
                created_at = data.pop('created_at', None)
                updated_at = data.pop('updated_at', None)
                is_borrowed = data.pop('is_borrowed', False)
                borrowed_by = data.pop('borrowed_by', None)
                data.pop('folder_type', None)
                borrowed_books = data.pop('borrowed_books', [])
                
                obj = cls(**data)
                obj.created_at = datetime.fromisoformat(created_at)
                obj.updated_at = datetime.fromisoformat(updated_at) 
                obj.is_borrowed = is_borrowed
                obj.borrowed_by = borrowed_by
                obj.borrowed_books = borrowed_books
                
                return obj
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
        
    @classmethod
    def list_all(cls):
        try:
            files = os.listdir(f'{cls.folder_type}')
            objs = []
            for file in files:
                filename = file.replace('.json', '')
                obj = cls.load(filename)
                if obj is not None:
                    objs.append(obj)
            return objs
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

class Book(Base):
    folder_type = 'Books'
    
    def __init__(self, id, title, author, genre, year_published):
        super().__init__(id, created_at=datetime.now(), updated_at=datetime.now())
        self.title = title
        self.author = author
        self.genre = genre
        self.is_borrowed = False
        self.borrowed_by = None
        self.year_published = year_published
        

class User(Base):
    folder_type = 'Users'

    def __init__(self, id, name):
        super().__init__(id, created_at=datetime.now(), updated_at=datetime.now())
        self.name = name
        self.borrowed_books = []
        
    def borrow_book(self, book):
        if not book.is_borrowed:
            book.is_borrowed = True
            book.borrowed_by = self.name
            self.borrowed_books.append(book.title)
            print(f"{self.name} has borrowed {book.title}.")
            book.save(**book.__dict__)
        else:
            print(f"{book.title} is already borrowed.")
            
    def return_book(self, book):
        if book.title in self.borrowed_books:
            book.is_borrowed = False
            book.borrowed_by = None
            self.borrowed_books.remove(book.title)
            print(f"{self.name} has returned {book.title}.")
            book.save(**book.__dict__)
        else:
            print(f"{self.name} cannot return {book.title} because it was not borrowed by them.")
        
