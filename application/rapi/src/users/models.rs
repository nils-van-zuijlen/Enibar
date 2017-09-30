use schema::admins;
use validator::Validate;

#[derive(Insertable)]
#[table_name = "admins"]
pub struct NewUser<'a> {
    pub login: &'a str,
    pub password: &'a str,
}

#[derive(Debug, Queryable, Identifiable, AsChangeset, Validate, Model)]
#[primary_key(login)]
#[table_name="admins"]
pub struct User {
    #[validate(custom = "::validators::not_empty")]
    pub login: String,
    pub password: String,
    pub manage_notes: bool,
    pub manage_users: bool,
    pub manage_products: bool,
}
