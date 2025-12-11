from app import db
from sqlalchemy import sql

def sort_all_kelmas(preserve_till=0):
    """This function sort all kelmas in the db\n
    preserve_till - nonnegative integer: all kelmas that has sort less than or equal preserve_till will be left untouched.
    it you want to sort all the table leave it 0 as the default\n
    it expects an active app_context()"""
    
    if not isinstance(preserve_till, int):
        raise TypeError("preserve_till should be an integer!")
    if preserve_till < 0:
        raise ValueError("preserve_till can't be negative!")

    # Note that this this statement gets started actually one after preserve till
    set_statement = "SET @i = :preserve_till;"
    update_statement = """
    UPDATE kelma SET sort = @i:=@i+1 
    WHERE sort > :preserve_till
    ORDER BY RAND();"""
    
    db.session.execute(sql.text(set_statement), {'preserve_till': preserve_till})
    db.session.execute(sql.text(update_statement), {'preserve_till': preserve_till})
    db.session.commit()