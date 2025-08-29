from sqlalchemy import create_engine, inspect

engine = create_engine("sqlite:///attendance.db")
insp = inspect(engine)
print(insp.get_table_names())
