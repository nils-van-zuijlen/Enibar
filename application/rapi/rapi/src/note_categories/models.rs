use schema::note_categories;
use validator::Validate;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "note_categories"]
pub struct NoteCategory {
    pub id: i32,
    #[validate(custom = "::validators::not_empty")]
    pub name: String,
    pub hidden: bool,
    pub protected: bool,
}

#[derive(Insertable, Validate)]
#[table_name = "note_categories"]
pub struct NewNoteCategory<'a> {
    #[validate(custom = "::validators::not_empty")]
    pub name: &'a str,
}

#[derive(Debug, Clone)]
pub struct NoteCategorySql;
