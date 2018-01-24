use schema::categories;
use validator::Validate;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "categories"]
pub struct Category {
    pub id: i32,
    #[validate(custom = "::validators::not_empty")]
    pub name: String,
    pub color: String,
    pub alcoholic: bool,
}

#[derive(Insertable, Validate)]
#[table_name = "categories"]
pub struct NewCategory<'a> {
    #[validate(custom = "::validators::not_empty")]
    pub name: &'a str,
}
