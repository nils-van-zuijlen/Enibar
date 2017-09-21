use schema::categories;

#[derive(Debug, Queryable, AsChangeset)]
#[table_name="categories"]
pub struct Category {
    pub id: i32,
    pub name: String,
    pub color: String,
    pub alcoholic: bool,
}

#[derive(Insertable)]
#[table_name="categories"]
pub struct NewCategory<'a> {
    pub name: &'a str,
}
