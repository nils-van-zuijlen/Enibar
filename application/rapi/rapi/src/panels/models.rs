use schema::panels;
use validator::Validate;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "panels"]
pub struct Panel {
    pub id: i32,
    #[validate(custom = "::validators::not_empty")] pub name: String,
    pub hidden: bool,
}

#[derive(Insertable, Validate)]
#[table_name = "panels"]
pub struct NewPanel<'a> {
    #[validate(custom = "::validators::not_empty")] pub name: &'a str,
}
