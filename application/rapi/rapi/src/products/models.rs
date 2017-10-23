use schema::products;
use validator::Validate;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "products"]
pub struct Product {
    pub id: i32,
    #[validate(custom = "::validators::not_empty")] pub name: String,
    pub category: i32,
    pub percentage: ::BigDecimal,
}

#[derive(Insertable, Validate)]
#[table_name = "products"]
pub struct NewProduct<'a> {
    #[validate(custom = "::validators::not_empty")] pub name: &'a str,
    pub category: i32,
    pub percentage: ::BigDecimal,
}
